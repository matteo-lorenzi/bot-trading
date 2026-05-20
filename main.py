import asyncio
import logging
import os
import sys

import uvicorn
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)


def _validate_config():
    missing = [k for k in ("ALPACA_API_KEY", "ALPACA_SECRET_KEY") if not os.getenv(k)]
    if missing:
        sys.exit(f"ERROR: Missing required env vars: {', '.join(missing)}")


async def _run():
    from api.server import create_app
    from api.ws import WebSocketHub
    from engine.engine import TradingEngine

    hub = WebSocketHub()
    engine = TradingEngine(ws_hub=hub)
    app = create_app(engine, hub)

    server_config = uvicorn.Config(
        app, host="127.0.0.1", port=8000, log_level="info"
    )
    server = uvicorn.Server(server_config)

    await asyncio.gather(engine.start(), server.serve())


if __name__ == "__main__":
    _validate_config()
    asyncio.run(_run())
