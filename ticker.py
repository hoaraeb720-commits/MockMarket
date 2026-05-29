import pandas as pd
import streamlit as st
import yfinance as yf
import time
import random
from typing import Callable, Any


def _call_with_retry(func: Callable[[], Any], max_attempts: int = 5, base_delay: float = 1.0) -> Any:
    """Call `func` with retries on YFRateLimitError (exponential backoff + jitter).

    Falls back to checking exception class name if `yfinance.exceptions` isn't importable.
    """
    attempt = 1
    while True:
        try:
            return func()
        except Exception as e:
            # Detect YFRateLimitError if possible
            is_rate_limit = False
            try:
                import yfinance.exceptions as yf_exceptions

                is_rate_limit = isinstance(e, getattr(yf_exceptions, "YFRateLimitError", Exception))
            except Exception:
                # Fall back to name/content check
                is_rate_limit = e.__class__.__name__ == "YFRateLimitError" or "rate limit" in str(e).lower()

            if not is_rate_limit:
                # Not a rate-limit error — re-raise immediately
                raise

            if attempt >= max_attempts:
                # Exhausted retries
                raise

            delay = base_delay * (2 ** (attempt - 1)) + random.random()
            try:
                # Use streamlit spinner/warning when available to give feedback
                st.warning(f"YFinance rate limit hit — retrying in {delay:.1f}s (attempt {attempt}/{max_attempts})")
            except Exception:
                pass
            time.sleep(delay)
            attempt += 1


@st.cache_data(show_spinner=False, ttl=3600)
def load_stock_data(tickers: list, period: str) -> pd.DataFrame:
    """Load historical stock data from yfinance with retry on rate limit."""

    def _fetch():
        tickers_obj = yf.Tickers(tickers)
        data = tickers_obj.history(period=period)
        if data is None or data.empty:
            raise RuntimeError("YFinance returned no data.")
        return data["Close"]

    return _call_with_retry(_fetch)


def download_history(ticker: str, start, end) -> pd.DataFrame:
    """Download daily OHLCV with retry on rate limit.

    Returns the raw DataFrame from yf.download. May be empty if no data.
    """
    def _fetch():
        return yf.download(ticker, start=start, end=end, auto_adjust=True, progress=False)
    return _call_with_retry(_fetch)


def download_history_years(ticker: str, years: int = 2) -> pd.DataFrame:
    """Download last N years of daily OHLCV with retry on rate limit."""
    from datetime import datetime, timedelta
    end = datetime.today()
    start = end - timedelta(days=365 * years)
    return download_history(ticker, start, end)


@st.cache_data(ttl=300)
def get_current_stock_price(ticker: str) -> float:
    """Get the current stock price for a given ticker with retry on rate limit."""

    def _fetch():
        stock_data = yf.Ticker(ticker)
        hist = stock_data.history(period="1d")
        if hist is None or hist.empty:
            raise RuntimeError("YFinance returned no data.")
        return float(hist["Close"].iloc[-1])

    return _call_with_retry(_fetch)
