import pathlib
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse

from api.routes import create_router
from api.ws import WebSocketHub
from engine.engine import TradingEngine

_DASHBOARD = pathlib.Path(__file__).parent.parent / "dashboard" / "index.html"


def create_app(engine: TradingEngine, hub: WebSocketHub) -> FastAPI:
    app = FastAPI(title="Trading Bot")

    @app.get("/")
    async def dashboard():
        return FileResponse(_DASHBOARD)

    @app.websocket("/ws")
    async def ws_endpoint(ws: WebSocket):
        await hub.connect(ws)
        try:
            while True:
                await ws.receive_text()
        except WebSocketDisconnect:
            hub.disconnect(ws)

    app.include_router(create_router(engine, hub))
    return app
