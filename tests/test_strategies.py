import pytest
from datetime import datetime, timezone
from models import Bar, Signal
from strategies.sma_crossover import SmaCrossover


def _bar(symbol: str, close: float) -> Bar:
    return Bar(symbol=symbol, timestamp=datetime.now(timezone.utc),
               open=close, high=close, low=close, close=close, volume=100000)


@pytest.mark.asyncio
async def test_hold_when_insufficient_data():
    strat = SmaCrossover(short_window=3, long_window=5)
    signal = await strat.on_bar("AAPL", _bar("AAPL", 100.0))
    assert signal == Signal.HOLD


@pytest.mark.asyncio
async def test_buy_when_short_above_long():
    strat = SmaCrossover(short_window=2, long_window=4)
    # Feed 4 low prices then 2 high ones -> short SMA > long SMA
    for price in [100.0, 100.0, 100.0, 100.0]:
        await strat.on_bar("AAPL", _bar("AAPL", price))
    signal = await strat.on_bar("AAPL", _bar("AAPL", 200.0))
    assert signal == Signal.BUY


@pytest.mark.asyncio
async def test_sell_when_short_below_long():
    strat = SmaCrossover(short_window=2, long_window=4)
    # Feed 4 high prices then 2 low ones -> short SMA < long SMA
    for price in [200.0, 200.0, 200.0, 200.0]:
        await strat.on_bar("AAPL", _bar("AAPL", price))
    signal = await strat.on_bar("AAPL", _bar("AAPL", 50.0))
    assert signal == Signal.SELL


@pytest.mark.asyncio
async def test_strategies_are_per_symbol():
    strat = SmaCrossover(short_window=2, long_window=4)
    for price in [100.0, 100.0, 100.0, 100.0]:
        await strat.on_bar("AAPL", _bar("AAPL", price))
    # TSLA has no history yet -> HOLD
    signal = await strat.on_bar("TSLA", _bar("TSLA", 500.0))
    assert signal == Signal.HOLD
