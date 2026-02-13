# -*- coding: utf-8 -*-
import json

import streamlit as st
import yfinance as yf
import pandas as pd
import altair as alt
from session_manager import logout_session
from database import update_wallet_balance, add_stock_to_portfolio

# ============================================================================
# Configuration
# ============================================================================

st.set_page_config(
    page_title="MockMarket Dashboard",
    page_icon=":chart_with_upwards_trend:",
    layout="wide",
)

DEFAULT_STOCKS = ["AAPL", "MSFT", "GOOGL", "NVDA", "AMZN", "TSLA", "META"]
HORIZON_MAP = {
    "1 Month": "1mo",
    "3 Months": "3mo",
    "6 Months": "6mo",
    "1 Year": "1y",
    "2 Years": "2y",
    "5 Years": "5y",
    "10 Years": "10y",
    "Max": "max",
}


# ============================================================================
# Data Loading & Utilities
# ============================================================================


def get_ticker_list() -> list:
    """Load all available tickers from stocks.json"""
    with open("stocks.json", "r") as f:
        data = json.load(f)
    tickers = [item["symbol"] for item in data["data"]["rows"]]
    return sorted(tickers)


def tickers_to_str(tickers: list) -> str:
    """Convert ticker list to comma-separated string"""
    return ",".join(tickers)


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


# ============================================================================
# Session State Management
# ============================================================================


def initialize_session_state():
    """Initialize session state variables"""
    if "wallet_balance" not in st.session_state:
        st.session_state.wallet_balance = 10000
    if "session_token" not in st.session_state:
        st.session_state.session_token = None


def save_wallet_balance():
    """Save wallet balance to database"""
    username = st.session_state.get("username")
    if username:
        update_wallet_balance(username, st.session_state.wallet_balance)


def initialize_tickers_input():
    """Initialize ticker selection from query params or use defaults"""
    if "tickers_input" not in st.session_state:
        st.session_state.tickers_input = st.query_params.get(
            "stocks", tickers_to_str(DEFAULT_STOCKS)
        ).split(",")


def update_query_params(tickers: list):
    """Update URL query parameters with selected tickers"""
    if tickers:
        st.query_params["stocks"] = tickers_to_str(tickers)
    else:
        st.query_params.pop("stocks", None)


# ============================================================================
# Data Processing
# ============================================================================


def validate_stock_data(data: pd.DataFrame) -> list:
    """Validate data and return list of invalid tickers"""
    return data.columns[data.isna().all()].tolist()


def normalize_prices(data: pd.DataFrame) -> pd.DataFrame:
    """Normalize prices so they start at 1 for comparison"""
    return data.div(data.iloc[0])


def calculate_performance(normalized: pd.DataFrame, tickers: list) -> tuple:
    """Calculate best and worst performing stocks"""
    latest_norm_values = {normalized[ticker].iat[-1]: ticker for ticker in tickers}
    return max(latest_norm_values.items()), min(latest_norm_values.items())


# ============================================================================
# UI Components - Header & Selection
# ============================================================================


def display_header():
    """Display dashboard header with welcome message and wallet balance"""
    username = st.session_state.get("username", "User")
    balance = st.session_state.wallet_balance

    # Create header with logout button
    col1, col2 = st.columns([0.85, 0.15])

    with col1:
        st.markdown(
            f"""# :material/query_stats: Stock Comparison Dashboard

Welcome, **{username}**! Compare stocks and manage your trading portfolio."""
        )

    with col2:
        if st.button("Logout", use_container_width=True):
            logout_session(st.session_state.session_token)
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.session_token = None
            st.query_params.pop("session_token", None)
            st.rerun()

    st.write(f"**Wallet Balance:** ${balance:,.2f}")
    ""  # Add spacing


def create_stock_selector(all_tickers: list) -> tuple:
    """Create and return stock ticker and time horizon selections"""
    cols = st.columns([1, 3])

    top_left_cell = cols[0].container(
        border=True, height="stretch", vertical_alignment="center"
    )

    with top_left_cell:
        tickers = st.multiselect(
            "Stock tickers",
            options=set(all_tickers) | set(st.session_state.tickers_input),
            default=st.session_state.tickers_input,
            placeholder="Choose stocks to compare",
            accept_new_options=True,
        )

        horizon = st.pills(
            "Time horizon",
            options=list(HORIZON_MAP.keys()),
            default="6 Months",
        )

    right_cell = cols[1].container(
        border=True, height="stretch", vertical_alignment="center"
    )

    return (tickers, horizon, cols, top_left_cell, right_cell)


# ============================================================================
# UI Components - Charts & Metrics
# ============================================================================


def display_performance_metrics(cols: list, max_stock: tuple, min_stock: tuple):
    """Display best and worst performing stock metrics"""
    bottom_left_cell = cols[0].container(
        border=True, height="stretch", vertical_alignment="center"
    )

    with bottom_left_cell:
        metrics_cols = st.columns(2)
        max_value, max_ticker = max_stock
        min_value, min_ticker = min_stock

        metrics_cols[0].metric(
            "Best stock",
            max_ticker,
            delta=f"{round(max_value * 100 - 100)}%",
            width="content",
        )
        metrics_cols[1].metric(
            "Worst stock",
            min_ticker,
            delta=f"{round(min_value * 100 - 100)}%",
            width="content",
        )


def create_price_chart(normalized: pd.DataFrame) -> alt.Chart:
    """Create an Altair line chart for normalized stock prices"""
    chart_data = normalized.reset_index().melt(
        id_vars=["Date"], var_name="Stock", value_name="Normalized price"
    )

    return (
        alt.Chart(chart_data)
        .mark_line()
        .encode(
            alt.X("Date:T"),
            alt.Y("Normalized price:Q").scale(zero=False),
            alt.Color("Stock:N"),
        )
        .properties(height=400)
    )


def display_comparison_chart(right_cell, normalized: pd.DataFrame):
    """Display the stock price comparison chart"""
    with right_cell:
        chart = create_price_chart(normalized)
        st.altair_chart(chart)


# ============================================================================
# UI Components - Trading


@st.dialog("Confirm Purchase")
def confirm_purchase_modal(ticker: str, quantity: int):
    """Modal dialog to confirm stock purchase before executing"""
    try:
        current_price = get_current_stock_price(ticker)
        total_cost = current_price * quantity

        # Display purchase details
        st.markdown(f"### Purchase Details for **{ticker}**")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Quantity", f"{quantity} shares")
            st.metric("Price per Share", f"${current_price:.2f}")
        with col2:
            st.metric("Total Cost", f"${total_cost:,.2f}")
            st.metric("Wallet Balance", f"${st.session_state.wallet_balance:,.2f}")

        st.divider()

        # Warning if insufficient funds
        if total_cost > st.session_state.wallet_balance:
            st.error("❌ Insufficient funds for this purchase!")
        else:
            st.success(
                f"✅ You will have ${st.session_state.wallet_balance - total_cost:,.2f} remaining after this purchase"
            )

        # Action buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Confirm Purchase", use_container_width=True):
                execute_stock_purchase(ticker, quantity)
        with col2:
            if st.button("❌ Cancel", use_container_width=True):
                st.rerun()
    except Exception as e:
        st.error(f"Error loading price: {str(e)}")


def execute_stock_purchase(ticker: str, quantity: int) -> bool:
    """Execute stock purchase and update wallet balance and portfolio"""
    stock_data = yf.Ticker(ticker)
    current_price = stock_data.history(period="1d")["Close"].iloc[-1]
    total_cost = current_price * quantity

    if total_cost > st.session_state.wallet_balance:
        st.error("Insufficient funds to complete the purchase.")
        return False
    else:
        # Update wallet balance
        st.session_state.wallet_balance -= total_cost
        save_wallet_balance()

        # Add stock to portfolio
        username = st.session_state.get("username")
        add_stock_to_portfolio(username, ticker, current_price, quantity)

        st.success(f"Purchased {quantity} shares of {ticker} for ${total_cost:,.2f}.")
        st.rerun()
        return True


def display_trading_section(tickers: list):
    """Display stock trading interface"""
    st.markdown(
        "## :material/trending_up: Trading\n\nBuy and manage your stock portfolio."
    )

    trading_col1, trading_col2 = st.columns([1, 2])

    with trading_col1:
        with st.container(border=True):
            st.subheader("Buy Stocks")
            if tickers:
                stock_to_buy = st.selectbox("Select Stock to Buy", tickers)
                quantity_to_buy = st.number_input(
                    "Enter Quantity to Buy", min_value=1, step=1, value=1
                )
                if st.button("Buy", use_container_width=True):
                    confirm_purchase_modal(stock_to_buy, quantity_to_buy)
            else:
                st.info("Select stocks above to buy")


# ============================================================================
# Main Application
# ============================================================================


def main():
    """Main application flow"""
    # Initialize
    initialize_session_state()
    initialize_tickers_input()

    # Display header
    display_header()
    ""

    # Get stock selections
    all_tickers = get_ticker_list()
    tickers, horizon, cols, top_left_cell, right_cell = create_stock_selector(
        all_tickers
    )

    # Normalize tickers
    tickers = [t.upper() for t in tickers]
    update_query_params(tickers)

    # Validate selection
    if not tickers:
        top_left_cell.info("Pick some stocks to compare", icon=":material/info:")
        st.stop()

    # Load and validate data
    try:
        data = load_stock_data(tickers, HORIZON_MAP[horizon])
    except yf.exceptions.YFRateLimitError as e:
        st.warning("YFinance is rate-limiting us :(\nTry again later.")
        load_stock_data.clear()
        st.stop()

    # Check for errors
    empty_columns = validate_stock_data(data)
    if empty_columns:
        st.error(f"Error loading data for the tickers: {', '.join(empty_columns)}.")
        st.stop()

    # Process data
    normalized = normalize_prices(data)
    max_stock, min_stock = calculate_performance(normalized, tickers)

    # Display comparison section
    display_performance_metrics(cols, max_stock, min_stock)
    display_comparison_chart(right_cell, normalized)

    # Display trading section
    ""
    ""
    display_trading_section(tickers)


if __name__ == "__main__":
    main()
