from abc import ABC, abstractmethod
from models import Bar, Signal


class Strategy(ABC):
    @abstractmethod
    async def on_bar(self, symbol: str, bar: Bar) -> Signal:
        ...
