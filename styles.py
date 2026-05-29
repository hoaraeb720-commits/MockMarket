"""Shared theme styles for MockMarket pages.

All pages call `apply_theme()` near the top to inject the global dark theme
and the SVG logo helper.
"""

import streamlit as st


LOGO_SVG = """
<svg width="16" height="16" viewBox="0 0 16 16" fill="none">
  <rect x="2"  y="10" width="2.4" height="4"  rx="0.6" fill="#001a01"/>
  <rect x="6.8" y="6"  width="2.4" height="8"  rx="0.6" fill="#001a01"/>
  <rect x="11.6" y="2" width="2.4" height="12" rx="0.6" fill="#001a01"/>
</svg>
"""


def logo_html(size: int = 28) -> str:
    """Return the MockMarket lockup (mark + wordmark) HTML."""
    return f"""
<div class="mm-logo">
  <div class="mm-logo-mark" style="width:{size}px;height:{size}px;">{LOGO_SVG}</div>
  <div class="mm-logo-text">MockMarket</div>
</div>
"""


def app_nav(active: str) -> None:
    """Render the top navigation bar for protected pages.

    `active` is the slug of the current page: dashboard, leaderboard, predict, monte_carlo.
    Sign-out is a query-param link (?signout=1) handled here.
    """
    import streamlit as st
    from auth_helper import clear_session_cookie
    from session_manager import logout_session

    # Handle sign-out from URL query param
    if st.query_params.get("signout"):
        token = st.session_state.get("session_token")
        if token:
            logout_session(token)
        clear_session_cookie()
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.session_token = None
        st.query_params.clear()
        st.switch_page("pages/landing.py")

    items = [
        ("dashboard", "Trade"),
        ("leaderboard", "Leaderboard"),
        ("predict", "Forecast"),
        ("monte_carlo", "Monte Carlo"),
    ]
    links_html = "".join(
        f'<a href="/{slug}" class="mm-app-nav-link{" is-active" if slug == active else ""}" target="_self">{label}</a>'
        for slug, label in items
    )
    username = st.session_state.get("username", "")

    st.markdown(
        f"""
<style>
.mm-app-nav {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1.4rem 0;
    margin-bottom: 2rem;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    gap: 2rem;
}}
.mm-app-nav-left {{ display: flex; align-items: center; gap: 2.4rem; }}
.mm-app-nav-right {{ display: flex; align-items: center; gap: 0.8rem; margin-left: auto; }}
.mm-app-nav-links {{ display: flex; gap: 1.6rem; align-items: center; }}
.mm-app-nav-link, .mm-app-nav-link:visited, .mm-app-nav-link:link {{
    color: #888 !important;
    font-family: 'Geist', sans-serif;
    font-size: 0.9rem;
    font-weight: 500;
    text-decoration: none !important;
    transition: color 0.15s;
    padding: 0.4rem 0;
    position: relative;
}}
.mm-app-nav-link:hover {{ color: #f2f2f2 !important; }}
.mm-app-nav-link.is-active {{ color: #f2f2f2 !important; }}
.mm-app-nav-link.is-active::after {{
    content: '';
    position: absolute;
    left: 0; right: 0; bottom: -1.5rem;
    height: 2px;
    background: #00C805;
}}
.mm-app-nav-user {{
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    color: #888;
    font-size: 0.85rem;
    padding: 0.45rem 0.9rem 0.45rem 0.7rem;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 100px;
    line-height: 1;
}}
.mm-app-nav-user .dot {{
    width: 6px;
    height: 6px;
    background: #00C805;
    border-radius: 50%;
    box-shadow: 0 0 8px #00C805;
}}
.mm-app-nav-user strong {{ color: #f2f2f2; font-weight: 500; }}
.mm-app-nav-signout, .mm-app-nav-signout:visited, .mm-app-nav-signout:link {{
    color: #888 !important;
    font-family: 'Geist', sans-serif !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    text-decoration: none !important;
    padding: 0.45rem 0.9rem !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    background: rgba(255,255,255,0.03) !important;
    border-radius: 100px !important;
    line-height: 1 !important;
    transition: color 0.15s, border-color 0.15s, background 0.15s;
}}
.mm-app-nav-signout:hover {{
    color: #ff6060 !important;
    border-color: rgba(255,80,80,0.25) !important;
    background: rgba(255,80,80,0.06) !important;
    text-decoration: none !important;
}}
</style>
<div class="mm-app-nav">
  <div class="mm-app-nav-left">
    <a href="/dashboard" target="_self" style="text-decoration:none;color:inherit;">
      <div class="mm-logo">
        <div class="mm-logo-mark" style="width:28px;height:28px;">{LOGO_SVG}</div>
        <div class="mm-logo-text">MockMarket</div>
      </div>
    </a>
    <div class="mm-app-nav-links">{links_html}</div>
  </div>
  <div class="mm-app-nav-right">
    <div class="mm-app-nav-user"><span class="dot"></span><span>Signed in as <strong>{username}</strong></span></div>
    <a href="?signout=1" class="mm-app-nav-signout" target="_self">Sign out</a>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )



def apply_theme() -> None:
    """Inject global dark theme CSS — call once per page near the top."""
    st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=Geist:wght@300;400;500;600;700;800&family=Geist+Mono:wght@400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"], .stApp {
    font-family: 'Geist', sans-serif !important;
    background-color: #050505 !important;
    color: #f2f2f2;
}

#MainMenu, footer, header,
[data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="stStatusWidget"] { display: none !important; }
section[data-testid="stSidebar"] { display: none !important; }

/* Strip Streamlit's default top padding so our nav sits at the top */
.stApp > header { display: none !important; }
.stApp section[data-testid="stMain"] .block-container,
.stApp [data-testid="stAppViewBlockContainer"] {
    padding-top: 0 !important;
}
.stApp section[data-testid="stMain"] {
    padding-top: 0 !important;
}

/* ── Logo ─────────────────────────────────────────── */
.mm-logo {
    display: flex;
    align-items: center;
    gap: 10px;
}
.mm-logo-mark {
    border-radius: 7px;
    background: linear-gradient(135deg, #00C805 0%, #009804 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 14px rgba(0,200,5,0.35), inset 0 1px 0 rgba(255,255,255,0.18);
}
.mm-logo-text {
    font-family: 'Geist', sans-serif;
    font-size: 1rem;
    font-weight: 600;
    color: #f2f2f2;
    letter-spacing: -0.01em;
}

/* ── Anchor (text) links ──────────────────────────── */
a.mm-link, a.mm-link:visited, a.mm-link:link {
    color: #00C805 !important;
    text-decoration: none !important;
    font-weight: 500;
    transition: color 0.15s;
}
a.mm-link:hover { color: #05e00a !important; text-decoration: none !important; }

a.mm-nav-link, a.mm-nav-link:visited, a.mm-nav-link:link {
    color: #888 !important;
    font-size: 0.9rem;
    font-weight: 500;
    text-decoration: none !important;
    transition: color 0.15s;
}
a.mm-nav-link:hover { color: #f2f2f2 !important; text-decoration: none !important; }

/* ── Buttons (HTML anchors styled as buttons) ─────── */
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
}

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
}
.btn-secondary:hover {
    border-color: rgba(255,255,255,0.18) !important;
    color: #ffffff !important;
    background: rgba(255,255,255,0.06) !important;
}

/* ── Streamlit st.button primary ──────────────────── */
.stApp div[data-testid="stFormSubmitButton"] button,
.stApp div[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(180deg, #00d806 0%, #00b805 100%) !important;
    color: #001a01 !important;
    border: none !important;
    border-radius: 9px !important;
    font-family: 'Geist', sans-serif !important;
    font-size: 0.95rem !important;
    font-weight: 600 !important;
    padding: 0.75rem 1.4rem !important;
    letter-spacing: -0.005em !important;
    transition: transform 0.15s, box-shadow 0.15s, filter 0.15s !important;
    box-shadow:
        0 1px 0 rgba(255,255,255,0.25) inset,
        0 -1px 0 rgba(0,0,0,0.15) inset,
        0 8px 24px rgba(0,200,5,0.22) !important;
    width: 100% !important;
}
.stApp div[data-testid="stFormSubmitButton"] button:hover,
.stApp div[data-testid="stButton"] > button[kind="primary"]:hover {
    filter: brightness(1.08) !important;
    transform: translateY(-1px) !important;
}

/* ── Streamlit st.button secondary (default) ──────── */
.stApp div[data-testid="stButton"] > button:not([kind="primary"]) {
    background: rgba(255,255,255,0.03) !important;
    color: #d5d5d5 !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 9px !important;
    font-family: 'Geist', sans-serif !important;
    font-size: 0.92rem !important;
    font-weight: 500 !important;
    padding: 0.7rem 1.2rem !important;
    transition: all 0.15s !important;
    width: 100% !important;
}
.stApp div[data-testid="stButton"] > button:not([kind="primary"]):hover {
    border-color: rgba(255,255,255,0.18) !important;
    color: #ffffff !important;
    background: rgba(255,255,255,0.06) !important;
}

/* ── Inputs ───────────────────────────────────────── */
.stApp div[data-testid="stTextInput"] label,
.stApp div[data-testid="stPasswordInput"] label,
.stApp div[data-testid="stNumberInput"] label,
.stApp div[data-testid="stSelectbox"] label,
.stApp div[data-testid="stMultiSelect"] label {
    font-family: 'Geist Mono', monospace !important;
    font-size: 0.7rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    color: #666 !important;
}

/* Input wrapper — the actual rounded border lives here */
.stApp [data-testid="stTextInputRootElement"],
.stApp [data-testid="stNumberInputContainer"] {
    background: rgba(255,255,255,0.02) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 9px !important;
    transition: border-color 0.2s, box-shadow 0.2s, background 0.2s !important;
    overflow: hidden !important;
    box-shadow: none !important;
}
.stApp [data-testid="stTextInputRootElement"]:hover,
.stApp [data-testid="stNumberInputContainer"]:hover {
    border-color: rgba(255,255,255,0.14) !important;
    background: rgba(255,255,255,0.03) !important;
}
.stApp [data-testid="stTextInputRootElement"]:focus-within,
.stApp [data-testid="stNumberInputContainer"]:focus-within {
    border-color: #00C805 !important;
    box-shadow: 0 0 0 3px rgba(0,200,5,0.08) !important;
    background: rgba(255,255,255,0.03) !important;
}

/* Strip Streamlit's internal input styling so it flows inside the wrapper */
.stApp [data-testid="stTextInputRootElement"] > div,
.stApp [data-testid="stTextInputRootElement"] > div > div {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    border-radius: 0 !important;
}

.stApp [data-testid="stTextInput"] input,
.stApp [data-testid="stPasswordInput"] input,
.stApp [data-testid="stNumberInput"] input {
    background: transparent !important;
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
    color: #f2f2f2 !important;
    caret-color: #00C805 !important;
    font-family: 'Geist', sans-serif !important;
    font-size: 0.95rem !important;
    padding: 0.7rem 1rem !important;
}
.stApp [data-testid="stTextInput"] input::placeholder,
.stApp [data-testid="stPasswordInput"] input::placeholder {
    color: #444 !important;
}
/* Password reveal button — flat, integrates with input */
.stApp [data-testid="stTextInputRootElement"] button {
    background: transparent !important;
    border: none !important;
    border-radius: 0 !important;
    color: #555 !important;
    box-shadow: none !important;
    padding: 0 0.9rem !important;
    margin: 0 !important;
    transition: color 0.15s !important;
}
.stApp [data-testid="stTextInputRootElement"] button:hover {
    color: #00C805 !important;
    background: transparent !important;
    border: none !important;
}
.stApp [data-testid="stTextInputRootElement"] button svg {
    fill: currentColor !important;
}

/* ── Alerts ───────────────────────────────────────── */
.stApp div[data-testid="stAlert"] {
    border-radius: 9px !important;
    font-size: 0.88rem !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    background: rgba(255,255,255,0.02) !important;
}

/* ── Containers / cards ───────────────────────────── */
.stApp div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #080808 !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 12px !important;
}

/* ── Metrics ──────────────────────────────────────── */
.stApp [data-testid="stMetric"] {
    background: #080808;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px;
    padding: 1.2rem 1.3rem;
}
.stApp [data-testid="stMetricLabel"] {
    font-family: 'Geist Mono', monospace;
    font-size: 0.7rem !important;
    color: #666 !important;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}
.stApp [data-testid="stMetricValue"] {
    font-family: 'Geist', sans-serif;
    font-weight: 600;
    color: #f2f2f2;
    letter-spacing: -0.02em;
}

/* ── Tabs / pills (segmented control) ─────────────── */
.stApp [data-testid="stSegmentedControl"] button,
.stApp [data-baseweb="tab-list"] button {
    background: rgba(255,255,255,0.02) !important;
    color: #888 !important;
    border-radius: 7px !important;
    font-family: 'Geist', sans-serif !important;
    font-size: 0.85rem !important;
}

/* ── Markdown / headers inside the app ────────────── */
.stApp h1, .stApp h2, .stApp h3, .stApp h4 {
    font-family: 'Geist', sans-serif !important;
    color: #f2f2f2 !important;
    letter-spacing: -0.02em !important;
    font-weight: 600 !important;
}

/* ── Table ────────────────────────────────────────── */
.stApp [data-testid="stTable"], .stApp [data-testid="stDataFrame"] {
    background: #080808;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px;
}

/* ── Divider ──────────────────────────────────────── */
.stApp hr {
    border-color: rgba(255,255,255,0.06) !important;
    margin: 1.4rem 0 !important;
}
</style>
""",
        unsafe_allow_html=True,
    )
