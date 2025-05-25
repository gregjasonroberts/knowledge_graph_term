# stock_loader.py
import yfinance as yf

class StockLoader:
    """
    Fetches historical close prices (and computes returns) for given tickers.
    Uses yfinance under the hood.
    """
    def __init__(self):
        pass

    def fetch_monthly_returns(self, symbol, start="2022-01-01", end=None):
        """
        Returns a dict of {date_str: monthly_return}.
        """
        ticker = yf.Ticker(symbol)
        # Get daily close and resample to month-end
        hist = ticker.history(start=start, end=end, auto_adjust=True)
        # month-end prices
        monthly = hist['Close'].resample('ME').last()
        # compute simple or log returns
        returns = monthly.pct_change().dropna()
        # format as { 'YYYY-MM-DD': float }
        return {date.strftime("%Y-%m-%d"): float(ret) for date, ret in returns.items()}
