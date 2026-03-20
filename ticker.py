import pandas as pd
import streamlit as st
import yfinance as yf


@st.cache_resource(show_spinner=False, ttl="1h")
def load_stock_data(tickers: list, period: str) -> pd.DataFrame:
    """Load historical stock data from yfinance"""
    tickers_obj = yf.Tickers(tickers)
    data = tickers_obj.history(period=period)
    if data is None:
        raise RuntimeError("YFinance returned no data.")
    return data["Close"]


@st.cache_data(ttl=300)
def get_current_stock_price(ticker: str) -> float:
    """Get the current stock price for a given ticker"""
    stock_data = yf.Ticker(ticker)
    current_price = stock_data.history(period="1d")["Close"].iloc[-1]
    return current_price
