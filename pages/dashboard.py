import json

import streamlit as st
import yfinance as yf
import pandas as pd
import altair as alt
from auth_helper import require_login
from database import (
    get_user_portfolio,
    get_aggregated_portfolio,
    calculate_net_worth,
)
from ticker import get_current_stock_price, load_stock_data
from constants import INITIAL_BALANCE
from trading import confirm_purchase_modal, confirm_sale_modal
from styles import apply_theme, app_nav

# Ensure user is logged in
require_login()

# ============================================================================
# Configuration
# ============================================================================

st.set_page_config(
    page_title="MockMarket Dashboard",
    page_icon=":chart_with_upwards_trend:",
    layout="wide",
)

apply_theme()

DEFAULT_STOCKS = ["AAPL", "MSFT", "GOOGL", "NVDA", "AMZN", "TSLA"]
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


@st.cache_data(ttl=300)
def load_ohlc_data(ticker: str, period: str) -> pd.DataFrame:
    """Load OHLC data for a single ticker (used for candlestick chart)"""
    df = yf.Ticker(ticker).history(period=period)
    df = df[["Open", "High", "Low", "Close"]].reset_index()
    df["Date"] = pd.to_datetime(df["Date"]).dt.tz_localize(None)
    return df


# ============================================================================
# Session State Management
# ============================================================================


def initialize_session_state():
    """Initialize session state variables"""
    if "wallet_balance" not in st.session_state:
        st.session_state.wallet_balance = INITIAL_BALANCE
    if "session_token" not in st.session_state:
        st.session_state.session_token = None
    if "chart_type" not in st.session_state:
        st.session_state.chart_type = "Line"


def initialize_tickers_input():
    """Initialize ticker selection from query params or use defaults."""
    if "tickers_input" not in st.session_state:
        raw = st.query_params.get("stocks", tickers_to_str(DEFAULT_STOCKS)).split(",")
        st.session_state.tickers_input = [t.strip().upper() for t in raw if t.strip()]


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
    """Normalize prices so each starts at 1 for comparison.

    Uses each column's first non-NaN value so recent IPOs don't blank out.
    """
    return data.apply(lambda col: col / col.dropna().iloc[0] if col.notna().any() else col)


def calculate_performance(normalized: pd.DataFrame, tickers: list) -> tuple:
    """Calculate best and worst performing stocks."""
    pairs = [(normalized[ticker].iat[-1], ticker) for ticker in tickers]
    max_pair = max(pairs, key=lambda p: p[0])
    min_pair = min(pairs, key=lambda p: p[0])
    return max_pair, min_pair


# ============================================================================
# UI Components - Header & Selection
# ============================================================================


def display_header():
    """Display dashboard header — top nav, hero stats, and logout."""
    app_nav(active="dashboard")

    username = st.session_state.get("username", "User")
    balance = st.session_state.wallet_balance
    net_worth = calculate_net_worth(username=username)
    pnl_pct = (net_worth - 10000) / 10000 * 100

    pnl_color = "accent-green" if pnl_pct >= 0 else "accent-red"
    arrow = "↑" if pnl_pct >= 0 else "↓"

    st.markdown(
        f"""
<style>
.dash-hero {{
    margin-bottom: 2.4rem;
}}
.dash-hero-eyebrow {{
    font-family: 'Geist Mono', monospace;
    font-size: 0.7rem;
    color: #555;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}}
.dash-hero-title {{
    font-family: 'Geist', sans-serif;
    font-size: 2rem;
    font-weight: 600;
    color: #f2f2f2;
    letter-spacing: -0.025em;
    line-height: 1.05;
    margin-bottom: 0.4rem;
}}
.dash-hero-sub {{
    font-family: 'Geist', sans-serif;
    font-size: 0.95rem;
    color: #666;
    margin-bottom: 2rem;
}}
.dash-stats-row {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
}}
.dash-stat {{
    background: linear-gradient(180deg, #0a0a0a 0%, #060606 100%);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
    position: relative;
    overflow: hidden;
}}
.dash-stat::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.08), transparent);
}}
.dash-stat-label {{
    font-family: 'Geist Mono', monospace;
    font-size: 0.68rem;
    color: #555;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 0.7rem;
}}
.dash-stat-value {{
    font-family: 'Geist', sans-serif;
    font-size: 1.7rem;
    font-weight: 600;
    color: #f2f2f2;
    letter-spacing: -0.025em;
    line-height: 1;
}}
.dash-stat-delta {{
    font-family: 'Geist Mono', monospace;
    font-size: 0.78rem;
    margin-top: 0.5rem;
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    padding: 0.18rem 0.5rem;
    border-radius: 5px;
}}
.dash-stat-delta.accent-green {{
    color: #00C805;
    background: rgba(0,200,5,0.08);
}}
.dash-stat-delta.accent-red {{
    color: #ff5050;
    background: rgba(255,80,80,0.08);
}}
</style>
<div class="dash-hero">
  <div class="dash-hero-eyebrow">— Welcome back, {username}</div>
  <div class="dash-hero-title">Your portfolio at a glance</div>
  <div class="dash-hero-sub">Live market data, $10,000 starting capital, zero real-world risk.</div>
  <div class="dash-stats-row">
    <div class="dash-stat">
      <div class="dash-stat-label">Wallet balance</div>
      <div class="dash-stat-value">${balance:,.2f}</div>
      <div class="dash-stat-delta accent-green" style="background:transparent;color:#555;padding:0;">Available to trade</div>
    </div>
    <div class="dash-stat">
      <div class="dash-stat-label">Net worth</div>
      <div class="dash-stat-value">${net_worth:,.2f}</div>
      <div class="dash-stat-delta {pnl_color}">{arrow} {abs(pnl_pct):.2f}%</div>
    </div>
    <div class="dash-stat">
      <div class="dash-stat-label">Total return</div>
      <div class="dash-stat-value" style="color:{'#00C805' if pnl_pct >= 0 else '#ff5050'};">${net_worth - 10000:+,.2f}</div>
      <div class="dash-stat-delta accent-green" style="background:transparent;color:#555;padding:0;">Since signup</div>
    </div>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )



def create_stock_selector(all_tickers: list) -> tuple:
    """Create and return stock ticker and time horizon selections"""
    cols = st.columns([1, 3])

    top_left_cell = cols[0].container(
        border=True, height="stretch", vertical_alignment="center"
    )

    with top_left_cell:
        tickers = st.multiselect(
            "Stock tickers",
            options=sorted(set(all_tickers) | set(st.session_state.tickers_input)),
            default=st.session_state.tickers_input,
            placeholder="Choose stocks to compare",
            accept_new_options=True,
        )

        horizon = st.pills(
            "Time horizon",
            options=list(HORIZON_MAP.keys()),
            default="6 Months",
        )

        # ── Chart type toggle ──────────────────────────────────────────
        chart_type = st.pills(
            "Chart type",
            options=["Line", "Candlestick"],
            default=st.session_state.chart_type,
            key="chart_type_pills",
        )
        if chart_type:
            st.session_state.chart_type = chart_type

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


def create_line_chart(normalized: pd.DataFrame) -> alt.Chart:
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


def create_candlestick_chart(ohlc: pd.DataFrame, ticker: str) -> alt.LayerChart:
    """Create an Altair candlestick chart for a single ticker"""
    base = alt.Chart(ohlc).encode(
        alt.X("Date:T", axis=alt.Axis(title="Date", grid=False)),
        color=alt.condition(
            "datum.Open <= datum.Close",
            alt.value("#00C805"),   # green candle
            alt.value("#FF3B30"),   # red candle
        ),
        tooltip=[
            alt.Tooltip("Date:T", title="Date"),
            alt.Tooltip("Open:Q",  title="Open",  format="$.2f"),
            alt.Tooltip("High:Q",  title="High",  format="$.2f"),
            alt.Tooltip("Low:Q",   title="Low",   format="$.2f"),
            alt.Tooltip("Close:Q", title="Close", format="$.2f"),
        ],
    )

    # High-low wick
    rule = base.mark_rule(strokeWidth=1).encode(
        alt.Y("Low:Q",  title="Price ($)", scale=alt.Scale(zero=False)),
        alt.Y2("High:Q"),
    )

    # Open-close body
    bar = base.mark_bar(width={"band": 0.6}).encode(
        alt.Y("Open:Q",  scale=alt.Scale(zero=False)),
        alt.Y2("Close:Q"),
    )

    return (
        (rule + bar)
        .properties(height=400, title=f"{ticker} — Candlestick Chart")
        .configure_axis(labelColor="#888", titleColor="#888", gridColor="#1e1e1e")
        .configure_title(color="#ccc")
        .configure_view(strokeWidth=0)
    )


def display_comparison_chart(
    right_cell,
    normalized: pd.DataFrame,
    tickers: list,
    horizon_period: str,
):
    """Display either the line chart or candlestick chart based on toggle"""
    chart_type = st.session_state.chart_type

    with right_cell:
        if chart_type == "Candlestick":
            # Candlestick only works for a single ticker — let user pick one
            if len(tickers) > 1:
                candle_ticker = st.selectbox(
                    "Select ticker for candlestick view",
                    options=tickers,
                    key="candle_ticker_select",
                )
            else:
                candle_ticker = tickers[0]

            try:
                ohlc = load_ohlc_data(candle_ticker, horizon_period)
                chart = create_candlestick_chart(ohlc, candle_ticker)
                st.altair_chart(chart, width="stretch")
            except Exception as e:
                st.error(f"Could not load candlestick data: {e}")
        else:
            chart = create_line_chart(normalized)
            st.altair_chart(chart, width="stretch")


# ============================================================================
# UI Components - Trading
# ============================================================================


def display_trading_section(tickers: list):
    """Display stock trading interface."""
    st.markdown(
        """
<style>
.trade-section { margin-top: 4rem; }
.trade-eyebrow {
    font-family: 'Geist Mono', monospace;
    font-size: 0.7rem;
    color: #555;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}
.trade-headline {
    font-family: 'Geist', sans-serif;
    font-size: 1.7rem;
    font-weight: 600;
    color: #f2f2f2;
    letter-spacing: -0.025em;
    line-height: 1.05;
    margin-bottom: 0.4rem;
}
.trade-sub {
    font-family: 'Geist', sans-serif;
    font-size: 0.95rem;
    color: #666;
    margin-bottom: 2rem;
}

/* ── Trading panels ── */
.trade-grid > div {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
}
.trade-panel {
    background: linear-gradient(180deg, #0a0a0a 0%, #060606 100%);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
    padding: 1.5rem 1.5rem 1.7rem;
    min-height: 280px;
    display: flex;
    flex-direction: column;
}
.trade-panel-head {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin-bottom: 1.4rem;
}
.trade-panel-icon {
    width: 32px;
    height: 32px;
    border-radius: 9px;
    background: rgba(0,200,5,0.08);
    border: 1px solid rgba(0,200,5,0.16);
    color: #00C805;
    display: flex;
    align-items: center;
    justify-content: center;
}
.trade-panel-icon.sell {
    background: rgba(255,80,80,0.06);
    border-color: rgba(255,80,80,0.16);
    color: #ff5050;
}
.trade-panel-icon.neutral {
    background: rgba(255,255,255,0.03);
    border-color: rgba(255,255,255,0.08);
    color: #888;
}
.trade-panel-title {
    font-family: 'Geist', sans-serif;
    font-size: 1rem;
    font-weight: 600;
    color: #f2f2f2;
    letter-spacing: -0.01em;
}

/* Empty state */
.trade-empty {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    flex: 1;
    color: #555;
    font-size: 0.85rem;
    padding: 1rem 0;
    line-height: 1.5;
}
.trade-empty-icon {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: rgba(255,255,255,0.02);
    border: 1px dashed rgba(255,255,255,0.08);
    margin-bottom: 0.8rem;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #444;
}

/* Holdings list */
.holdings-row {
    display: grid;
    grid-template-columns: 1fr auto auto;
    gap: 0.8rem;
    align-items: center;
    padding: 0.7rem 0.2rem;
    border-bottom: 1px solid rgba(255,255,255,0.04);
}
.holdings-row:last-child { border-bottom: none; }
.holdings-ticker {
    font-family: 'Geist', sans-serif;
    font-weight: 600;
    color: #f2f2f2;
    font-size: 0.9rem;
}
.holdings-qty {
    font-family: 'Geist Mono', monospace;
    font-size: 0.78rem;
    color: #888;
}
.holdings-avg {
    font-family: 'Geist', sans-serif;
    font-size: 0.88rem;
    color: #00C805;
    font-weight: 500;
    text-align: right;
}

/* Recent txns */
.txn-row {
    padding: 0.7rem 0;
    border-bottom: 1px solid rgba(255,255,255,0.04);
    display: flex;
    flex-direction: column;
    gap: 0.2rem;
}
.txn-row:last-child { border-bottom: none; }
.txn-row-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-family: 'Geist', sans-serif;
    font-size: 0.88rem;
    color: #f2f2f2;
    font-weight: 500;
}
.txn-row-bot {
    font-family: 'Geist Mono', monospace;
    font-size: 0.74rem;
    color: #555;
}
.txn-tag {
    display: inline-block;
    background: rgba(0,200,5,0.08);
    color: #00C805;
    font-family: 'Geist Mono', monospace;
    font-size: 0.65rem;
    padding: 0.12rem 0.45rem;
    border-radius: 4px;
    border: 1px solid rgba(0,200,5,0.18);
    letter-spacing: 0.04em;
}

/* Sell button override (red) */
div[data-testid="stButton"] > button.sell-btn,
div[data-testid="stButton"] > button[kind="primary"].sell-btn {
    background: linear-gradient(180deg, #ff5050 0%, #d63030 100%) !important;
    color: #fff !important;
    box-shadow: 0 8px 24px rgba(255,80,80,0.22) !important;
}
</style>
<div class="trade-section">
  <div class="trade-eyebrow">— Order management</div>
  <div class="trade-headline">Trade & manage your portfolio</div>
  <div class="trade-sub">Buy or sell positions at live market prices.</div>
</div>
""",
        unsafe_allow_html=True,
    )

    username = st.session_state.get("username")
    user_portfolio = get_user_portfolio(username)
    aggregated = get_aggregated_portfolio(username)

    # ── Trading row: Buy, Sell, Holdings, Recent ─────────────────────────
    buy_col, sell_col, hold_col, txn_col = st.columns([1, 1, 1, 1])

    panel_head = (
        '<div class="trade-panel-head">'
        '<div class="trade-panel-icon{cls}">{icon}</div>'
        '<div class="trade-panel-title">{title}</div>'
        '</div>'
    )

    # ── BUY ─────────────────────────────────────────────────────────────
    with buy_col, st.container(border=True):
        st.markdown(
            panel_head.format(
                cls="",
                title="Buy shares",
                icon='<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>',
            ),
            unsafe_allow_html=True,
        )
        if tickers:
            stock_to_buy = st.selectbox("Stock", tickers, key="buy_ticker")
            quantity_to_buy = st.number_input(
                "Quantity", min_value=1, step=1, value=1, key="buy_qty"
            )
            if st.button(
                "Buy at market", key="buy_btn", type="primary", width="stretch"
            ):
                confirm_purchase_modal(stock_to_buy, quantity_to_buy)
        else:
            st.markdown(
                '<div class="trade-empty">'
                '<div class="trade-empty-icon">'
                '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>'
                '</div>Pick stocks above<br>to start trading</div>',
                unsafe_allow_html=True,
            )

    # ── SELL ────────────────────────────────────────────────────────────
    with sell_col, st.container(border=True):
        st.markdown(
            panel_head.format(
                cls=" sell",
                title="Sell shares",
                icon='<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"/></svg>',
            ),
            unsafe_allow_html=True,
        )
        if aggregated:
            stock_to_sell = st.selectbox(
                "Stock", list(aggregated.keys()), key="sell_ticker"
            )
            max_quantity = aggregated[stock_to_sell]["quantity"]
            quantity_to_sell = st.number_input(
                f"Quantity (max {max_quantity})",
                min_value=1,
                max_value=max_quantity,
                step=1,
                value=1,
                key="sell_qty",
            )
            if st.button("Sell at market", key="sell_btn", width="stretch"):
                confirm_sale_modal(stock_to_sell, quantity_to_sell)
        else:
            st.markdown(
                '<div class="trade-empty">'
                '<div class="trade-empty-icon">'
                '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg>'
                "</div>You don't own any<br>shares to sell yet</div>",
                unsafe_allow_html=True,
            )

    # ── HOLDINGS ────────────────────────────────────────────────────────
    with hold_col, st.container(border=True):
        st.markdown(
            panel_head.format(
                cls=" neutral",
                title="Your holdings",
                icon='<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><path d="M7 14l4-4 4 3 5-6"/></svg>',
            ),
            unsafe_allow_html=True,
        )
        if aggregated:
            rows = "".join(
                f'<div class="holdings-row">'
                f'<div class="holdings-ticker">{t}</div>'
                f'<div class="holdings-qty">{info["quantity"]} sh</div>'
                f'<div class="holdings-avg">${info["avg_price"]:.2f}</div>'
                f"</div>"
                for t, info in aggregated.items()
            )
            st.markdown(rows, unsafe_allow_html=True)
        else:
            st.markdown(
                '<div class="trade-empty">'
                '<div class="trade-empty-icon">'
                '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/></svg>'
                "</div>Your portfolio<br>is empty</div>",
                unsafe_allow_html=True,
            )

    # ── RECENT TRANSACTIONS ─────────────────────────────────────────────
    with txn_col, st.container(border=True):
        st.markdown(
            panel_head.format(
                cls=" neutral",
                title="Recent activity",
                icon='<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>',
            ),
            unsafe_allow_html=True,
        )
        if user_portfolio:
            recent = sorted(
                user_portfolio, key=lambda s: s.get("bought_at", ""), reverse=True
            )[:6]

            def fmt_when(ts) -> str:
                if not ts:
                    return ""
                try:
                    dt = pd.to_datetime(ts)
                    now = pd.Timestamp.now(tz=dt.tz if dt.tz else None)
                    delta = now - dt
                    secs = int(delta.total_seconds())
                    if secs < 60:
                        return "just now"
                    if secs < 3600:
                        return f"{secs // 60}m ago"
                    if secs < 86400:
                        return f"{secs // 3600}h ago"
                    if secs < 604800:
                        return f"{secs // 86400}d ago"
                    return dt.strftime("%b %-d")
                except Exception:
                    return ""

            rows = "".join(
                f'<div class="txn-row">'
                f'<div class="txn-row-top">'
                f'<span><span class="txn-tag">BUY</span>&nbsp;&nbsp;{stock["stock_ticker"]}</span>'
                f'<span>{stock["stock_quantity"]} × ${stock["stock_price"]:.2f}</span>'
                f"</div>"
                f'<div class="txn-row-bot">{fmt_when(stock.get("bought_at"))}</div>'
                f"</div>"
                for stock in recent
            )
            st.markdown(rows, unsafe_allow_html=True)
        else:
            st.markdown(
                '<div class="trade-empty">'
                '<div class="trade-empty-icon">'
                '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>'
                "</div>No transactions<br>yet</div>",
                unsafe_allow_html=True,
            )


# ============================================================================
# Main Application
# ============================================================================


def main():
    """Main application flow"""
    initialize_session_state()
    initialize_tickers_input()

    display_header()

    all_tickers = get_ticker_list()
    tickers, horizon, cols, top_left_cell, right_cell = create_stock_selector(
        all_tickers
    )

    tickers = [t.upper() for t in tickers]
    update_query_params(tickers)

    if not tickers:
        top_left_cell.info("Pick some stocks to compare", icon=":material/info:")
        st.stop()

    try:
        data = load_stock_data(tickers, HORIZON_MAP[horizon])
    except yf.exceptions.YFRateLimitError:
        st.warning("YFinance is rate-limiting us :(\nTry again later.")
        load_stock_data.clear()
        st.stop()

    empty_columns = validate_stock_data(data)
    if empty_columns:
        st.error(f"Error loading data for the tickers: {', '.join(empty_columns)}.")
        st.stop()

    normalized = normalize_prices(data)
    max_stock, min_stock = calculate_performance(normalized, tickers)

    display_performance_metrics(cols, max_stock, min_stock)
    display_comparison_chart(right_cell, normalized, tickers, HORIZON_MAP[horizon])

    display_trading_section(tickers)


if __name__ == "__main__":
    main()