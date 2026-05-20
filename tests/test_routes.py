import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from api.server import create_app
from api.ws import WebSocketHub


def _make_client(state: dict):
    engine = MagicMock()
    engine.status = state["status"]
    engine.get_state.return_value = state
    hub = WebSocketHub()
    app = create_app(engine, hub)
    return TestClient(app)


_state = {
    "status": "running",
    "equity": 100000.0,
    "buying_power": 95000.0,
    "positions": [
        {"symbol": "AAPL", "qty": 2, "avg_entry_price": 150.0,
         "current_price": 155.0, "unrealized_pl": 10.0}
    ],
    "recent_trades": [
        {"symbol": "AAPL", "side": "buy", "qty": 1,
         "price": 150.0, "timestamp": "2026-05-19T10:00:00+00:00"}
    ],
    "last_signal": {},
}


def test_get_status():
    client = _make_client(_state)
    resp = client.get("/status")
    assert resp.status_code == 200
    assert resp.json()["status"] == "running"


def test_get_account():
    client = _make_client(_state)
    resp = client.get("/account")
    assert resp.status_code == 200
    data = resp.json()
    assert data["equity"] == 100000.0
    assert data["buying_power"] == 95000.0


def test_get_positions():
    client = _make_client(_state)
    resp = client.get("/positions")
    assert resp.status_code == 200
    assert resp.json()[0]["symbol"] == "AAPL"


def test_get_trades():
    client = _make_client(_state)
    resp = client.get("/trades")
    assert resp.status_code == 200
    assert resp.json()[0]["side"] == "buy"


def test_dashboard_serves_html():
    client = _make_client(_state)
    resp = client.get("/")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
