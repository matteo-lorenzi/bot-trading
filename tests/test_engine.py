import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from models import Bar, Signal, Trade, Position
from engine.engine import TradingEngine


def _bar(symbol="AAPL", close=150.0):
    return Bar(symbol=symbol, timestamp=datetime.now(timezone.utc),
               open=close, high=close, low=close, close=close, volume=100000)


def _make_engine(signal=Signal.HOLD, submit_raises=False):
    broker = MagicMock()
    broker.get_account.return_value = {"equity": 100000.0, "buying_power": 95000.0}
    broker.get_positions.return_value = []
    broker.submit_order.return_value = Trade(
        symbol="AAPL", side="buy", qty=1, price=150.0,
        timestamp=datetime.now(timezone.utc)
    )
    if submit_raises:
        broker.submit_order.side_effect = RuntimeError("order rejected")

    feed = MagicMock()
    feed.get_latest_bar.return_value = _bar()  # sync, no AsyncMock

    strategy = MagicMock()
    strategy.on_bar = AsyncMock(return_value=signal)

    engine = TradingEngine(broker=broker, feed=feed, strategy=strategy)
    return engine, broker, feed, strategy


@pytest.mark.asyncio
async def test_tick_calls_strategy_on_bar():
    engine, broker, feed, strategy = _make_engine(Signal.HOLD)
    await engine._tick()
    strategy.on_bar.assert_called_once()


@pytest.mark.asyncio
async def test_tick_submits_buy_order_on_buy_signal():
    engine, broker, _, _ = _make_engine(Signal.BUY)
    await engine._tick()
    broker.submit_order.assert_called_once_with("AAPL", qty=1, side="buy")


@pytest.mark.asyncio
async def test_tick_submits_sell_order_on_sell_signal():
    engine, broker, _, _ = _make_engine(Signal.SELL)
    await engine._tick()
    broker.submit_order.assert_called_once_with("AAPL", qty=1, side="sell")


@pytest.mark.asyncio
async def test_tick_no_order_on_hold_signal():
    engine, broker, _, _ = _make_engine(Signal.HOLD)
    await engine._tick()
    broker.submit_order.assert_not_called()


@pytest.mark.asyncio
async def test_tick_continues_on_broker_error():
    engine, broker, _, _ = _make_engine(Signal.BUY, submit_raises=True)
    await engine._tick()  # must not raise


@pytest.mark.asyncio
async def test_get_state_returns_expected_keys():
    engine, _, _, _ = _make_engine()
    state = engine.get_state()
    assert "status" in state
    assert "equity" in state
    assert "positions" in state
    assert "recent_trades" in state


def test_status_stopped_before_start():
    engine, _, _, _ = _make_engine()
    assert engine.status == "stopped"
