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


def get_stock_info(ticker: str) -> dict:
    """Get current stock information"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        hist = stock.history(period="1d")

        if not hist.empty:
            current_price = hist["Close"].iloc[-1]
            prev_close = hist["Open"].iloc[0] if len(hist) > 1 else current_price
            change = current_price - prev_close
            change_percent = (change / prev_close) * 100 if prev_close != 0 else 0

            return {
                "current_price": current_price,
                "change": change,
                "change_percent": change_percent,
                "volume": hist["Volume"].iloc[-1] if "Volume" in hist.columns else 0,
                "market_cap": info.get("marketCap", "N/A"),
                "company_name": info.get("longName", ticker),
                "sector": info.get("sector", "N/A"),
                "industry": info.get("industry", "N/A"),
            }
    except Exception as e:
        st.error(f"Error fetching data for {ticker}: {str(e)}")
        return None


def get_stock_price(ticker: str, period: str = "1y") -> pd.DataFrame:
    stock = yf.Ticker(ticker)
    price_df = stock.history(period=period)
    return price_df


# Check if user is logged in
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in to access this page.")
    if st.button("Go to Login"):
        st.switch_page("pages/login.py")
else:
    # Initialize portfolio if not exists
    if "portfolio" not in st.session_state:
        st.session_state.portfolio = {}
    if "cash" not in st.session_state:
        st.session_state.cash = 10000.0

    st.title(f"📈 Welcome to MockMarket, {st.session_state.username}!")

    # Main layout with columns
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Stock Analysis")

        # Search functionality
        tickers = get_ticker_list()
        search_term = st.text_input(
            "Search for a stock ticker or company name:",
            placeholder="e.g., AAPL, Apple, TSLA",
        )

        if search_term:
            # Filter tickers based on search
            filtered_tickers = [t for t in tickers if search_term.upper() in t.upper()]
            if not filtered_tickers:
                # Try to find by company name (this is a simple implementation)
                st.warning(
                    "No exact ticker matches. Try selecting from the dropdown below."
                )
            else:
                ticker_dropdown = st.selectbox(
                    "Select a ticker:", filtered_tickers, key="ticker_select"
                )
        else:
            ticker_dropdown = st.selectbox(
                "Select a ticker:", tickers[:100], key="ticker_select"
            )  # Limit to first 100 for performance

        period = st.selectbox(
            "Select time period:",
            options=[
                "1d",
                "5d",
                "1mo",
                "3mo",
                "6mo",
                "1y",
                "2y",
                "5y",
                "10y",
                "ytd",
                "max",
            ],
            index=5,  # Default to 1y
        )

        if ticker_dropdown:
            # Get stock information
            stock_info = get_stock_info(ticker_dropdown)

            if stock_info:
                # Display stock info in a nice format
                info_col1, info_col2, info_col3 = st.columns(3)

                with info_col1:
                    st.metric(
                        label="Current Price",
                        value=f"${stock_info['current_price']:.2f}",
                        delta=f"{stock_info['change']:+.2f} ({stock_info['change_percent']:+.2f}%)",
                    )

                with info_col2:
                    st.metric(label="Volume", value=f"{stock_info['volume']:,}")

                with info_col3:
                    market_cap = stock_info["market_cap"]
                    if isinstance(market_cap, (int, float)):
                        if market_cap >= 1e12:
                            market_cap_str = f"${market_cap / 1e12:.1f}T"
                        elif market_cap >= 1e9:
                            market_cap_str = f"${market_cap / 1e9:.1f}B"
                        elif market_cap >= 1e6:
                            market_cap_str = f"${market_cap / 1e6:.1f}M"
                        else:
                            market_cap_str = f"${market_cap:,.0f}"
                    else:
                        market_cap_str = "N/A"

                    st.metric(label="Market Cap", value=market_cap_str)

                # Company info
                st.write(f"**{stock_info['company_name']}**")
                st.write(
                    f"**Sector:** {stock_info['sector']} | **Industry:** {stock_info['industry']}"
                )

                # Price chart
                st.subheader(f"Price Chart for {ticker_dropdown}")
                price_data = get_stock_price(ticker_dropdown, period)
                if not price_data.empty:
                    st.line_chart(price_data["Close"])
                else:
                    st.error("No price data available for this period.")

                # Buy/Sell section
                st.subheader("Trade Stock")
                trade_col1, trade_col2 = st.columns(2)

                with trade_col1:
                    buy_quantity = st.number_input(
                        "Buy Quantity", min_value=1, value=1, key="buy_qty"
                    )
                    if st.button("Buy", key="buy_btn"):
                        total_cost = buy_quantity * stock_info["current_price"]
                        if st.session_state.cash >= total_cost:
                            st.session_state.cash -= total_cost
                            if ticker_dropdown in st.session_state.portfolio:
                                st.session_state.portfolio[ticker_dropdown][
                                    "quantity"
                                ] += buy_quantity
                                st.session_state.portfolio[ticker_dropdown][
                                    "avg_price"
                                ] = (
                                    st.session_state.portfolio[ticker_dropdown][
                                        "avg_price"
                                    ]
                                    * (
                                        st.session_state.portfolio[ticker_dropdown][
                                            "quantity"
                                        ]
                                        - buy_quantity
                                    )
                                    + stock_info["current_price"] * buy_quantity
                                ) / st.session_state.portfolio[ticker_dropdown][
                                    "quantity"
                                ]
                            else:
                                st.session_state.portfolio[ticker_dropdown] = {
                                    "quantity": buy_quantity,
                                    "avg_price": stock_info["current_price"],
                                    "company_name": stock_info["company_name"],
                                }
                            st.success(
                                f"Bought {buy_quantity} shares of {ticker_dropdown} for ${total_cost:.2f}"
                            )
                            st.rerun()
                        else:
                            st.error("Insufficient funds!")

                with trade_col2:
                    if ticker_dropdown in st.session_state.portfolio:
                        current_quantity = st.session_state.portfolio[ticker_dropdown][
                            "quantity"
                        ]
                        sell_quantity = st.number_input(
                            "Sell Quantity",
                            min_value=1,
                            max_value=current_quantity,
                            value=1,
                            key="sell_qty",
                        )
                        if st.button("Sell", key="sell_btn"):
                            total_value = sell_quantity * stock_info["current_price"]
                            st.session_state.cash += total_value
                            st.session_state.portfolio[ticker_dropdown]["quantity"] -= (
                                sell_quantity
                            )
                            if (
                                st.session_state.portfolio[ticker_dropdown]["quantity"]
                                == 0
                            ):
                                del st.session_state.portfolio[ticker_dropdown]
                            st.success(
                                f"Sold {sell_quantity} shares of {ticker_dropdown} for ${total_value:.2f}"
                            )
                            st.rerun()
                    else:
                        st.info("You don't own this stock yet.")

    with col2:
        st.subheader("💰 Portfolio")
        st.metric("Available Cash", f"${st.session_state.cash:,.2f}")

        if st.session_state.portfolio:
            total_value = 0
            st.write("**Your Holdings:**")
            for ticker, data in st.session_state.portfolio.items():
                try:
                    current_info = get_stock_info(ticker)
                    if current_info:
                        current_value = current_info["current_price"] * data["quantity"]
                        total_value += current_value
                        pnl = (
                            current_info["current_price"] - data["avg_price"]
                        ) * data["quantity"]
                        pnl_percent = (
                            pnl / (data["avg_price"] * data["quantity"])
                        ) * 100

                        st.write(
                            f"**{ticker}**: {data['quantity']} shares @ ${data['avg_price']:.2f}"
                        )
                        st.write(
                            f"Current Value: ${current_value:.2f} | P&L: ${pnl:+.2f} ({pnl_percent:+.2f}%)"
                        )
                        st.divider()
                except:
                    st.write(
                        f"**{ticker}**: {data['quantity']} shares (data unavailable)"
                    )

            total_portfolio_value = st.session_state.cash + total_value
            st.metric("Total Portfolio Value", f"${total_portfolio_value:,.2f}")
        else:
            st.info("Your portfolio is empty. Start trading to build your portfolio!")

    # Logout button
    st.divider()
    if st.button("🚪 Log Out"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.portfolio = {}
        st.session_state.cash = 10000.0
        st.success("You have been logged out.")
        st.rerun()
