from collections import defaultdict, deque
from models import Bar, Signal
from strategies.base import Strategy


class SmaCrossover(Strategy):
    def __init__(self, short_window: int = 5, long_window: int = 20):
        self.short_window = short_window
        self.long_window = long_window
        self._prices: dict[str, deque] = defaultdict(
            lambda: deque(maxlen=long_window)
        )

    async def on_bar(self, symbol: str, bar: Bar) -> Signal:
        self._prices[symbol].append(bar.close)
        prices = list(self._prices[symbol])
        if len(prices) < self.long_window:
            return Signal.HOLD
        short_sma = sum(prices[-self.short_window :]) / self.short_window
        long_sma = sum(prices) / self.long_window
        if short_sma > long_sma:
            return Signal.BUY
        if short_sma < long_sma:
            return Signal.SELL
        return Signal.HOLD
