from datetime import datetime, timezone
from models import Bar, Signal, Trade, Position


def _now():
    return datetime.now(timezone.utc)


def test_signal_values():
    assert Signal.BUY.value == "BUY"
    assert Signal.SELL.value == "SELL"
    assert Signal.HOLD.value == "HOLD"


def test_bar_fields():
    bar = Bar(symbol="AAPL", timestamp=_now(),
              open=100.0, high=105.0, low=99.0, close=102.0, volume=500000)
    assert bar.symbol == "AAPL"
    assert bar.close == 102.0


def test_position_unrealized_pl_long():
    pos = Position(symbol="AAPL", qty=10, avg_entry_price=100.0, current_price=110.0)
    assert pos.unrealized_pl == 100.0


def test_position_unrealized_pl_negative():
    pos = Position(symbol="AAPL", qty=5, avg_entry_price=200.0, current_price=190.0)
    assert pos.unrealized_pl == -50.0


def test_trade_to_dict_contains_iso_timestamp():
    t = Trade(symbol="AAPL", side="buy", qty=1, price=150.0, timestamp=_now())
    d = t.to_dict()
    assert d["symbol"] == "AAPL"
    assert "T" in d["timestamp"]  # ISO 8601 contains "T"


def test_position_to_dict_includes_unrealized_pl():
    pos = Position(symbol="TSLA", qty=2, avg_entry_price=200.0, current_price=210.0)
    d = pos.to_dict()
    assert d["unrealized_pl"] == 20.0
