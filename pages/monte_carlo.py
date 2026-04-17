from datetime import datetime, timedelta

import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
import altair as alt


# ============================================================================
# Configuration
# ============================================================================

st.set_page_config(
    page_title="Monte Carlo · Stock Simulator",
    page_icon="📈",
    layout="wide",
)


# ============================================================================
# Helper Functions
# ============================================================================


@st.cache_data(show_spinner=False)
def fetch_data(ticker: str, years: int = 2) -> pd.DataFrame:
    """Fetch historical stock data from Yahoo Finance."""
    end = datetime.today()
    start = end - timedelta(days=365 * years)
    df = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=True)
    if df.empty:
        return pd.DataFrame()
    df = df[["Close"]].dropna()
    df.columns = ["close"]
    return df


def compute_gbm_params(prices: pd.Series) -> tuple:
    """Estimate µ (drift) and σ (volatility) from log returns."""
    log_ret = np.log(prices / prices.shift(1)).dropna()
    mu = log_ret.mean()
    sigma = log_ret.std()
    return float(mu), float(sigma)


def run_simulation(
    last_price: float,
    mu: float,
    sigma: float,
    n_days: int,
    n_sims: int,
    seed: int = 42,
) -> np.ndarray:
    """Generate Monte Carlo simulation paths using Geometric Brownian Motion.

    Returns array of shape (n_sims, n_days+1).
    """
    rng = np.random.default_rng(seed)
    dt = 1
    paths = np.empty((n_sims, n_days + 1))
    paths[:, 0] = last_price
    shocks = rng.standard_normal((n_sims, n_days))
    drift = (mu - 0.5 * sigma**2) * dt
    diffusion = sigma * np.sqrt(dt)
    for t in range(1, n_days + 1):
        paths[:, t] = paths[:, t - 1] * np.exp(drift + diffusion * shocks[:, t - 1])
    return paths


def build_simulation_chart(
    hist: pd.DataFrame,
    paths: np.ndarray,
    ticker: str,
    n_days: int,
    percentiles: list,
    show_paths: int,
) -> alt.Chart:
    """Build Altair chart with historical price, simulated paths, and percentile bands."""

    future_dates = pd.bdate_range(start=hist.index[-1], periods=n_days + 1)

    # ── Historical price trace ────────────────────────────────────────────
    hist_df = hist.reset_index()
    hist_df.columns = ["Date", "Price"]
    hist_df["Type"] = "Historical"

    hist_chart = (
        alt.Chart(hist_df)
        .mark_line(point=False, interpolate="monotone")
        .encode(
            x=alt.X("Date:T", axis=alt.Axis(format="%b %d", labelAngle=-45)),
            y=alt.Y("Price:Q", axis=alt.Axis(format="$,.0f")),
            color=alt.value("steelblue"),
            tooltip=["Date:T", alt.Tooltip("Price:Q", format="$.2f")],
        )
        .properties(
            title=f"{ticker.upper()} · {paths.shape[0]:,} simulations · {n_days}d horizon"
        )
    )

    # ── Sample simulation paths ───────────────────────────────────────────
    n_show = min(show_paths, paths.shape[0])
    idx_show = np.linspace(0, paths.shape[0] - 1, n_show, dtype=int)

    paths_list = []
    for sim_idx in idx_show:
        for day, price in enumerate(paths[sim_idx]):
            paths_list.append(
                {
                    "Date": future_dates[day],
                    "Price": price,
                    "SimPath": sim_idx,
                    "Type": "Simulation",
                }
            )

    paths_df = pd.DataFrame(paths_list)

    paths_chart = (
        alt.Chart(paths_df)
        .mark_line(size=0.5, opacity=0.2)
        .encode(
            x=alt.X("Date:T", axis=alt.Axis(format="%b %d", labelAngle=-45)),
            y=alt.Y("Price:Q", axis=alt.Axis(format="$,.0f")),
            detail="SimPath:N",
            color=alt.value("lightblue"),
        )
    )

    # ── Percentile bands ──────────────────────────────────────────────────
    pct_colors = {
        10: "#d62728",
        25: "#ff7f0e",
        50: "#2ca02c",
        75: "#ff7f0e",
        90: "#d62728",
    }

    pct_list = []
    for p in sorted(percentiles):
        band = np.percentile(paths, p, axis=0)
        for day, price in enumerate(band):
            pct_list.append(
                {
                    "Date": future_dates[day],
                    "Price": price,
                    "Percentile": f"P{p}" if p != 50 else "Median",
                }
            )

    pct_df = pd.DataFrame(pct_list)

    pct_chart = (
        alt.Chart(pct_df)
        .mark_line(size=2, interpolate="monotone")
        .encode(
            x=alt.X("Date:T", axis=alt.Axis(format="%b %d", labelAngle=-45)),
            y=alt.Y("Price:Q", axis=alt.Axis(format="$,.0f")),
            color=alt.Color(
                "Percentile:N",
                scale=alt.Scale(
                    domain=[
                        f"P{p}" if p != 50 else "Median" for p in sorted(percentiles)
                    ],
                    range=[pct_colors.get(p, "blue") for p in sorted(percentiles)],
                ),
            ),
            strokeDash=alt.condition(
                alt.datum.Percentile == "Median",
                alt.value([]),
                alt.value([3, 3]),
            ),
            tooltip=["Date:T", alt.Tooltip("Price:Q", format="$.2f"), "Percentile"],
        )
    )

    # ── Combine all layers ────────────────────────────────────────────────
    combined = (
        alt.layer(hist_chart, paths_chart, pct_chart)
        .properties(
            height=450,
            width="container",
        )
        .interactive()
        .resolve_scale(color="independent")
    )

    return combined


def build_distribution_chart(paths: np.ndarray, percentiles: list) -> alt.Chart:
    """Build Altair histogram of final price distribution with percentile markers."""

    finals = paths[:, -1]

    # Create histogram data
    hist_data = []
    bin_edges = np.histogram_bin_edges(finals, bins=50)
    for i in range(len(bin_edges) - 1):
        mask = (finals >= bin_edges[i]) & (finals < bin_edges[i + 1])
        count = mask.sum()
        if count > 0:
            hist_data.append(
                {
                    "PriceRange": f"${bin_edges[i]:.0f}-${bin_edges[i + 1]:.0f}",
                    "Price": (bin_edges[i] + bin_edges[i + 1]) / 2,
                    "Count": count,
                }
            )

    hist_df = pd.DataFrame(hist_data)

    hist_chart = (
        alt.Chart(hist_df)
        .mark_bar(opacity=0.7, color="steelblue")
        .encode(
            x=alt.X("Price:Q", axis=alt.Axis(format="$,.0f")),
            y=alt.Y("Count:Q"),
            tooltip=["PriceRange", alt.Tooltip("Count:Q")],
        )
    )

    # Add percentile rule lines
    pct_colors_map = {10: "#d62728", 50: "#2ca02c", 90: "#d62728"}
    rule_data = []
    for p in [10, 50, 90]:
        if p in percentiles:
            val = np.percentile(finals, p)
            rule_data.append({"Percentile": f"P{p}", "Value": val})

    rule_df = pd.DataFrame(rule_data)

    rules = (
        alt.Chart(rule_df)
        .mark_rule(size=2, strokeDash=[3, 3])
        .encode(
            x="Value:Q",
            color=alt.Color(
                "Percentile:N",
                scale=alt.Scale(
                    domain=["P10", "P50", "P90"],
                    range=["#d62728", "#2ca02c", "#d62728"],
                ),
                legend=None,
            ),
        )
    )

    combined = (
        alt.layer(hist_chart, rules)
        .properties(height=250, width="container")
        .interactive()
    )

    return combined


# ============================================================================
# Main Content
# ============================================================================

st.title("Monte Carlo Simulation")
st.caption("GBM Stock Price Simulator")

st.divider()

# Parameters
st.markdown("## Parameters")

c1, c2, c3, c4 = st.columns(4)

with c1:
    ticker = (
        st.text_input("Ticker", value="AAPL", help="Any valid Yahoo Finance ticker")
        .upper()
        .strip()
    )

with c2:
    history_years = st.slider(
        "History (years)",
        1,
        5,
        2,
        help="Years of historical data for parameter estimation",
    )

with c3:
    n_simulations = st.select_slider(
        "Simulations",
        options=[100, 250, 500, 1000, 2000, 5000],
        value=500,
    )

with c4:
    n_days = st.slider(
        "Forecast horizon (days)", 30, 252, 126, help="Trading days into the future"
    )

c5, c6, c7 = st.columns(3)

with c5:
    show_paths = st.slider("Visible sample paths", 10, 300, 80)

with c6:
    pct_options = [5, 10, 25, 50, 75, 90, 95]
    percentiles = st.multiselect(
        "Percentile bands",
        options=pct_options,
        default=[10, 50, 90],
    )

with c7:
    st.write("")
    st.write("")
    run_btn = st.button("RUN SIMULATION")

st.divider()

if not run_btn:
    st.info(
        "Configure parameters above and press **RUN SIMULATION**. "
        "Paths are generated using Geometric Brownian Motion calibrated to historical log-returns."
    )
    st.stop()

# ── Fetch & validate ──────────────────────────────────────────────────────────
with st.spinner(f"Fetching {ticker}…"):
    hist = fetch_data(ticker, years=history_years)

if hist.empty:
    st.error(
        f"Could not retrieve data for **{ticker}**. Check the ticker and try again."
    )
    st.stop()

# ── Compute parameters ────────────────────────────────────────────────────────
mu, sigma = compute_gbm_params(hist["close"])
last_price = float(hist["close"].iloc[-1])
ann_ret = mu * 252
ann_vol = sigma * np.sqrt(252)

# ── Run simulation ────────────────────────────────────────────────────────────
with st.spinner("Running simulations…"):
    paths = run_simulation(last_price, mu, sigma, n_days, n_simulations)

finals = paths[:, -1]
p10, p50, p90 = np.percentile(finals, [10, 50, 90])
expected_ret = (p50 - last_price) / last_price * 100
prob_profit = (finals > last_price).mean() * 100

# ── Metrics ───────────────────────────────────────────────────────────────────
m1, m2, m3, m4, m5, m6 = st.columns(6)

m1.metric("Last Close", f"${last_price:.2f}")
m2.metric("Ann. Return (µ)", f"{ann_ret * 100:.1f}%")
m3.metric("Ann. Volatility (σ)", f"{ann_vol * 100:.1f}%")
m4.metric(f"Median ({n_days}d)", f"${p50:.2f} ({expected_ret:+.1f}%)")
m5.metric("P10 / P90", f"${p10:.2f} / ${p90:.2f}")
m6.metric("P(Profit)", f"{prob_profit:.1f}%")

st.divider()

# ── Simulation chart ──────────────────────────────────────────────────────────
if not percentiles:
    percentiles = [50]

with st.spinner("Building chart…"):
    sim_chart = build_simulation_chart(
        hist, paths, ticker, n_days, percentiles, show_paths
    )

st.altair_chart(sim_chart, width="stretch")

# ── Distribution chart ────────────────────────────────────────────────────────
with st.spinner("Building distribution chart…"):
    dist_chart = build_distribution_chart(paths, percentiles)

st.altair_chart(dist_chart, width="stretch")

# ── Footer note ───────────────────────────────────────────────────────────────
st.warning(
    "⚠ This tool is for educational and research purposes only. "
    "GBM assumes constant drift and volatility and does not account for jumps, "
    "fat tails, or regime changes. Not financial advice."
)
