import html as html_lib  # BUG 5 FIX: escape usernames before rendering as HTML
import streamlit as st
from auth_helper import require_login
from database import get_all_users_net_worth
from styles import apply_theme, app_nav

require_login()

st.set_page_config(page_title="Leaderboard · MockMarket", page_icon="🏆", layout="wide")

apply_theme()

st.markdown(
    """
<style>
.lb-hero { margin-bottom: 2.4rem; }
.lb-hero-eyebrow {
    font-family: 'Geist Mono', monospace;
    font-size: 0.7rem;
    color: #555;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}
.lb-hero-title {
    font-family: 'Geist', sans-serif;
    font-size: 2rem;
    font-weight: 600;
    color: #f2f2f2;
    letter-spacing: -0.025em;
    margin: 0 0 0.4rem 0;
}
.lb-hero-sub {
    font-family: 'Geist', sans-serif;
    font-size: 0.95rem;
    color: #666;
    margin-bottom: 2rem;
}

.lb-stats {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    margin-bottom: 2.5rem;
}
.lb-stat {
    background: linear-gradient(180deg, #0a0a0a 0%, #060606 100%);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
}
.lb-stat-label {
    font-family: 'Geist Mono', monospace;
    font-size: 0.68rem;
    color: #555;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 0.7rem;
}
.lb-stat-value {
    font-family: 'Geist', sans-serif;
    font-size: 1.7rem;
    font-weight: 600;
    color: #f2f2f2;
    letter-spacing: -0.025em;
    line-height: 1;
}
.lb-stat-value.accent { color: #00C805; }

.lb-list {
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
    margin-bottom: 4rem;
}
.lb-row {
    display: grid;
    grid-template-columns: 50px 50px 1fr auto;
    align-items: center;
    gap: 1.2rem;
    background: #080808;
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 12px;
    padding: 1rem 1.4rem;
    transition: border-color 0.15s, background 0.15s, transform 0.15s;
}
.lb-row:hover {
    border-color: rgba(0,200,5,0.18);
    background: #0c0c0c;
    transform: translateX(2px);
}
.lb-row.rank-1 {
    background: linear-gradient(90deg, rgba(0,200,5,0.06) 0%, #080808 60%);
    border-color: rgba(0,200,5,0.25);
}
.lb-row.rank-2 {
    background: linear-gradient(90deg, rgba(255,255,255,0.03) 0%, #080808 60%);
    border-color: rgba(255,255,255,0.12);
}
.lb-row.rank-3 {
    background: linear-gradient(90deg, rgba(255,255,255,0.02) 0%, #080808 60%);
    border-color: rgba(255,255,255,0.08);
}

.lb-rank {
    font-family: 'Geist Mono', monospace;
    font-weight: 500;
    font-size: 0.95rem;
    color: #444;
    text-align: center;
}
.lb-row.rank-1 .lb-rank { color: #00C805; font-size: 1.4rem; font-weight: 600; }
.lb-row.rank-2 .lb-rank { color: #d0d0d0; font-size: 1.2rem; font-weight: 600; }
.lb-row.rank-3 .lb-rank { color: #b8b8b8; font-size: 1.1rem; font-weight: 600; }

.lb-avatar {
    width: 40px;
    height: 40px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'Geist', sans-serif;
    font-weight: 600;
    font-size: 0.85rem;
    color: #888;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.06);
}
.lb-row.rank-1 .lb-avatar {
    background: linear-gradient(135deg, #00C805 0%, #009804 100%);
    color: #001a01;
    border-color: rgba(0,200,5,0.3);
    box-shadow: 0 4px 14px rgba(0,200,5,0.25);
}
.lb-row.rank-2 .lb-avatar {
    background: linear-gradient(135deg, #f0f0f0 0%, #b0b0b0 100%);
    color: #0a0a0a;
}
.lb-row.rank-3 .lb-avatar {
    background: linear-gradient(135deg, #c8a070 0%, #8a6840 100%);
    color: #0a0a0a;
}

.lb-name {
    font-family: 'Geist', sans-serif;
    font-weight: 500;
    font-size: 1rem;
    color: #d8d8d8;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
.lb-row.rank-1 .lb-name,
.lb-row.rank-2 .lb-name,
.lb-row.rank-3 .lb-name { color: #f2f2f2; font-weight: 600; }

.lb-name .you-tag {
    color: #00C805;
    font-family: 'Geist Mono', monospace;
    font-size: 0.7rem;
    margin-left: 0.4rem;
    letter-spacing: 0.08em;
    background: rgba(0,200,5,0.08);
    padding: 0.18rem 0.5rem;
    border-radius: 4px;
    border: 1px solid rgba(0,200,5,0.2);
}

.lb-value {
    font-family: 'Geist', sans-serif;
    font-weight: 600;
    font-size: 1.05rem;
    color: #00C805;
    letter-spacing: -0.015em;
    text-align: right;
}
.lb-row.rank-1 .lb-value { font-size: 1.2rem; }

.lb-divider {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    color: #333;
    font-family: 'Geist Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin: 1.4rem 0 0.6rem;
}
.lb-divider::before, .lb-divider::after {
    content: '';
    flex: 1;
    height: 1px;
    background: rgba(255,255,255,0.05);
}
</style>
""",
    unsafe_allow_html=True,
)

app_nav(active="leaderboard")


def fmt_money(value: float) -> str:
    if value >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"
    if value >= 1_000:
        return f"${value / 1_000:.2f}K"
    return f"${value:.2f}"


def initials(username: str) -> str:
    parts = username.split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    return username[:2].upper()


def display_leaderboard():
    net_worth_data = get_all_users_net_worth()
    sorted_data = sorted(
        net_worth_data, key=lambda x: x["net_worth"], reverse=True
    )

    st.markdown(
        """
<div class="lb-hero">
  <div class="lb-hero-eyebrow">— Rankings</div>
  <div class="lb-hero-title">Leaderboard</div>
  <div class="lb-hero-sub">Top traders by net worth. Where do you stand?</div>
</div>
""",
        unsafe_allow_html=True,
    )

    if not sorted_data:
        st.info("No data available yet.")
        return

    total_players = len(sorted_data)
    top_nw = sorted_data[0]["net_worth"]
    avg_nw = sum(u["net_worth"] for u in sorted_data) / total_players

    st.markdown(
        f"""
<div class="lb-stats">
  <div class="lb-stat">
    <div class="lb-stat-label">Total players</div>
    <div class="lb-stat-value">{total_players}</div>
  </div>
  <div class="lb-stat">
    <div class="lb-stat-label">Top net worth</div>
    <div class="lb-stat-value accent">{fmt_money(top_nw)}</div>
  </div>
  <div class="lb-stat">
    <div class="lb-stat-label">Average</div>
    <div class="lb-stat-value">{fmt_money(avg_nw)}</div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    rows_html = []
    current_user = st.session_state.get("username", "")
    for rank, user in enumerate(sorted_data, start=1):
        rc = f"rank-{rank}" if rank <= 3 else ""
        av = html_lib.escape(initials(user["username"]))
        name = html_lib.escape(user["username"])
        if user["username"] == current_user:
            name = f'{name}<span class="you-tag">YOU</span>'
        value = fmt_money(user["net_worth"])
        rank_display = f"#{rank:02d}" if rank > 3 else f"#{rank}"

        if rank == 4:
            rows_html.append('<div class="lb-divider">Rest of the field</div>')

        rows_html.append(
            f'<div class="lb-row {rc}">'
            f'<div class="lb-rank">{rank_display}</div>'
            f'<div class="lb-avatar">{av}</div>'
            f'<div class="lb-name">{name}</div>'
            f'<div class="lb-value">{value}</div>'
            f"</div>"
        )

    st.markdown(
        f'<div class="lb-list">{"".join(rows_html)}</div>',
        unsafe_allow_html=True,
    )


display_leaderboard()
