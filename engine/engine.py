import asyncio
import importlib
import logging
from datetime import datetime, timezone

import config
from engine.broker import AlpacaBroker
from engine.market_data import MarketDataFeed
from models import Signal, Trade
from strategies.base import Strategy

logger = logging.getLogger(__name__)


class TradingEngine:
    def __init__(self, ws_hub=None, broker=None, feed=None, strategy=None):
        self._broker = broker or AlpacaBroker()
        self._feed = feed or MarketDataFeed()
        self._strategy: Strategy = strategy or self._load_strategy()
        self._ws_hub = ws_hub
        self._running = False
        self._recent_trades: list[Trade] = []
        self._last_signal: dict = {}

    def _load_strategy(self) -> Strategy:
        module_path, class_name = config.STRATEGY_CLASS.rsplit(".", 1)
        module = importlib.import_module(module_path)
        return getattr(module, class_name)()

    @property
    def status(self) -> str:
        return "running" if self._running else "stopped"

    async def start(self):
        self._running = True
        logger.info("Engine started. Symbols: %s", config.SYMBOLS)
        while self._running:
            await self._tick()
            await asyncio.sleep(config.LOOP_INTERVAL_SECONDS)

    def stop(self):
        self._running = False

    async def _tick(self):
        for symbol in config.SYMBOLS:
            try:
                bar = self._feed.get_latest_bar(symbol)   # sync call, no await
                signal = await self._strategy.on_bar(symbol, bar)
                self._last_signal = {
                    "symbol": symbol,
                    "action": signal.value,
                    "ts": datetime.now(timezone.utc).isoformat(),
                }
                if signal == Signal.BUY:
                    trade = self._broker.submit_order(symbol, qty=1, side="buy")
                    self._recent_trades.append(trade)
                elif signal == Signal.SELL:
                    trade = self._broker.submit_order(symbol, qty=1, side="sell")
                    self._recent_trades.append(trade)
            except Exception as exc:
                logger.error("Tick error [%s]: %s", symbol, exc)

        if self._ws_hub:
            await self._ws_hub.broadcast(self.get_state())

    def get_state(self) -> dict:
        try:
            account = self._broker.get_account()
            positions = [p.to_dict() for p in self._broker.get_positions()]
        except Exception as exc:
            logger.error("State build error: %s", exc)
            account = {"equity": 0.0, "buying_power": 0.0}
            positions = []
        return {
            "status": self.status,
            "equity": account["equity"],
            "buying_power": account["buying_power"],
            "positions": positions,
            "recent_trades": [t.to_dict() for t in self._recent_trades[-20:]],
            "last_signal": self._last_signal,
        }
