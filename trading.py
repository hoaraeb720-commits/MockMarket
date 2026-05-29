"""Trading business logic — buy, sell, FIFO accounting."""

import streamlit as st
from database import (
    update_wallet_balance,
    add_stock_to_portfolio,
    get_user_portfolio,
    remove_from_portfolio,
)
from ticker import get_current_stock_price


def save_wallet_balance():
    """Save wallet balance to database."""
    username = st.session_state.get("username")
    if username:
        update_wallet_balance(username, st.session_state.wallet_balance)


def execute_stock_purchase(ticker: str, quantity: int) -> bool:
    """Execute stock purchase and update wallet balance and portfolio."""
    current_price = get_current_stock_price(ticker)
    total_cost = current_price * quantity

    if total_cost > st.session_state.wallet_balance:
        st.error("Insufficient funds to complete the purchase.")
        return False

    username = st.session_state.get("username")
    # BUG 3 FIX: Insert portfolio document FIRST, then deduct wallet.
    # If the insert fails, no money is lost.
    try:
        add_stock_to_portfolio(username, ticker, current_price, quantity)
    except Exception as e:
        st.error(f"Purchase failed: {str(e)}")
        return False

    st.session_state.wallet_balance -= total_cost
    save_wallet_balance()

    st.success(f"Purchased {quantity} shares of {ticker} for ${total_cost:,.2f}.")
    st.rerun()
    return True


def execute_stock_sale(ticker: str, quantity: int) -> bool:
    """Execute stock sale using FIFO and update wallet."""
    # BUG 1 & 2 FIX: Use calculate_fifo_sale_preview for consistent P&L,
    # and check remove_from_portfolio return value to prevent silent money creation.
    try:
        username = st.session_state.get("username")
        current_price, sale_value, cost_basis, profit_loss = (
            calculate_fifo_sale_preview(username, ticker, quantity)
        )

        st.session_state.wallet_balance += sale_value
        save_wallet_balance()
        success = remove_from_portfolio(username, ticker, quantity)

        if not success:
            # Rollback wallet
            st.session_state.wallet_balance -= sale_value
            save_wallet_balance()
            st.error("Could not complete sale: insufficient shares.")
            return False

        if profit_loss >= 0:
            st.success(
                f"Sold {quantity} shares of {ticker} for ${sale_value:,.2f}. "
                f"Profit: ${profit_loss:,.2f}"
            )
        else:
            st.error(
                f"Sold {quantity} shares of {ticker} for ${sale_value:,.2f}. "
                f"Loss: ${abs(profit_loss):,.2f}"
            )

        st.rerun()
        return True

    except Exception as e:
        st.error(f"Error executing sale: {str(e)}")
        return False


def calculate_fifo_sale_preview(username: str, ticker: str, quantity: int):
    """Preview sale P&L using FIFO accounting."""
    current_price = get_current_stock_price(ticker)
    user_portfolio = get_user_portfolio(username)
    purchases = sorted(
        [s for s in user_portfolio if s["stock_ticker"] == ticker],
        key=lambda x: x["bought_at"],
    )

    remaining = quantity
    total_cost_basis = 0
    for stock in purchases:
        if remaining <= 0:
            break
        available = stock["stock_quantity"]
        price = stock["stock_price"]
        if available <= remaining:
            total_cost_basis += available * price
            remaining -= available
        else:
            total_cost_basis += remaining * price
            remaining = 0

    total_sale_value = current_price * quantity
    profit_loss = total_sale_value - total_cost_basis
    return current_price, total_sale_value, total_cost_basis, profit_loss


@st.dialog("Confirm Purchase")
def confirm_purchase_modal(ticker: str, quantity: int):
    """Modal dialog to confirm stock purchase before executing."""
    try:
        current_price = get_current_stock_price(ticker)
        total_cost = current_price * quantity

        st.markdown(f"### Purchase Details for **{ticker}**")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Quantity", f"{quantity} shares")
            st.metric("Price per Share", f"${current_price:.2f}")
        with col2:
            st.metric("Total Cost", f"${total_cost:,.2f}")
            st.metric("Wallet Balance", f"${st.session_state.wallet_balance:,.2f}")

        st.divider()

        # BUG 4 FIX: Track whether funds are insufficient to disable the button.
        insufficient = total_cost > st.session_state.wallet_balance
        if insufficient:
            st.error("Insufficient funds for this purchase!")
        else:
            st.success(
                f"You will have ${st.session_state.wallet_balance - total_cost:,.2f} remaining after this purchase"
            )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Confirm Purchase", width="stretch", disabled=insufficient):
                execute_stock_purchase(ticker, quantity)
        with col2:
            if st.button("Cancel", width="stretch"):
                st.rerun()
    except Exception as e:
        st.error(f"Error loading price: {str(e)}")


@st.dialog("Confirm Sale")
def confirm_sale_modal(ticker: str, quantity: int):
    """Modal dialog to confirm stock sale before executing."""
    username = st.session_state.get("username")
    try:
        current_price, sale_value, cost_basis, profit_loss = (
            calculate_fifo_sale_preview(username, ticker, quantity)
        )

        st.markdown(f"### Sale Details for **{ticker}**")
        col1, col2 = st.columns(2)

        with col1:
            st.metric("Quantity", f"{quantity} shares")
            st.metric("Current Price", f"${current_price:.2f}")
            st.metric("Total Sale Value", f"${sale_value:,.2f}")

        with col2:
            st.metric("Cost Basis (FIFO)", f"${cost_basis:,.2f}")
            if profit_loss >= 0:
                st.metric("Projected Gain", f"${profit_loss:,.2f}", delta="Profit")
                st.success("You are selling at a gain.")
            else:
                st.metric("Projected Loss", f"${abs(profit_loss):,.2f}", delta="Loss")
                st.error("You are selling at a loss.")

        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Confirm Sale", width="stretch"):
                execute_stock_sale(ticker, quantity)
        with col2:
            if st.button("Cancel", width="stretch"):
                st.rerun()
    except Exception as e:
        st.error(f"Error calculating sale preview: {str(e)}")
