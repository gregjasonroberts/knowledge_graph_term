# stock_loader.py
import yfinance as yf

class StockLoader:
    """
    Fetches historical close prices (and computes returns) for given tickers.
    Uses yfinance under the hood.
    """
    def __init__(self):
        pass

    def fetch_daily_returns(self, symbol, start="2022-01-01", end=None):
        """
        Returns a dict of {date_str: daily_return}.
        """
        ticker = yf.Ticker(symbol)
        # Get daily close prices
        hist = ticker.history(start=start, end=end, auto_adjust=True)
        # daily closing prices
        daily = hist['Close']
        # compute simple daily returns
        returns = daily.pct_change().dropna()
        # format as { 'YYYY-MM-DD': float }
        return {date.strftime("%Y-%m-%d"): float(ret) for date, ret in returns.items()}
