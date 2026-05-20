# Bot Trading

Paper trading bot for US equities using the Alpaca API. Continuous asyncio loop, pluggable strategy interface, real-time web dashboard.

> **Paper trading only** — no real money involved. Uses Alpaca's sandbox environment.

## Features

- Pluggable strategy interface — swap strategies by changing one line in `.env`
- Real-time dashboard via WebSocket (no page refresh needed)
- Async engine with per-symbol error isolation
- FastAPI REST endpoints for account, positions, and trade history

## Quick Start

**1. Install dependencies**

```bash
pip install -r requirements.txt
```

**2. Configure**

```bash
cp .env.example .env
```

Edit `.env` and set your [Alpaca paper trading](https://app.alpaca.markets/paper-trading/overview) keys:

```
ALPACA_API_KEY=your_paper_api_key
ALPACA_SECRET_KEY=your_paper_secret_key
```

**3. Run**

```bash
python main.py
```

Open `http://127.0.0.1:8000` to see the dashboard.

## Configuration

All settings in `.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `ALPACA_API_KEY` | — | Alpaca paper API key (required) |
| `ALPACA_SECRET_KEY` | — | Alpaca paper secret key (required) |
| `ALPACA_BASE_URL` | `https://paper-api.alpaca.markets` | Alpaca API base URL |
| `SYMBOLS` | `AAPL,TSLA` | Comma-separated symbols to trade |
| `LOOP_INTERVAL_SECONDS` | `60` | Seconds between each trading tick |
| `STRATEGY_CLASS` | `strategies.sma_crossover.SmaCrossover` | Dotted path to strategy class |

## Writing a Strategy

Create a file in `strategies/` and implement the `Strategy` ABC:

```python
from models import Bar, Signal
from strategies.base import Strategy

class MyStrategy(Strategy):
    async def on_bar(self, symbol: str, bar: Bar) -> Signal:
        # Your logic here
        return Signal.HOLD  # BUY | SELL | HOLD
```

Set `STRATEGY_CLASS=strategies.my_strategy.MyStrategy` in `.env`.

The included `SmaCrossover` strategy generates BUY/SELL signals based on a short vs. long simple moving average crossover.

## Project Structure

```
├── main.py                  # Entry point
├── config.py                # Env var loading
├── models.py                # Bar, Signal, Trade, Position
├── engine/
│   ├── engine.py            # Main asyncio trading loop
│   ├── broker.py            # Alpaca order/position wrapper
│   └── market_data.py       # Alpaca price feed
├── strategies/
│   ├── base.py              # Strategy abstract base class
│   └── sma_crossover.py     # SMA crossover example
├── api/
│   ├── server.py            # FastAPI app factory
│   ├── routes.py            # REST endpoints
│   └── ws.py                # WebSocket hub
└── dashboard/
    └── index.html           # Single-page dashboard
```

## REST API

| Endpoint | Description |
|----------|-------------|
| `GET /` | Dashboard |
| `GET /status` | Bot running state |
| `GET /account` | Equity and buying power |
| `GET /positions` | Open positions |
| `GET /trades` | Recent trade history |
| `WS /ws` | Real-time state stream |

## Tests

```bash
pytest -v
```

32 tests covering models, strategies, broker, market data, engine, WebSocket hub, and API routes.
