from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class Signal(Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


@dataclass
class Bar:
    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int


@dataclass
class Trade:
    symbol: str
    side: str
    qty: float
    price: float
    timestamp: datetime

    def to_dict(self) -> dict:
        return {
            "symbol": self.symbol,
            "side": self.side,
            "qty": self.qty,
            "price": self.price,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class Position:
    symbol: str
    qty: float
    avg_entry_price: float
    current_price: float

    @property
    def unrealized_pl(self) -> float:
        return (self.current_price - self.avg_entry_price) * self.qty

    def to_dict(self) -> dict:
        return {
            "symbol": self.symbol,
            "qty": self.qty,
            "avg_entry_price": self.avg_entry_price,
            "current_price": self.current_price,
            "unrealized_pl": self.unrealized_pl,
        }
