import streamlit as st
from database import verify_user, get_wallet_balance
from session_manager import create_session
from constants import INITIAL_BALANCE

st.set_page_config(
    page_title="MockMarket — Sign In",
    page_icon="📈",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Geist:wght@300;400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: 'Geist', sans-serif;
    background-color: #070707 !important;
    color: #f2f2f2;
}

#MainMenu, footer, header { visibility: hidden; }

.main .block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

section[data-testid="stMain"] > div {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    padding: 2rem 1.5rem;
}

.login-card {
    width: 100%;
    max-width: 400px;
}

.back-link {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    font-size: 0.75rem;
    color: #2a2a2a;
    text-decoration: none;
    margin-bottom: 2.4rem;
    transition: color 0.15s;
    letter-spacing: 0.02em;
}
.back-link:hover { color: #555; }

.login-logo {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 2.4rem;
}
.login-logo-text {
    font-family: 'Geist', sans-serif;
    font-size: 1rem;
    font-weight: 600;
    color: #f2f2f2;
    letter-spacing: -0.01em;
}
.login-logo-text span { color: #00C805; }

.login-heading {
    font-family: 'Instrument Serif', serif;
    font-size: 1.9rem;
    font-weight: 400;
    letter-spacing: -0.025em;
    color: #f2f2f2;
    line-height: 1.1;
    margin-bottom: 0.4rem;
}
.login-sub {
    font-size: 0.82rem;
    color: #2e2e2e;
    font-weight: 300;
    margin-bottom: 2rem;
}

.login-divider {
    height: 1px;
    background: #111;
    margin-bottom: 2rem;
}

div[data-testid="stTextInput"] label,
div[data-testid="stPasswordInput"] label {
    font-size: 0.7rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    color: #2e2e2e !important;
}

div[data-testid="stTextInput"] input,
div[data-testid="stPasswordInput"] input {
    background: #0c0c0c !important;
    border: 1px solid #161616 !important;
    border-radius: 8px !important;
    color: #f2f2f2 !important;
    font-family: 'Geist', sans-serif !important;
    font-size: 0.9rem !important;
    padding: 0.68rem 1rem !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
div[data-testid="stTextInput"] input:hover,
div[data-testid="stPasswordInput"] input:hover {
    border-color: #222 !important;
}
div[data-testid="stTextInput"] input:focus,
div[data-testid="stPasswordInput"] input:focus {
    border-color: #00C805 !important;
    box-shadow: 0 0 0 3px rgba(0,200,5,0.06) !important;
    outline: none !important;
}

div[data-testid="stTextInput"],
div[data-testid="stPasswordInput"] {
    margin-bottom: 0.6rem !important;
}

.login-meta {
    display: flex;
    justify-content: flex-end;
    margin-bottom: 1.4rem;
    margin-top: -0.2rem;
}
.login-meta a {
    font-size: 0.73rem;
    color: #252525;
    text-decoration: none;
    transition: color 0.15s;
}
.login-meta a:hover { color: #555; }

div[data-testid="stFormSubmitButton"] button {
    width: 100% !important;
    background: #00C805 !important;
    color: #000 !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Geist', sans-serif !important;
    font-size: 0.88rem !important;
    font-weight: 600 !important;
    padding: 0.75rem !important;
    letter-spacing: 0.02em !important;
    transition: background 0.15s, transform 0.12s, box-shadow 0.15s !important;
}
div[data-testid="stFormSubmitButton"] button:hover {
    background: #05e00a !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 24px rgba(0,200,5,0.18) !important;
}
div[data-testid="stFormSubmitButton"] button:active {
    transform: translateY(0) !important;
}

.login-footer-text {
    text-align: center;
    font-size: 0.78rem;
    color: #222;
    margin-top: 1.8rem;
}

div[data-testid="stButton"] button {
    width: 100% !important;
    background: transparent !important;
    color: #282828 !important;
    border: 1px solid #141414 !important;
    border-radius: 8px !important;
    font-family: 'Geist', sans-serif !important;
    font-size: 0.85rem !important;
    font-weight: 400 !important;
    padding: 0.68rem !important;
    margin-top: 0.6rem !important;
    transition: border-color 0.15s, color 0.15s !important;
}
div[data-testid="stButton"] button:hover {
    border-color: #242424 !important;
    color: #666 !important;
    background: transparent !important;
}

div[data-testid="stAlert"] {
    border-radius: 8px !important;
    font-size: 0.83rem !important;
    margin-top: 0.8rem !important;
}
</style>
""", unsafe_allow_html=True)

if st.session_state.get("logged_in"):
    st.rerun()

st.markdown("""
<div class="login-card">
    <a class="back-link" href="/">← MockMarket</a>
    <div class="login-logo">
        <svg width="22" height="22" viewBox="0 0 36 36" fill="none">
          <polygon points="2,28 10,8 18,20 14,20 10,12 6,28"   fill="#00C805"/>
          <polygon points="18,20 26,8 34,28 30,28 26,12 22,20" fill="#00C805"/>
          <polygon points="14,20 18,20 22,20 18,26"            fill="#00C805"/>
        </svg>
        <div class="login-logo-text">Mock<span>Market</span></div>
    </div>
    <div class="login-heading">Welcome back</div>
    <div class="login-sub">Sign in to continue to your portfolio</div>
    <div class="login-divider"></div>
</div>
""", unsafe_allow_html=True)

with st.form("login_form"):
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    st.markdown('<div class="login-meta"><a href="#">Forgot password?</a></div>', unsafe_allow_html=True)
    submitted = st.form_submit_button("Sign in")

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
                    wallet_balance if wallet_balance is not None else INITIAL_BALANCE
                )
                st.success(message)
                st.rerun()
            else:
                st.error(message)

st.markdown('<div class="login-footer-text">Don\'t have an account?</div>', unsafe_allow_html=True)

if st.button("Create a free account"):
    st.switch_page("pages/signup.py")