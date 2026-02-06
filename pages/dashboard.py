import json
import streamlit as st
import yfinance as yf
import pandas as pd


st.set_page_config(layout="wide")


def get_ticker_list() -> list:
    with open("stocks.json", "r") as f:
        data = json.load(f)

    tickers = [item["symbol"] for item in data["data"]["rows"]]
    return tickers


st.title("Dashboard")

column1, column2 = st.columns([1, 2])
tickers = get_ticker_list()

with column1:
    with st.container(border=True):
        selected_tickers = st.multiselect(
            "Select multiple stock tickers for comparison",
            tickers,
            default=["AAPL", "MSFT"],
        )
        time_period_selection = st.pills(
            "Select Time Period", ["1mo", "3mo", "6mo", "1y", "2y"], default="1mo"
        )

with column2:
    with st.container(border=True):
        if selected_tickers:
            data = yf.download(
                tickers=selected_tickers,
                period=time_period_selection,
                interval="1d",
                group_by="ticker",
                auto_adjust=True,
                threads=True,
            )

            price_data = pd.DataFrame()
            for ticker in selected_tickers:
                price_data[ticker] = data[ticker]["Close"]

            st.line_chart(price_data)
        else:
            st.info("Please select at least one stock ticker to display the chart.")
