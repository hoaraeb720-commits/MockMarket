import warnings

warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import holidays
import streamlit as st
from prophet import Prophet
import yfinance as yf

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Stock Forecast",
    page_icon="📈",
    layout="wide",
)

st.title("📈 Prophet Stock Forecast")
st.caption("Powered by Facebook Prophet · NYSE holidays · Volume regressor")

# ─────────────────────────────────────────────
# INPUTS — MAIN AREA
# ─────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns([2, 2, 2, 2, 1])

with c1:
    ticker = st.text_input("Ticker symbol", value="AAPL").upper().strip()
with c2:
    start_date = st.date_input("Start date", value=pd.to_datetime("2020-01-01"))
with c3:
    end_date = st.date_input("End date", value=pd.to_datetime("2025-01-01"))
with c4:
    forecast_days = st.slider("Forecast horizon (trading days)", 10, 120, 60)
with c5:
    st.write("")
    st.write("")
    run_btn = st.button("Run Forecast", use_container_width=True, type="primary")

st.divider()

# ─────────────────────────────────────────────
# DESIGN TOKENS
# ─────────────────────────────────────────────
BLUE = "#4f9cf9"
RED = "#ff6450"
GREEN = "#34d399"
PURPLE = "#a78bfa"
AMBER = "#fbbf24"
GRID = "rgba(255,255,255,0.06)"
BG = "rgba(0,0,0,0)"


def base_layout(title="", yaxis_title="", height=280):
    return dict(
        title=dict(text=title, font=dict(size=13, color="#e2e8f0"), x=0),
        height=height,
        margin=dict(l=0, r=0, t=36, b=0),
        plot_bgcolor=BG,
        paper_bgcolor=BG,
        hovermode="x unified",
        xaxis=dict(showgrid=False, tickfont=dict(color="#94a3b8"), linecolor=GRID),
        yaxis=dict(
            title=yaxis_title,
            gridcolor=GRID,
            tickfont=dict(color="#94a3b8"),
            title_font=dict(color="#94a3b8", size=11),
            zerolinecolor=GRID,
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color="#94a3b8", size=11),
        ),
        font=dict(color="#e2e8f0"),
    )


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_data(ticker, start, end):
    raw = yf.download(ticker, start=start, end=end, auto_adjust=True, progress=False)
    if raw.empty:
        return pd.DataFrame()
    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = raw.columns.get_level_values(0)
    df = raw[["Close", "Volume"]].copy().reset_index()
    df.columns = ["ds", "y", "Volume"]
    df["ds"] = pd.to_datetime(df["ds"]).dt.tz_localize(None)
    df = df.dropna()
    df["y"] = np.log(df["y"])
    df["volume"] = np.log(df["Volume"].clip(lower=1))
    return df[["ds", "y", "volume"]]


@st.cache_data(show_spinner=False)
def get_nyse_holidays(start_year, end_year):
    years = list(range(start_year, end_year + 1))
    nyse = holidays.financial_holidays("NYSE", years=years)
    records = [
        {
            "holiday": name,
            "ds": pd.Timestamp(date),
            "lower_window": -1,
            "upper_window": 1,
        }
        for date, name in nyse.items()
    ]
    return pd.DataFrame(records).sort_values("ds").reset_index(drop=True)


def fit_model(df, holiday_df):
    model = Prophet(
        holidays=holiday_df,
        seasonality_mode="multiplicative",
        changepoint_prior_scale=0.05,
        seasonality_prior_scale=10,
        holidays_prior_scale=10,
        weekly_seasonality=True,
        daily_seasonality=False,
        yearly_seasonality=True,
        interval_width=0.95,
    )
    model.add_regressor("volume", mode="additive")
    model.fit(df)
    return model


def build_future(df, periods):
    last_date = df["ds"].max()
    future_dates = pd.bdate_range(
        start=last_date + pd.Timedelta(days=1), periods=periods
    )
    future_new = pd.DataFrame({"ds": pd.to_datetime(future_dates)})
    future = pd.concat([df[["ds"]], future_new], ignore_index=True)
    rolling_vol = df["volume"].tail(30).median()
    future = future.merge(df[["ds", "volume"]], on="ds", how="left")
    future["volume"] = future["volume"].fillna(rolling_vol)
    return future


def make_forecast(model, future):
    fc = model.predict(future)
    for col in ["yhat", "yhat_lower", "yhat_upper"]:
        fc[col] = np.exp(fc[col]).clip(lower=0)
    return fc


# ─────────────────────────────────────────────
# CHART BUILDERS
# ─────────────────────────────────────────────
def plot_forecast(df, forecast):
    fut = forecast[forecast["ds"] > df["ds"].max()]
    fig = go.Figure()

    # CI ribbon
    fig.add_trace(
        go.Scatter(
            x=pd.concat([fut["ds"], fut["ds"][::-1]]),
            y=pd.concat([fut["yhat_upper"], fut["yhat_lower"][::-1]]),
            fill="toself",
            fillcolor="rgba(255,100,80,0.12)",
            line=dict(color="rgba(0,0,0,0)"),
            name="95% CI",
            hoverinfo="skip",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["ds"],
            y=np.exp(df["y"]),
            name="Actual",
            line=dict(color=BLUE, width=1.4),
            hovertemplate="%{x|%b %d %Y}  $%{y:.2f}<extra>Actual</extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=fut["ds"],
            y=fut["yhat"],
            name="Forecast",
            line=dict(color=RED, width=2, dash="dot"),
            hovertemplate="%{x|%b %d %Y}  $%{y:.2f}<extra>Forecast</extra>",
        )
    )

    layout = base_layout(yaxis_title="Price (USD)", height=420)
    layout["margin"]["t"] = 10
    fig.update_layout(**layout)
    return fig


def plot_trend(forecast, df):
    hist = forecast[forecast["ds"] <= df["ds"].max()]
    fut = forecast[forecast["ds"] > df["ds"].max()]
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=hist["ds"],
            y=np.exp(hist["trend"]),
            name="Historical",
            line=dict(color=BLUE, width=1.8),
            hovertemplate="%{x|%b %d %Y}  $%{y:.2f}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=fut["ds"],
            y=np.exp(fut["trend"]),
            name="Forecast",
            line=dict(color=RED, width=1.8, dash="dot"),
            hovertemplate="%{x|%b %d %Y}  $%{y:.2f}<extra></extra>",
        )
    )
    fig.update_layout(**base_layout("Trend", "Price (USD)"))
    return fig


def plot_weekly(forecast):
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    fc = forecast.copy()
    fc["_dow"] = fc["ds"].dt.day_name()
    weekly = fc[fc["_dow"].isin(days)].groupby("_dow")["weekly"].mean().reindex(days)
    vals = weekly.values
    colors = [GREEN if v >= 0 else RED for v in vals]

    fig = go.Figure(
        go.Bar(
            x=weekly.index,
            y=vals,
            marker=dict(color=colors, line=dict(width=0)),
            hovertemplate="%{x}: %{y:.5f}<extra></extra>",
        )
    )
    fig.update_layout(**base_layout("Weekly Seasonality", "Effect (log)"))
    fig.add_hline(y=0, line_color=GRID, line_width=1)
    return fig


def plot_yearly(forecast):
    fc = forecast.copy()
    fc["_fake"] = pd.to_datetime(
        "2024-"
        + fc["ds"].dt.month.astype(str).str.zfill(2)
        + "-"
        + fc["ds"].dt.day.astype(str).str.zfill(2),
        errors="coerce",
    )
    yr = (
        fc.dropna(subset=["_fake"])
        .groupby("_fake")["yearly"]
        .mean()
        .reset_index()
        .sort_values("_fake")
    )
    fig = go.Figure(
        go.Scatter(
            x=yr["_fake"],
            y=yr["yearly"],
            mode="lines",
            line=dict(color=PURPLE, width=2),
            fill="tozeroy",
            fillcolor="rgba(167,139,250,0.10)",
            hovertemplate="%{x|%b %d}  %{y:.5f}<extra></extra>",
        )
    )
    layout = base_layout("Yearly Seasonality", "Effect (log)")
    fig.update_layout(**layout)
    fig.update_xaxes(tickformat="%b")
    fig.add_hline(y=0, line_color=GRID, line_width=1)
    return fig


def plot_volume(forecast):
    if "volume" not in forecast.columns:
        return None
    fig = go.Figure(
        go.Scatter(
            x=forecast["ds"],
            y=forecast["volume"],
            mode="lines",
            line=dict(color=AMBER, width=1.4),
            fill="tozeroy",
            fillcolor="rgba(251,191,36,0.08)",
            hovertemplate="%{x|%b %d %Y}  %{y:.5f}<extra></extra>",
        )
    )
    fig.update_layout(**base_layout("Volume Regressor Effect", "Effect (log)"))
    fig.add_hline(y=0, line_color=GRID, line_width=1)
    return fig


def plot_holidays(forecast, holiday_df):
    """Average effect per holiday, sorted by impact."""
    known = holiday_df["holiday"].unique().tolist()
    cols = [c for c in forecast.columns if c in known]
    if not cols:
        return None

    effects = {c: forecast[c].mean() for c in cols if c in forecast.columns}
    if not effects:
        return None

    s = pd.Series(effects).sort_values()
    colors = [RED if v < 0 else GREEN for v in s.values]

    fig = go.Figure(
        go.Bar(
            x=s.values,
            y=s.index,
            orientation="h",
            marker=dict(color=colors, line=dict(width=0)),
            hovertemplate="%{y}: %{x:.5f}<extra></extra>",
        )
    )
    h = max(300, len(s) * 24 + 60)
    layout = base_layout("Holiday Effects (avg log impact)", height=h)
    layout["margin"]["l"] = 180
    layout["yaxis"]["tickfont"] = dict(color="#94a3b8", size=11)
    fig.update_layout(**layout)
    fig.add_vline(x=0, line_color=GRID, line_width=1)
    return fig


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
if run_btn:
    with st.spinner(f"Downloading {ticker}…"):
        df = load_data(ticker, str(start_date), str(end_date))

    if df.empty:
        st.error(
            f"❌ No data found for **{ticker}**. Check the ticker symbol and date range."
        )
        st.stop()

    start_year = df["ds"].dt.year.min()
    end_year = df["ds"].dt.year.max() + 2
    holiday_df = get_nyse_holidays(start_year, end_year)

    with st.spinner("Fitting Prophet model…"):
        model = fit_model(df, holiday_df)

    with st.spinner("Generating forecast…"):
        future = build_future(df, forecast_days)
        forecast = make_forecast(model, future)

    # ── Metrics ────────────────────────────────
    last_actual = np.exp(df["y"].iloc[-1])
    fut_rows = forecast[forecast["ds"] > df["ds"].max()]
    final_yhat = fut_rows.iloc[-1]["yhat"]
    pct_change = (final_yhat - last_actual) / last_actual * 100
    upper_end = fut_rows.iloc[-1]["yhat_upper"]
    lower_end = fut_rows.iloc[-1]["yhat_lower"]

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Ticker", ticker)
    m2.metric("Last Close", f"${last_actual:.2f}")
    m3.metric(f"{forecast_days}d Forecast", f"${final_yhat:.2f}", f"{pct_change:+.1f}%")
    m4.metric("95% Upper", f"${upper_end:.2f}")
    m5.metric("95% Lower", f"${lower_end:.2f}")

    st.divider()

    # ── Forecast ───────────────────────────────
    st.subheader("Forecast")
    st.plotly_chart(plot_forecast(df, forecast), use_container_width=True)

    # ── Components ─────────────────────────────
    st.subheader("Model components")

    col_a, col_b = st.columns(2)
    with col_a:
        st.plotly_chart(plot_trend(forecast, df), use_container_width=True)
    with col_b:
        st.plotly_chart(plot_weekly(forecast), use_container_width=True)

    col_c, col_d = st.columns(2)
    with col_c:
        st.plotly_chart(plot_yearly(forecast), use_container_width=True)
    with col_d:
        fig_vol = plot_volume(forecast)
        if fig_vol:
            st.plotly_chart(fig_vol, use_container_width=True)

    fig_hol = plot_holidays(forecast, holiday_df)
    if fig_hol:
        st.plotly_chart(fig_hol, use_container_width=True)

    # ── Table ──────────────────────────────────
    st.subheader("Forecast table")
    table = fut_rows[["ds", "yhat", "yhat_lower", "yhat_upper"]].copy()
    table.columns = ["Date", "Forecast ($)", "Lower ($)", "Upper ($)"]
    table["Date"] = table["Date"].dt.strftime("%Y-%m-%d")
    for c in ["Forecast ($)", "Lower ($)", "Upper ($)"]:
        table[c] = table[c].map("${:.2f}".format)
    st.dataframe(table, use_container_width=True, hide_index=True)

else:
    st.info("👆 Set your parameters above and click **Run Forecast**.")
