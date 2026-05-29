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

/* ── Podium for top 3 ── */
.lb-podium {
    display: grid;
    grid-template-columns: 1fr 1.2fr 1fr;
    gap: 1rem;
    align-items: end;
    margin-bottom: 2rem;
}
.lb-podium-card {
    background: linear-gradient(180deg, #0a0a0a 0%, #060606 100%);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px;
    padding: 1.6rem 1.4rem 1.8rem;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.lb-podium-card.first {
    border-color: rgba(0,200,5,0.3);
    background:
      radial-gradient(ellipse 80% 60% at 50% 0%, rgba(0,200,5,0.12), transparent 70%),
      linear-gradient(180deg, #0a0a0a 0%, #060606 100%);
    padding-bottom: 2.4rem;
    transform: translateY(-12px);
}
.lb-podium-card.second {
    border-color: rgba(255,255,255,0.14);
}
.lb-podium-card.third {
    border-color: rgba(200,160,112,0.25);
}
.lb-podium-rank {
    font-family: 'Geist Mono', monospace;
    font-size: 0.72rem;
    color: #555;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 0.7rem;
}
.lb-podium-card.first .lb-podium-rank { color: #00C805; }
.lb-podium-medal {
    font-size: 1.6rem;
    margin-bottom: 0.6rem;
}
.lb-podium-avatar {
    width: 60px;
    height: 60px;
    border-radius: 50%;
    margin: 0 auto 0.9rem;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'Geist', sans-serif;
    font-weight: 600;
    font-size: 1.2rem;
}
.lb-podium-card.first .lb-podium-avatar {
    background: linear-gradient(135deg, #00C805 0%, #009804 100%);
    color: #001a01;
    box-shadow: 0 6px 20px rgba(0,200,5,0.3);
    width: 72px;
    height: 72px;
    font-size: 1.4rem;
}
.lb-podium-card.second .lb-podium-avatar {
    background: linear-gradient(135deg, #f0f0f0 0%, #a0a0a0 100%);
    color: #0a0a0a;
}
.lb-podium-card.third .lb-podium-avatar {
    background: linear-gradient(135deg, #c8a070 0%, #8a6840 100%);
    color: #0a0a0a;
}
.lb-podium-name {
    font-family: 'Geist', sans-serif;
    font-weight: 600;
    font-size: 1.05rem;
    color: #f2f2f2;
    margin-bottom: 0.4rem;
    letter-spacing: -0.01em;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
.lb-podium-card.first .lb-podium-name { font-size: 1.15rem; }
.lb-podium-value {
    font-family: 'Geist', sans-serif;
    font-weight: 600;
    font-size: 1.3rem;
    color: #00C805;
    letter-spacing: -0.02em;
    line-height: 1;
}
.lb-podium-card.first .lb-podium-value { font-size: 1.6rem; }
.lb-podium-delta {
    font-family: 'Geist Mono', monospace;
    font-size: 0.78rem;
    margin-top: 0.5rem;
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    padding: 0.18rem 0.55rem;
    border-radius: 5px;
}
.lb-podium-delta.up {
    color: #00C805;
    background: rgba(0,200,5,0.08);
}
.lb-podium-delta.down {
    color: #ff5050;
    background: rgba(255,80,80,0.08);
}
.lb-podium-delta.flat {
    color: #666;
    background: rgba(255,255,255,0.03);
}

/* ── List ── */
.lb-list {
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
    margin-bottom: 4rem;
}
.lb-list-header {
    display: grid;
    grid-template-columns: 60px 50px 1fr auto 120px;
    gap: 1.2rem;
    padding: 0 1.4rem 0.7rem;
    font-family: 'Geist Mono', monospace;
    font-size: 0.66rem;
    color: #444;
    letter-spacing: 0.12em;
    text-transform: uppercase;
}
.lb-list-header > div:last-child { text-align: right; }
.lb-list-header > div:nth-child(4) { text-align: right; }
.lb-row {
    display: grid;
    grid-template-columns: 60px 50px 1fr auto 120px;
    align-items: center;
    gap: 1.2rem;
    background: #080808;
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 12px;
    padding: 0.95rem 1.4rem;
    transition: border-color 0.15s, background 0.15s, transform 0.15s;
}
.lb-row:hover {
    border-color: rgba(0,200,5,0.18);
    background: #0c0c0c;
    transform: translateX(2px);
}
.lb-row.is-you {
    background: linear-gradient(90deg, rgba(0,200,5,0.05) 0%, #0a0a0a 50%);
    border-color: rgba(0,200,5,0.25);
}
.lb-rank {
    font-family: 'Geist Mono', monospace;
    font-weight: 500;
    font-size: 0.92rem;
    color: #555;
    text-align: left;
}
.lb-avatar {
    width: 38px;
    height: 38px;
    border-radius: 9px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'Geist', sans-serif;
    font-weight: 600;
    font-size: 0.82rem;
    color: #888;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.06);
}
.lb-row.is-you .lb-avatar {
    background: linear-gradient(135deg, #00C805 0%, #009804 100%);
    color: #001a01;
}
.lb-name {
    font-family: 'Geist', sans-serif;
    font-weight: 500;
    font-size: 0.98rem;
    color: #d8d8d8;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
.lb-row.is-you .lb-name { color: #f2f2f2; font-weight: 600; }
.lb-name .you-tag {
    color: #00C805;
    font-family: 'Geist Mono', monospace;
    font-size: 0.62rem;
    margin-left: 0.5rem;
    letter-spacing: 0.08em;
    background: rgba(0,200,5,0.08);
    padding: 0.15rem 0.4rem;
    border-radius: 4px;
    border: 1px solid rgba(0,200,5,0.2);
    vertical-align: 1px;
}
.lb-value {
    font-family: 'Geist', sans-serif;
    font-weight: 600;
    font-size: 1rem;
    color: #f2f2f2;
    letter-spacing: -0.015em;
    text-align: right;
}
.lb-delta {
    font-family: 'Geist Mono', monospace;
    font-size: 0.78rem;
    display: inline-flex;
    align-items: center;
    justify-content: flex-end;
    gap: 0.3rem;
    padding: 0.2rem 0.55rem;
    border-radius: 5px;
    justify-self: end;
    min-width: 80px;
}
.lb-delta.up { color: #00C805; background: rgba(0,200,5,0.08); }
.lb-delta.down { color: #ff5050; background: rgba(255,80,80,0.08); }
.lb-delta.flat { color: #666; background: rgba(255,255,255,0.03); }
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
    s = username[:2].upper()
    return s if len(s) == 2 else (s + s)  # repeat single char to fill avatar


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

    current_user = st.session_state.get("username", "")

    def delta(nw: float) -> tuple[str, str]:
        pct = (nw - 10000) / 10000 * 100
        if pct > 0.005:
            return ("up", f"↑ {pct:.2f}%")
        if pct < -0.005:
            return ("down", f"↓ {abs(pct):.2f}%")
        return ("flat", "—")

    # ── Podium for top 3 ─────────────────────────────────────────────
    podium_order = [1, 0, 2]  # 2nd, 1st, 3rd visually
    podium_cards = []
    for visual_idx, data_idx in enumerate(podium_order):
        if data_idx >= len(sorted_data):
            podium_cards.append('<div class="lb-podium-card" style="opacity:0.3;"></div>')
            continue
        user = sorted_data[data_idx]
        actual_rank = data_idx + 1
        position_class = ["first", "second", "third"][data_idx] if data_idx <= 2 else ""
        medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(actual_rank, "")
        av = html_lib.escape(initials(user["username"]))
        name = html_lib.escape(user["username"])
        if user["username"] == current_user:
            name += '<span class="you-tag">YOU</span>'
        value = fmt_money(user["net_worth"])
        d_cls, d_label = delta(user["net_worth"])
        podium_cards.append(
            f'<div class="lb-podium-card {position_class}">'
            f'<div class="lb-podium-rank">#{actual_rank} · {medal}</div>'
            f'<div class="lb-podium-avatar">{av}</div>'
            f'<div class="lb-podium-name">{name}</div>'
            f'<div class="lb-podium-value">{value}</div>'
            f'<div class="lb-podium-delta {d_cls}">{d_label}</div>'
            f"</div>"
        )

    st.markdown(
        f'<div class="lb-podium">{"".join(podium_cards)}</div>',
        unsafe_allow_html=True,
    )

    # ── Full rankings table ──────────────────────────────────────────
    rows_html = [
        '<div class="lb-list-header">'
        '<div>Rank</div><div></div><div>Trader</div>'
        '<div>Net worth</div><div>Return</div></div>'
    ]
    for rank, user in enumerate(sorted_data, start=1):
        you = user["username"] == current_user
        you_cls = " is-you" if you else ""
        av = html_lib.escape(initials(user["username"]))
        name = html_lib.escape(user["username"])
        if you:
            name += '<span class="you-tag">YOU</span>'
        value = fmt_money(user["net_worth"])
        d_cls, d_label = delta(user["net_worth"])
        rows_html.append(
            f'<div class="lb-row{you_cls}">'
            f'<div class="lb-rank">#{rank:02d}</div>'
            f'<div class="lb-avatar">{av}</div>'
            f'<div class="lb-name">{name}</div>'
            f'<div class="lb-value">{value}</div>'
            f'<div class="lb-delta {d_cls}">{d_label}</div>'
            f"</div>"
        )

    st.markdown(
        f'<div class="lb-list">{"".join(rows_html)}</div>',
        unsafe_allow_html=True,
    )


display_leaderboard()
