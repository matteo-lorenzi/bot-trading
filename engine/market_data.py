from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestBarRequest
import config
from models import Bar


class MarketDataFeed:
    def __init__(self):
        self._client = StockHistoricalDataClient(
            api_key=config.ALPACA_API_KEY,
            secret_key=config.ALPACA_SECRET_KEY,
            url_override=config.ALPACA_BASE_URL,
        )

    def get_latest_bar(self, symbol: str) -> Bar:
        request = StockLatestBarRequest(symbol_or_symbols=symbol)
        response = self._client.get_stock_latest_bar(request)
        b = response[symbol]
        return Bar(
            symbol=symbol,
            timestamp=b.timestamp,
            open=float(b.open),
            high=float(b.high),
            low=float(b.low),
            close=float(b.close),
            volume=int(b.volume),
        )
