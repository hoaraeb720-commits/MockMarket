import streamlit as st
import streamlit.components.v1 as components
from database import verify_user, get_wallet_balance
from session_manager import create_session

st.set_page_config(page_title="MockMarket — Login", page_icon="📈", layout="wide")

# ── Global Streamlit styles (right panel + page shell) ────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0a0a0a !important;
    color: #f0f0f0;
}

#MainMenu, footer, header { visibility: hidden; }

/* Remove all default page padding */
.main .block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* Kill gap between columns */
div[data-testid="stHorizontalBlock"] {
    gap: 0 !important;
}

/* Right column — vertically centered, padded */
div[data-testid="column"]:nth-child(2) {
    display: flex !important;
    flex-direction: column !important;
    justify-content: center !important;
    min-height: 100vh !important;
    padding: 3rem 5rem !important;
    background: #0a0a0a;
}

/* ── Form heading ── */
.mm-form-title {
    font-size: 1.8rem;
    font-weight: 700;
    color: #fff;
    letter-spacing: -0.02em;
    margin-bottom: 0.3rem;
}
.mm-form-sub {
    font-size: 0.88rem;
    color: #555;
    margin-bottom: 1.8rem;
}

/* ── Input labels ── */
div[data-testid="stTextInput"] label,
div[data-testid="stPasswordInput"] label {
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
    color: #555 !important;
}

/* ── Inputs ── */
div[data-testid="stTextInput"] input,
div[data-testid="stPasswordInput"] input {
    background: #111 !important;
    border: 1px solid #222 !important;
    border-radius: 10px !important;
    color: #f0f0f0 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.95rem !important;
    padding: 0.65rem 0.9rem !important;
    transition: border-color 0.15s ease !important;
}
div[data-testid="stTextInput"] input:focus,
div[data-testid="stPasswordInput"] input:focus {
    border-color: #00C805 !important;
    box-shadow: 0 0 0 3px rgba(0,200,5,0.08) !important;
}

/* ── Login button ── */
div[data-testid="stFormSubmitButton"] button {
    width: 100% !important;
    background: #00C805 !important;
    color: #000 !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.95rem !important;
    font-weight: 700 !important;
    padding: 0.72rem !important;
    letter-spacing: 0.02em !important;
    margin-top: 0.5rem !important;
    transition: background 0.15s ease, transform 0.1s ease !important;
}
div[data-testid="stFormSubmitButton"] button:hover {
    background: #00e006 !important;
    transform: translateY(-1px) !important;
}

/* ── Create account button ── */
div[data-testid="stButton"] button {
    width: 100% !important;
    background: transparent !important;
    color: #666 !important;
    border: 1px solid #1e1e1e !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.9rem !important;
    font-weight: 500 !important;
    padding: 0.65rem !important;
    transition: border-color 0.15s ease, color 0.15s ease !important;
}
div[data-testid="stButton"] button:hover {
    border-color: #00C805 !important;
    color: #00C805 !important;
    background: transparent !important;
}

.mm-divider-text {
    text-align: center;
    color: #2a2a2a;
    font-size: 0.78rem;
    margin: 1rem 0;
    letter-spacing: 0.05em;
}

div[data-testid="stAlert"] {
    border-radius: 10px !important;
    font-size: 0.875rem !important;
}
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.session_token = None

if st.session_state.logged_in:
    st.rerun()

# ── Left panel HTML (self-contained, rendered in iframe) ──────────────────────
LEFT_PANEL_HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    font-family: 'DM Sans', sans-serif;
    background: #0d0d0d;
    color: #f0f0f0;
    height: 100vh;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 2.8rem 3rem;
    border-right: 1px solid #1a1a1a;
  }

  /* ── Logo ── */
  .logo {
    display: flex;
    align-items: center;
    gap: 10px;
  }
  .logo-text {
    font-size: 1.4rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    color: #fff;
  }
  .logo-text span { color: #00C805; }

  /* ── Portfolio ── */
  .portfolio-label {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #444;
    margin-bottom: 0.35rem;
    margin-top: 2.5rem;
  }
  .portfolio-value {
    font-size: 2.6rem;
    font-weight: 700;
    color: #fff;
    letter-spacing: -0.03em;
    line-height: 1;
    margin-bottom: 0.4rem;
  }
  .portfolio-gain {
    font-size: 0.9rem;
    font-weight: 500;
    color: #00C805;
    margin-bottom: 1.6rem;
  }

  /* ── Chart ── */
  .chart-wrap {
    width: 100%;
  }

  /* ── Stats ── */
  .stats-row {
    display: flex;
    gap: 2.5rem;
    margin-top: 1.8rem;
    padding-top: 1.4rem;
    border-top: 1px solid #1a1a1a;
  }
  .stat-val {
    font-size: 1rem;
    font-weight: 600;
    color: #fff;
  }
  .stat-lbl {
    font-size: 0.68rem;
    color: #444;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 0.15rem;
  }

  /* ── Tagline ── */
  .tagline {
    font-size: 0.72rem;
    color: #272727;
    letter-spacing: 0.07em;
    text-transform: uppercase;
  }

  /* ── Animations ── */
  @keyframes drawLine {
    from { stroke-dashoffset: 1200; }
    to   { stroke-dashoffset: 0; }
  }
  @keyframes fadeIn {
    from { opacity: 0; }
    to   { opacity: 1; }
  }
  .chart-line {
    stroke-dasharray: 1200;
    stroke-dashoffset: 1200;
    animation: drawLine 2.4s cubic-bezier(0.4,0,0.2,1) forwards;
  }
  .chart-area {
    opacity: 0;
    animation: fadeIn 1s ease 2s forwards;
  }
  .chart-dot {
    opacity: 0;
    animation: fadeIn 0.4s ease 2.3s forwards;
  }
</style>
</head>
<body>

  <!-- Logo -->
  <div class="logo">
    <svg width="30" height="30" viewBox="0 0 36 36" fill="none">
      <polygon points="2,28 10,8 18,20 14,20 10,12 6,28"   fill="#00C805"/>
      <polygon points="18,20 26,8 34,28 30,28 26,12 22,20" fill="#00C805"/>
      <polygon points="14,20 18,20 22,20 18,26"            fill="#00C805"/>
    </svg>
    <div class="logo-text">Mock<span>Market</span></div>
  </div>

  <!-- Chart section -->
  <div>
    <div class="portfolio-label">Portfolio Value</div>
    <div class="portfolio-value">$12,483.21</div>
    <div class="portfolio-gain">▲ $2,483.21 &nbsp;&nbsp;+24.83% all time</div>

    <div class="chart-wrap">
      <svg viewBox="0 0 560 210" xmlns="http://www.w3.org/2000/svg"
           style="width:100%;display:block;overflow:visible;">
        <defs>
          <linearGradient id="cg" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%"   stop-color="#00C805" stop-opacity="0.22"/>
            <stop offset="100%" stop-color="#00C805" stop-opacity="0"/>
          </linearGradient>
        </defs>

        <!-- Grid -->
        <line x1="30" y1="20"  x2="555" y2="20"  stroke="#161616" stroke-width="1"/>
        <line x1="30" y1="72"  x2="555" y2="72"  stroke="#161616" stroke-width="1"/>
        <line x1="30" y1="124" x2="555" y2="124" stroke="#161616" stroke-width="1"/>
        <line x1="30" y1="176" x2="555" y2="176" stroke="#161616" stroke-width="1"/>

        <!-- Y labels -->
        <text x="0" y="24"  fill="#2a2a2a" font-size="11" font-family="DM Sans,sans-serif">13K</text>
        <text x="0" y="76"  fill="#2a2a2a" font-size="11" font-family="DM Sans,sans-serif">12K</text>
        <text x="0" y="128" fill="#2a2a2a" font-size="11" font-family="DM Sans,sans-serif">11K</text>
        <text x="0" y="180" fill="#2a2a2a" font-size="11" font-family="DM Sans,sans-serif">10K</text>

        <!-- X labels -->
        <text x="36"  y="200" fill="#2a2a2a" font-size="11" font-family="DM Sans,sans-serif">May 1</text>
        <text x="150" y="200" fill="#2a2a2a" font-size="11" font-family="DM Sans,sans-serif">May 8</text>
        <text x="268" y="200" fill="#2a2a2a" font-size="11" font-family="DM Sans,sans-serif">May 15</text>
        <text x="382" y="200" fill="#2a2a2a" font-size="11" font-family="DM Sans,sans-serif">May 22</text>
        <text x="484" y="200" fill="#2a2a2a" font-size="11" font-family="DM Sans,sans-serif">May 29</text>

        <!-- Area fill -->
        <path class="chart-area"
          d="M36,170 C60,163 78,157 100,148 C126,137 140,130 165,120
             C192,109 208,102 236,91  C264,80  280,73  308,62
             C336,51  354,44  382,36  C410,28  428,24  456,20
             C478,17  494,15  525,10
             L525,185 L36,185 Z"
          fill="url(#cg)"/>

        <!-- Line -->
        <path class="chart-line"
          d="M36,170 C60,163 78,157 100,148 C126,137 140,130 165,120
             C192,109 208,102 236,91  C264,80  280,73  308,62
             C336,51  354,44  382,36  C410,28  428,24  456,20
             C478,17  494,15  525,10"
          fill="none" stroke="#00C805" stroke-width="2.5"
          stroke-linecap="round" stroke-linejoin="round"/>

        <!-- End dot -->
        <circle class="chart-dot" cx="525" cy="10" r="4.5" fill="#00C805"/>
        <circle class="chart-dot" cx="525" cy="10" r="10"  fill="#00C805" fill-opacity="0.15"/>
      </svg>
    </div>

    <div class="stats-row">
      <div>
        <div class="stat-val">10,000+</div>
        <div class="stat-lbl">Students</div>
      </div>
      <div>
        <div class="stat-val">$0 risk</div>
        <div class="stat-lbl">All skill</div>
      </div>
      <div>
        <div class="stat-val">Live data</div>
        <div class="stat-lbl">Real prices</div>
      </div>
    </div>
  </div>

  <!-- Tagline -->
  <div class="tagline">The stock market. Simulated. Not simplified.</div>

</body>
</html>
"""

# ── Layout ────────────────────────────────────────────────────────────────────
left_col, right_col = st.columns([1.15, 0.85])

with left_col:
    components.html(LEFT_PANEL_HTML, height=800, scrolling=False)

with right_col:
    st.markdown("""
        <div class="mm-form-title">Welcome back</div>
        <div class="mm-form-sub">Sign in to your MockMarket account</div>
    """, unsafe_allow_html=True)

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Log In")

        if submitted:
            if not username or not password:
                st.error("Please fill in all fields.")
            else:
                success, message = verify_user(username, password)
                if success:
                    token = create_session(username)
                    wallet_balance = get_wallet_balance(username)
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.session_token = token
                    st.session_state.wallet_balance = (
                        wallet_balance if wallet_balance is not None else 10000
                    )
                    st.query_params["session_token"] = token
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

    st.markdown('<div class="mm-divider-text">— or —</div>', unsafe_allow_html=True)
    if st.button("Create an Account"):
        st.switch_page("pages/signup.py")