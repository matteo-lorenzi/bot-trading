# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run all tests
pytest -v

# Run a single test
pytest tests/test_engine.py::test_tick_submits_buy_order_on_buy_signal -v

# Run a test file
pytest tests/test_broker.py -v

# Start the bot (requires .env with Alpaca paper keys)
python main.py
```

## Architecture

Five-layer dependency graph — imports flow one direction only:

```
models.py → (no deps)
config.py → (no deps, reads env via dotenv)
engine/   → models, config, strategies/base
api/      → engine/engine (injected), models
main.py   → api, engine, config
```

**Engine loop** (`engine/engine.py`): `TradingEngine.start()` runs an asyncio while-loop. Each tick calls `asyncio.to_thread(feed.get_latest_bar, symbol)` (sync Alpaca HTTP wrapped in a thread), then `await strategy.on_bar(symbol, bar)`, then submits orders via `broker.submit_order()`. Exceptions are caught per-symbol so one bad symbol never stops the loop. After each tick, state is broadcast to all WebSocket clients via `ws_hub.broadcast()`.

**Dependency injection**: `TradingEngine.__init__` accepts `broker`, `feed`, `strategy`, and `ws_hub` as optional overrides — all default to real implementations. Tests pass mocks directly; no `@patch` needed.

**Strategy interface** (`strategies/base.py`): One abstract method — `async def on_bar(self, symbol: str, bar: Bar) -> Signal`. Add a new strategy by subclassing `Strategy`, then set `STRATEGY_CLASS=strategies.mymodule.MyClass` in `.env`.

**WebSocket hub** (`api/ws.py`): `WebSocketHub` holds a list of connected `WebSocket` clients. `broadcast()` JSON-serializes state and sends to all, removing dead clients silently. The engine holds a reference to the hub and calls `broadcast()` at the end of each tick.

**FastAPI server** (`api/server.py`): `create_app(engine, hub)` is a factory — not a module-level singleton. Tests instantiate it with mock engine/hub. The `/ws` endpoint keeps a receive loop alive so `hub.broadcast()` can push at any time.

**State serialization**: `Trade.to_dict()` and `Position.to_dict()` on models handle datetime→ISO string and include computed fields (e.g. `unrealized_pl`). `get_state()` in the engine calls these and caps `recent_trades` at the last 20.

## Tests

`tests/conftest.py` sets dummy env vars (`ALPACA_API_KEY=test_key`, etc.) before any import, so `config.py` is importable without a real `.env`. `pytest.ini` sets `asyncio_mode = auto`.

Alpaca API calls are always mocked at the client level (`TradingClient`, `StockHistoricalDataClient`) — tests never hit the network.
