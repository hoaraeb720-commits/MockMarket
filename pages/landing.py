import streamlit as st

st.set_page_config(
    page_title="MockMarket — Trade Smarter",
    page_icon="📈",
    layout="wide",
)

if st.session_state.get("logged_in"):
    st.switch_page("pages/dashboard.py")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Geist:wght@300;400;500;600;700;800&family=Geist+Mono:wght@400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"], .stApp {
    font-family: 'Geist', sans-serif !important;
    background-color: #050505 !important;
    color: #f2f2f2;
    margin: 0;
    padding: 0;
}

#MainMenu, footer, header,
[data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="stStatusWidget"] { display: none !important; }
section[data-testid="stSidebar"] { display: none !important; }

section[data-testid="stMain"] .block-container,
.main .block-container {
    padding: 0 !important;
    max-width: 100% !important;
}
section[data-testid="stMain"] > div { padding: 0 !important; }
[data-testid="stAppViewBlockContainer"] { padding: 0 !important; max-width: 100% !important; }
[data-testid="stVerticalBlock"] { gap: 0 !important; }

/* ─────────────────────────────────────────────────────
   HERO
   ───────────────────────────────────────────────────── */
.hero {
    min-height: 100vh;
    width: 100%;
    display: flex;
    flex-direction: column;
    position: relative;
    overflow: hidden;
    background:
        radial-gradient(ellipse 60% 50% at 50% 30%, rgba(0,200,5,0.08), transparent 70%),
        radial-gradient(ellipse 80% 50% at 50% 100%, rgba(0,200,5,0.04), transparent 70%),
        #050505;
}

/* grid background */
.hero::before {
    content: '';
    position: absolute;
    inset: 0;
    background-image:
        linear-gradient(rgba(255,255,255,0.015) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.015) 1px, transparent 1px);
    background-size: 60px 60px;
    mask-image: radial-gradient(ellipse 70% 60% at 50% 50%, black, transparent 80%);
    -webkit-mask-image: radial-gradient(ellipse 70% 60% at 50% 50%, black, transparent 80%);
    pointer-events: none;
}

.hero-nav {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1.8rem 2.5rem;
    position: relative;
    z-index: 2;
}
.hero-logo {
    display: flex;
    align-items: center;
    gap: 10px;
}
.hero-logo-mark {
    width: 28px;
    height: 28px;
    border-radius: 7px;
    background: linear-gradient(135deg, #00C805 0%, #009804 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 14px rgba(0,200,5,0.35), inset 0 1px 0 rgba(255,255,255,0.18);
}
.hero-logo-text {
    font-family: 'Geist', sans-serif;
    font-size: 1rem;
    font-weight: 600;
    color: #f2f2f2;
    letter-spacing: -0.01em;
}
.hero-nav-link, .hero-nav-link:visited, .hero-nav-link:link {
    color: #888 !important;
    font-size: 0.9rem;
    font-weight: 500;
    text-decoration: none !important;
    transition: color 0.15s;
}
.hero-nav-link:hover { color: #f2f2f2 !important; text-decoration: none !important; }

.hero-body {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 2rem 1.5rem 6rem;
    position: relative;
    z-index: 2;
}

.hero-tag {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    color: #b0b0b0;
    font-size: 0.78rem;
    font-weight: 500;
    letter-spacing: 0.04em;
    margin-bottom: 2.2rem;
    padding: 0.4rem 0.9rem 0.4rem 0.6rem;
    border: 1px solid rgba(255,255,255,0.08);
    background: rgba(255,255,255,0.02);
    border-radius: 100px;
    backdrop-filter: blur(8px);
}
.hero-tag-dot {
    width: 6px;
    height: 6px;
    background: #00C805;
    border-radius: 50%;
    box-shadow: 0 0 10px #00C805, 0 0 4px #00C805;
    animation: pulse 2s ease-in-out infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.6; transform: scale(0.9); }
}

.hero-headline {
    font-family: 'Geist', sans-serif !important;
    font-size: clamp(3.2rem, 7.5vw, 6.4rem) !important;
    font-weight: 600 !important;
    letter-spacing: -0.045em !important;
    line-height: 0.96 !important;
    color: #f5f5f5 !important;
    margin: 0 auto 1.6rem !important;
    padding: 0 !important;
    max-width: 16ch !important;
    background: linear-gradient(180deg, #ffffff 0%, #b8b8b8 100%);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero-headline .accent {
    background: linear-gradient(180deg, #00ff09 0%, #00a004 100%);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-sub {
    font-size: 1.15rem;
    font-weight: 300;
    color: #888;
    max-width: 580px !important;
    line-height: 1.55;
    margin: 0 auto 2.6rem !important;
    letter-spacing: -0.005em;
}

.hero-ctas {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.8rem;
    flex-wrap: wrap;
    margin-bottom: 5rem;
}
.btn-primary, .btn-primary:visited, .btn-primary:link {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: linear-gradient(180deg, #00d806 0%, #00b805 100%) !important;
    color: #001a01 !important;
    padding: 0.85rem 1.5rem;
    border-radius: 9px;
    font-family: 'Geist', sans-serif;
    font-size: 0.95rem;
    font-weight: 600;
    text-decoration: none !important;
    letter-spacing: -0.005em;
    transition: transform 0.15s, box-shadow 0.15s, filter 0.15s;
    border: none;
    cursor: pointer;
    box-shadow:
        0 1px 0 rgba(255,255,255,0.25) inset,
        0 -1px 0 rgba(0,0,0,0.15) inset,
        0 8px 24px rgba(0,200,5,0.22);
}
.btn-primary:hover {
    filter: brightness(1.08);
    transform: translateY(-1px);
    box-shadow:
        0 1px 0 rgba(255,255,255,0.3) inset,
        0 -1px 0 rgba(0,0,0,0.15) inset,
        0 12px 32px rgba(0,200,5,0.32);
    color: #001a01 !important;
    text-decoration: none !important;
}
.btn-primary svg { transition: transform 0.2s; }
.btn-primary:hover svg { transform: translateX(3px); }

.btn-secondary, .btn-secondary:visited, .btn-secondary:link {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: rgba(255,255,255,0.03) !important;
    color: #d5d5d5 !important;
    padding: 0.85rem 1.4rem;
    border-radius: 9px;
    font-family: 'Geist', sans-serif;
    font-size: 0.95rem;
    font-weight: 500;
    text-decoration: none !important;
    border: 1px solid rgba(255,255,255,0.08);
    transition: all 0.15s;
    cursor: pointer;
    backdrop-filter: blur(8px);
}
.btn-secondary:hover {
    border-color: rgba(255,255,255,0.18) !important;
    color: #ffffff !important;
    background: rgba(255,255,255,0.06) !important;
    text-decoration: none !important;
}

/* hero footer stats */
.hero-stats {
    display: flex;
    justify-content: center;
    gap: 2.5rem;
    flex-wrap: wrap;
    padding: 1.8rem 0 0;
    border-top: 1px solid rgba(255,255,255,0.05);
    width: 100%;
    max-width: 720px;
    margin: 0 auto;
}
.hero-stat {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.25rem;
}
.hero-stat-num {
    font-family: 'Geist', sans-serif;
    font-size: 1.15rem;
    font-weight: 600;
    color: #f2f2f2;
    line-height: 1;
    letter-spacing: -0.02em;
}
.hero-stat-num .accent { color: #00C805; }
.hero-stat-label {
    font-family: 'Geist Mono', monospace;
    font-size: 0.68rem;
    color: #555;
    font-weight: 400;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}

/* ─────────────────────────────────────────────────────
   FEATURES
   ───────────────────────────────────────────────────── */
.features-section {
    width: 100%;
    padding: 8rem 1.5rem 8rem;
    background: #050505;
    border-top: 1px solid rgba(255,255,255,0.04);
}
.features-inner {
    max-width: 1120px;
    margin: 0 auto;
    text-align: center;
}
.features-eyebrow {
    display: inline-block;
    color: #00C805;
    font-family: 'Geist Mono', monospace;
    font-size: 0.72rem;
    font-weight: 500;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin: 0 auto 1.3rem;
}
.features-section-title {
    font-family: 'Geist', sans-serif !important;
    font-size: clamp(2.2rem, 4.2vw, 3.4rem) !important;
    font-weight: 600 !important;
    letter-spacing: -0.035em !important;
    line-height: 1.05 !important;
    color: #f5f5f5 !important;
    margin: 0 auto 1.1rem !important;
    max-width: 22ch !important;
    background: linear-gradient(180deg, #ffffff 0%, #c0c0c0 100%);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
}
.features-section-title .accent {
    background: linear-gradient(180deg, #00ff09 0%, #00a004 100%);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
}
.features-section-sub {
    font-size: 1.05rem;
    color: #777;
    font-weight: 300;
    max-width: 540px !important;
    margin: 0 auto 4.5rem !important;
    line-height: 1.55;
}
.features-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1px;
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px;
    overflow: hidden;
}
.feature-card {
    background: #080808;
    padding: 2.5rem 2.2rem;
    transition: background 0.25s;
    position: relative;
    text-align: left;
}
.feature-card:hover { background: #0c0c0c; }
.feature-card-num {
    position: absolute;
    top: 1.6rem;
    right: 1.8rem;
    font-family: 'Geist Mono', monospace;
    font-size: 0.7rem;
    color: #2a2a2a;
    font-weight: 500;
    letter-spacing: 0.06em;
}
.feature-card-icon {
    width: 42px;
    height: 42px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(180deg, rgba(0,200,5,0.12) 0%, rgba(0,200,5,0.06) 100%);
    border: 1px solid rgba(0,200,5,0.18);
    color: #00C805;
    border-radius: 10px;
    margin-bottom: 1.6rem;
}
.feature-card-title {
    font-family: 'Geist', sans-serif;
    font-size: 1.1rem;
    font-weight: 600;
    color: #f2f2f2;
    margin-bottom: 0.5rem;
    letter-spacing: -0.015em;
}
.feature-card-desc {
    font-size: 0.92rem;
    font-weight: 300;
    color: #666;
    line-height: 1.6;
}

/* ─────────────────────────────────────────────────────
   CLOSING
   ───────────────────────────────────────────────────── */
.closing {
    width: 100%;
    padding: 8rem 1.5rem;
    background: #050505;
    border-top: 1px solid rgba(255,255,255,0.04);
    text-align: center;
    position: relative;
    overflow: hidden;
}
.closing::before {
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(ellipse 50% 60% at 50% 100%, rgba(0,200,5,0.08), transparent 70%);
    pointer-events: none;
}
.closing-inner {
    position: relative;
    z-index: 2;
    max-width: 720px;
    margin: 0 auto;
}
.closing-headline {
    font-family: 'Geist', sans-serif !important;
    font-size: clamp(1.9rem, 3.6vw, 2.8rem) !important;
    font-weight: 600 !important;
    letter-spacing: -0.035em !important;
    line-height: 1.1 !important;
    color: #f5f5f5 !important;
    margin: 0 auto 0.9rem !important;
    max-width: 18ch !important;
}
.closing-headline .accent { color: #00C805; }
.closing-sub {
    font-size: 1rem;
    color: #777;
    margin: 0 auto 2.4rem !important;
    font-weight: 300;
    max-width: 480px !important;
}
.closing-cta-row {
    display: flex;
    justify-content: center;
    gap: 0.8rem;
    flex-wrap: wrap;
}

/* ─────────────────────────────────────────────────────
   RESPONSIVE
   ───────────────────────────────────────────────────── */
@media (max-width: 760px) {
    .features-grid { grid-template-columns: 1fr; }
    .hero-stats { gap: 1.4rem; }
    .hero-body { padding: 1.5rem 1.2rem 5rem; }
    .hero-nav { padding: 1.4rem 1.5rem; }
    .features-section, .closing { padding: 5rem 1.2rem; }
}
</style>
""", unsafe_allow_html=True)


st.markdown("""
<div class="hero">
  <div class="hero-nav">
    <a href="/" class="hero-logo" target="_self" style="text-decoration:none;color:inherit;">
      <div class="hero-logo-mark">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
          <rect x="2"  y="10" width="2.4" height="4" rx="0.6" fill="#001a01"/>
          <rect x="6.8" y="6"  width="2.4" height="8" rx="0.6" fill="#001a01"/>
          <rect x="11.6" y="2" width="2.4" height="12" rx="0.6" fill="#001a01"/>
        </svg>
      </div>
      <div class="hero-logo-text">MockMarket</div>
    </a>
    <a href="/login" class="hero-nav-link" target="_self">Sign in →</a>
  </div>
  <div class="hero-body">
    <div class="hero-tag"><span class="hero-tag-dot"></span>Live market data · Zero real-money risk</div>
    <h1 class="hero-headline">Trade smarter.<br><span class="accent">Risk nothing.</span></h1>
    <p class="hero-sub">Practice the markets with real-time data and $10,000 in virtual capital. Build conviction, test strategies, and compete on the leaderboard — all without putting a cent on the line.</p>
    <div class="hero-ctas">
      <a href="/signup" class="btn-primary" target="_self">Start trading free<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg></a>
      <a href="/login" class="btn-secondary" target="_self">I already have an account</a>
    </div>
    <div class="hero-stats">
      <div class="hero-stat"><div class="hero-stat-num"><span class="accent">$10,000</span></div><div class="hero-stat-label">Starting capital</div></div>
      <div class="hero-stat"><div class="hero-stat-num">5,000+</div><div class="hero-stat-label">Tradeable tickers</div></div>
      <div class="hero-stat"><div class="hero-stat-num">Real-time</div><div class="hero-stat-label">Market data</div></div>
      <div class="hero-stat"><div class="hero-stat-num">$0</div><div class="hero-stat-label">Risk to you</div></div>
    </div>
  </div>
</div>
<div class="features-section">
  <div class="features-inner">
    <div class="features-eyebrow">— What you get</div>
    <h2 class="features-section-title">Everything you need to learn the market, <span class="accent">none of the risk.</span></h2>
    <p class="features-section-sub">Built for traders who want to sharpen their instincts before putting real money on the line.</p>
    <div class="features-grid">
      <div class="feature-card">
        <div class="feature-card-num">01</div>
        <div class="feature-card-icon"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/></svg></div>
        <div class="feature-card-title">Real-time stock trading</div>
        <div class="feature-card-desc">Buy and sell thousands of US-listed stocks with live prices. Track positions, P&amp;L, and FIFO cost basis — exactly like a real brokerage.</div>
      </div>
      <div class="feature-card">
        <div class="feature-card-num">02</div>
        <div class="feature-card-icon"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><circle cx="15.5" cy="15.5" r="1.5"/><circle cx="8.5" cy="15.5" r="1.5"/><circle cx="15.5" cy="8.5" r="1.5"/></svg></div>
        <div class="feature-card-title">Monte Carlo simulation</div>
        <div class="feature-card-desc">Forecast portfolio outcomes across thousands of simulated paths. Visualize probability distributions and stress-test your strategy.</div>
      </div>
      <div class="feature-card">
        <div class="feature-card-num">03</div>
        <div class="feature-card-icon"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg></div>
        <div class="feature-card-title">Market predictions</div>
        <div class="feature-card-desc">Call your shot on price movements and track your accuracy over time. Sharpen your intuition with feedback you can measure.</div>
      </div>
      <div class="feature-card">
        <div class="feature-card-num">04</div>
        <div class="feature-card-icon"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"/><path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18"/><path d="M4 22h16"/><path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22"/><path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22"/><path d="M18 2H6v7a6 6 0 0 0 12 0V2Z"/></svg></div>
        <div class="feature-card-title">Compete on the leaderboard</div>
        <div class="feature-card-desc">Rank by net worth against every trader on the platform. See where your strategy stands — and what it takes to climb.</div>
      </div>
    </div>
  </div>
</div>
<div class="closing">
  <div class="closing-inner">
    <h2 class="closing-headline">Ready to put your strategy <span class="accent">to the test?</span></h2>
    <p class="closing-sub">Sign up free. No credit card. Trade in under a minute.</p>
    <div class="closing-cta-row">
      <a href="/signup" class="btn-primary" target="_self">Create free account<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg></a>
      <a href="/login" class="btn-secondary" target="_self">Sign in</a>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)
