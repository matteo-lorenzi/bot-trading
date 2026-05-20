# tests/test_market_data.py
import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
from models import Bar
from engine.market_data import MarketDataFeed


def _make_feed(mock_client):
    with patch("engine.market_data.StockHistoricalDataClient", return_value=mock_client):
        return MarketDataFeed()


def test_get_latest_bar_returns_bar():
    mock_client = MagicMock()
    mock_bar = MagicMock(
        timestamp=datetime(2026, 5, 19, 14, 30, tzinfo=timezone.utc),
        open=149.0,
        high=151.0,
        low=148.0,
        close=150.0,
        volume=1000000,
    )
    mock_client.get_stock_latest_bar.return_value = {"AAPL": mock_bar}
    feed = _make_feed(mock_client)
    bar = feed.get_latest_bar("AAPL")
    assert isinstance(bar, Bar)
    assert bar.symbol == "AAPL"
    assert bar.close == 150.0
    assert bar.volume == 1000000


def test_get_latest_bar_passes_correct_symbol():
    mock_client = MagicMock()
    mock_bar = MagicMock(
        timestamp=datetime.now(timezone.utc),
        open=800.0, high=810.0, low=795.0, close=805.0, volume=500000,
    )
    mock_client.get_stock_latest_bar.return_value = {"TSLA": mock_bar}
    feed = _make_feed(mock_client)
    bar = feed.get_latest_bar("TSLA")
    assert bar.symbol == "TSLA"
