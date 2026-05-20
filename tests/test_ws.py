import pytest
import json
from unittest.mock import AsyncMock, MagicMock
from api.ws import WebSocketHub


def _mock_ws():
    ws = MagicMock()
    ws.accept = AsyncMock()
    ws.send_text = AsyncMock()
    return ws


@pytest.mark.asyncio
async def test_connect_adds_client():
    hub = WebSocketHub()
    ws = _mock_ws()
    await hub.connect(ws)
    assert len(hub._clients) == 1
    ws.accept.assert_called_once()


@pytest.mark.asyncio
async def test_disconnect_removes_client():
    hub = WebSocketHub()
    ws = _mock_ws()
    await hub.connect(ws)
    hub.disconnect(ws)
    assert len(hub._clients) == 0


@pytest.mark.asyncio
async def test_broadcast_sends_json_to_all_clients():
    hub = WebSocketHub()
    ws1, ws2 = _mock_ws(), _mock_ws()
    await hub.connect(ws1)
    await hub.connect(ws2)
    await hub.broadcast({"status": "running"})
    ws1.send_text.assert_called_once_with('{"status": "running"}')
    ws2.send_text.assert_called_once_with('{"status": "running"}')


@pytest.mark.asyncio
async def test_broadcast_removes_dead_clients():
    hub = WebSocketHub()
    ws = _mock_ws()
    ws.send_text.side_effect = RuntimeError("disconnected")
    await hub.connect(ws)
    await hub.broadcast({"status": "running"})
    assert len(hub._clients) == 0
