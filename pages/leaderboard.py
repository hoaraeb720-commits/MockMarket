import streamlit as st
from database import get_all_users_net_worth

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Leaderboard", page_icon="🏆", layout="centered")

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500&display=swap');

/* ── Global reset ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0d0f14 !important;
    color: #e8eaf0;
}

.main .block-container {
    padding-top: 3.5rem;
    padding-bottom: 4rem;
    max-width: 780px;
}

/* ── Header ── */
.lb-header {
    text-align: center;
    margin-bottom: 3rem;
    padding: 1rem 0 0.5rem;
}

.lb-header h1 {
    font-family: 'Syne', sans-serif;
    font-size: 3.5rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    margin: 0;
    background: linear-gradient(135deg, #f5c842 0%, #f09b2f 60%, #e8774a 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.lb-header p {
    color: #6b7280;
    font-size: 0.95rem;
    font-weight: 300;
    margin: 0.6rem 0 0;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

/* ── Card ── */
.lb-card {
    display: flex;
    align-items: center;
    gap: 1.4rem;
    background: #161920;
    border: 1px solid #1e2330;
    border-radius: 16px;
    padding: 1.3rem 1.8rem;
    margin-bottom: 0.85rem;
    transition: transform 0.15s ease, border-color 0.15s ease, box-shadow 0.15s ease;
    cursor: default;
}

.lb-card:hover {
    transform: translateX(4px);
    border-color: #2e3650;
    box-shadow: 0 4px 24px rgba(0,0,0,0.35);
}

/* ── Top-3 special cards ── */
.lb-card.rank-1 { border-color: #c9a227; background: linear-gradient(135deg, #1a1710 0%, #161920 60%); }
.lb-card.rank-2 { border-color: #7a8fa6; background: linear-gradient(135deg, #111519 0%, #161920 60%); }
.lb-card.rank-3 { border-color: #7c5c3b; background: linear-gradient(135deg, #12100e 0%, #161920 60%); }

/* ── Rank badge ── */
.lb-rank {
    font-family: 'Syne', sans-serif;
    font-size: 1.1rem;
    font-weight: 800;
    min-width: 2.8rem;
    text-align: center;
    color: #3a4155;
}
.rank-1 .lb-rank { color: #f5c842; font-size: 1.7rem; }
.rank-2 .lb-rank { color: #a8bfd4; font-size: 1.55rem; }
.rank-3 .lb-rank { color: #c9835a; font-size: 1.4rem; }

/* ── Avatar ── */
.lb-avatar {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 1.05rem;
    flex-shrink: 0;
    background: #1e2330;
    color: #6b7280;
}
.rank-1 .lb-avatar { background: linear-gradient(135deg, #c9a227, #f5c842); color: #0d0f14; }
.rank-2 .lb-avatar { background: linear-gradient(135deg, #6b8090, #a8bfd4); color: #0d0f14; }
.rank-3 .lb-avatar { background: linear-gradient(135deg, #7c5c3b, #c9835a); color: #0d0f14; }

/* ── Username ── */
.lb-name {
    flex: 1;
    font-weight: 500;
    font-size: 1.1rem;
    color: #d1d5e0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.rank-1 .lb-name, .rank-2 .lb-name, .rank-3 .lb-name {
    color: #eef0f6;
    font-weight: 500;
}

/* ── Net worth ── */
.lb-value {
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 1.15rem;
    color: #4ade80;
    letter-spacing: -0.01em;
    white-space: nowrap;
}

/* ── Divider between top3 and rest ── */
.lb-divider {
    text-align: center;
    color: #2e3650;
    font-size: 0.75rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin: 1.6rem 0 1.2rem;
}

/* ── Stats row ── */
.lb-stats {
    display: flex;
    gap: 1.2rem;
    margin-bottom: 2.5rem;
}
.lb-stat {
    flex: 1;
    background: #161920;
    border: 1px solid #1e2330;
    border-radius: 14px;
    padding: 1.2rem 1.2rem;
    text-align: center;
}
.lb-stat-label {
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #4b5568;
    margin-bottom: 0.5rem;
}
.lb-stat-value {
    font-family: 'Syne', sans-serif;
    font-size: 1.5rem;
    font-weight: 700;
    color: #c9a227;
}
</style>
""", unsafe_allow_html=True)


# ── Helper ────────────────────────────────────────────────────────────────────
MEDAL = {1: "🥇", 2: "🥈", 3: "🥉"}

def fmt_money(value: float) -> str:
    """Format large numbers with K/M suffixes."""
    if value >= 1_000_000:
        return f"${value/1_000_000:.2f}M"
    if value >= 1_000:
        return f"${value/1_000:.2f}K"
    return f"${value:.2f}"

def initials(username: str) -> str:
    parts = username.split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    return username[:2].upper()

def rank_class(rank: int) -> str:
    return f"rank-{rank}" if rank <= 3 else ""


# ── Data ──────────────────────────────────────────────────────────────────────
def display_leaderboard():
    net_worth_data = get_all_users_net_worth()
    sorted_data = sorted(net_worth_data, key=lambda x: x["net_worth"], reverse=True)

    # Header
    st.markdown("""
        <div class="lb-header">
            <h1>🏆 Leaderboard</h1>
            <p>Ranked by net worth</p>
        </div>
    """, unsafe_allow_html=True)

    if not sorted_data:
        st.info("No data available yet.")
        return

    # Summary stats
    total_players = len(sorted_data)
    top_nw = sorted_data[0]["net_worth"]
    avg_nw = sum(u["net_worth"] for u in sorted_data) / total_players

    st.markdown(f"""
        <div class="lb-stats">
            <div class="lb-stat">
                <div class="lb-stat-label">Players</div>
                <div class="lb-stat-value">{total_players}</div>
            </div>
            <div class="lb-stat">
                <div class="lb-stat-label">Top Net Worth</div>
                <div class="lb-stat-value">{fmt_money(top_nw)}</div>
            </div>
            <div class="lb-stat">
                <div class="lb-stat-label">Average</div>
                <div class="lb-stat-value">{fmt_money(avg_nw)}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Rows
    for rank, user in enumerate(sorted_data, start=1):
        rc = rank_class(rank)
        badge = MEDAL.get(rank, f"#{rank}")
        av = initials(user["username"])
        name = user["username"]
        value = fmt_money(user["net_worth"])

        if rank == 4:
            st.markdown('<div class="lb-divider">─── Rest of the field ───</div>', unsafe_allow_html=True)

        st.markdown(f"""
            <div class="lb-card {rc}">
                <div class="lb-rank">{badge}</div>
                <div class="lb-avatar">{av}</div>
                <div class="lb-name">{name}</div>
                <div class="lb-value">{value}</div>
            </div>
        """, unsafe_allow_html=True)


display_leaderboard()