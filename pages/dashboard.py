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
            default=["AAPL", "MSFT", "GOOGL", "NVDA", "AMZN", "TSLA", "META"],
        )
        time_period_selection = st.pills(
            "Select Time Period", ["1mo", "3mo", "6mo", "1y", "2y"], default="6mo"
        )

    with st.container(border=True):
        # show worst stock and best stock
        if selected_tickers:
            data = yf.download(
                tickers=selected_tickers,
                period=time_period_selection,
                interval="1d",
                group_by="ticker",
            )

            performance = {}
            for ticker in selected_tickers:
                start_price = data[ticker]["Close"].iloc[0]
                end_price = data[ticker]["Close"].iloc[-1]
                change_pct = ((end_price - start_price) / start_price) * 100
                performance[ticker] = change_pct

            best_stock = max(performance, key=performance.get)
            worst_stock = min(performance, key=performance.get)

            nested_column1, nested_column2 = st.columns(2)
            with nested_column1:
                st.metric(
                    label="Best Performing Stock",
                    value=best_stock,
                    delta=f"{performance[best_stock]:.2f}%",
                    delta_color="normal",
                )
            with nested_column2:
                st.metric(
                    label="Worst Performing Stock",
                    value=worst_stock,
                    delta=f"{performance[worst_stock]:.2f}%",
                    delta_color="inverse",
                )

with column2:
    with st.container(border=True):
        if selected_tickers:
            data = yf.download(
                tickers=selected_tickers,
                period=time_period_selection,
                interval="1d",
                group_by="ticker",
            )

            price_data = pd.DataFrame()
            for ticker in selected_tickers:
                price_data[ticker] = data[ticker]["Close"]

            # create altair line chart

            st.line_chart(
                price_data,
                width="stretch",
                x_label="Date",
                y_label="Closing Price (USD)",
            )
        else:
            st.info("Please select at least one stock ticker to display the chart.")
