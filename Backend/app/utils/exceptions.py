class StockNotFound(Exception):
    """Custom exception for when a stock is not found."""
    def __init__(self, ticker_symbol: str):
        self.ticker_symbol = ticker_symbol
        super().__init__(f"Stock not found for ticker: {ticker_symbol}")
