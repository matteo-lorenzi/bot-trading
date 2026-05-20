from datetime import datetime, timezone
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
import config
from models import Position, Trade


class AlpacaBroker:
    def __init__(self):
        self._client = TradingClient(
            api_key=config.ALPACA_API_KEY,
            secret_key=config.ALPACA_SECRET_KEY,
            paper=True,
        )

    def get_account(self) -> dict:
        acct = self._client.get_account()
        return {
            "equity": float(acct.equity),
            "buying_power": float(acct.buying_power),
        }

    def get_positions(self) -> list[Position]:
        return [
            Position(
                symbol=p.symbol,
                qty=float(p.qty),
                avg_entry_price=float(p.avg_entry_price),
                current_price=float(p.current_price),
            )
            for p in self._client.get_all_positions()
        ]

    def submit_order(self, symbol: str, qty: float, side: str) -> Trade:
        request = MarketOrderRequest(
            symbol=symbol,
            qty=qty,
            side=OrderSide.BUY if side == "buy" else OrderSide.SELL,
            time_in_force=TimeInForce.DAY,
        )
        order = self._client.submit_order(request)
        if order.filled_avg_price is None:
            raise RuntimeError(f"Order for {symbol} did not fill: status={order.status}")
        return Trade(
            symbol=symbol,
            side=side,
            qty=qty,
            price=float(order.filled_avg_price),
            timestamp=datetime.now(timezone.utc),
        )
