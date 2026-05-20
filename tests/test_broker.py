# tests/test_broker.py
import pytest
from unittest.mock import MagicMock, patch
from models import Position, Trade
from engine.broker import AlpacaBroker


def _make_broker(mock_client):
    with patch("engine.broker.TradingClient", return_value=mock_client):
        return AlpacaBroker()


def test_get_account_returns_equity_and_buying_power():
    mock_client = MagicMock()
    mock_client.get_account.return_value = MagicMock(
        equity="100000.00", buying_power="95000.00"
    )
    broker = _make_broker(mock_client)
    result = broker.get_account()
    assert result == {"equity": 100000.0, "buying_power": 95000.0}


def test_get_positions_returns_position_list():
    mock_client = MagicMock()
    mock_client.get_all_positions.return_value = [
        MagicMock(
            symbol="AAPL", qty="2", avg_entry_price="150.00", current_price="155.00"
        )
    ]
    broker = _make_broker(mock_client)
    positions = broker.get_positions()
    assert len(positions) == 1
    assert positions[0].symbol == "AAPL"
    assert positions[0].unrealized_pl == pytest.approx(10.0)


def test_submit_order_returns_trade():
    mock_client = MagicMock()
    mock_client.submit_order.return_value = MagicMock(
        filled_avg_price="152.50"
    )
    broker = _make_broker(mock_client)
    trade = broker.submit_order("AAPL", qty=1, side="buy")
    assert trade.symbol == "AAPL"
    assert trade.side == "buy"
    assert trade.price == 152.50
