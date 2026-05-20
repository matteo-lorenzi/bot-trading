import os
from dotenv import load_dotenv

load_dotenv()

ALPACA_API_KEY: str = os.getenv("ALPACA_API_KEY", "")
ALPACA_SECRET_KEY: str = os.getenv("ALPACA_SECRET_KEY", "")
ALPACA_BASE_URL: str = os.getenv(
    "ALPACA_BASE_URL", "https://paper-api.alpaca.markets"
)
SYMBOLS: list[str] = os.getenv("SYMBOLS", "AAPL,TSLA").split(",")
LOOP_INTERVAL_SECONDS: int = int(os.getenv("LOOP_INTERVAL_SECONDS", "60"))
STRATEGY_CLASS: str = os.getenv(
    "STRATEGY_CLASS", "strategies.sma_crossover.SmaCrossover"
)
