import os

os.environ.setdefault("ALPACA_API_KEY", "test_key")
os.environ.setdefault("ALPACA_SECRET_KEY", "test_secret")
os.environ.setdefault("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")
os.environ.setdefault("SYMBOLS", "AAPL")
os.environ.setdefault("LOOP_INTERVAL_SECONDS", "1")
os.environ.setdefault("STRATEGY_CLASS", "strategies.sma_crossover.SmaCrossover")
