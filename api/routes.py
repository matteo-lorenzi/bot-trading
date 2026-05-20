from fastapi import APIRouter
from api.ws import WebSocketHub
from engine.engine import TradingEngine


def create_router(engine: TradingEngine, hub: WebSocketHub) -> APIRouter:
    router = APIRouter()

    @router.get("/status")
    async def get_status():
        return {"status": engine.status}

    @router.get("/account")
    async def get_account():
        state = engine.get_state()
        return {"equity": state["equity"], "buying_power": state["buying_power"]}

    @router.get("/positions")
    async def get_positions():
        return engine.get_state()["positions"]

    @router.get("/trades")
    async def get_trades():
        return engine.get_state()["recent_trades"]

    return router
