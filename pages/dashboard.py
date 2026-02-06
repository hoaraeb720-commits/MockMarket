import json
import streamlit as st
import yfinance as yf
import pandas as pd


st.set_page_config(layout="wide")

st.session_state.wallet_balance = st.session_state.get("wallet_balance", 10000)


def get_ticker_list() -> list:
    with open("stocks.json", "r") as f:
        data = json.load(f)

    tickers = [item["symbol"] for item in data["data"]["rows"]]
    return tickers


st.title("Dashboard")
st.subheader(f"Welcome, {st.session_state.username}!")
st.write(f"Your wallet balance: **${st.session_state.wallet_balance:,.2f}**")
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
    with st.container(border=True):
        # buy stocks and quantity
        st.subheader("Buy Stocks")
        stock_to_buy = st.selectbox("Select Stock to Buy", selected_tickers)
        quantity_to_buy = st.number_input(
            "Enter Quantity to Buy", min_value=1, step=1, value=1
        )
        if st.button("Buy"):
            stock_data = yf.Ticker(stock_to_buy)
            current_price = stock_data.history(period="1d")["Close"].iloc[-1]
            total_cost = current_price * quantity_to_buy

            if total_cost > st.session_state.wallet_balance:
                st.error("Insufficient funds to complete the purchase.")
            else:
                st.session_state.wallet_balance -= total_cost
                st.success(
                    f"Purchased {quantity_to_buy} shares of {stock_to_buy} for ${total_cost:,.2f}."
                )
            st.rerun()
        
        

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
