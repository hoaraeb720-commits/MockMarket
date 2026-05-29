import streamlit as st
from database import create_user, create_wallet
from session_manager import create_session
from profanity_check import check_username
from constants import INITIAL_BALANCE
from auth_helper import set_session_cookie
from styles import apply_theme, LOGO_SVG

st.set_page_config(
    page_title="MockMarket — Sign Up",
    page_icon="📈",
    layout="wide",
)

apply_theme()

st.markdown("""
<style>
section[data-testid="stMain"] .block-container,
.main .block-container,
[data-testid="stAppViewBlockContainer"] {
    padding: 0 !important;
    max-width: 100% !important;
}
section[data-testid="stMain"] > div { padding: 0 !important; }

.auth-bg {
    position: fixed;
    inset: 0;
    background:
        radial-gradient(ellipse 60% 50% at 50% 30%, rgba(0,200,5,0.06), transparent 70%),
        #050505;
    z-index: -1;
}
.auth-bg::before {
    content: '';
    position: absolute;
    inset: 0;
    background-image:
        linear-gradient(rgba(255,255,255,0.015) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.015) 1px, transparent 1px);
    background-size: 60px 60px;
    mask-image: radial-gradient(ellipse 60% 60% at 50% 40%, black, transparent 80%);
    -webkit-mask-image: radial-gradient(ellipse 60% 60% at 50% 40%, black, transparent 80%);
    pointer-events: none;
}

.auth-nav {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1.8rem 2.5rem;
}
.auth-intro {
    text-align: center;
    padding: 3.5rem 1.5rem 2rem;
}
.auth-eyebrow {
    color: #00C805;
    font-family: 'Geist Mono', monospace;
    font-size: 0.7rem;
    font-weight: 500;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 1.2rem;
}
.auth-headline {
    font-family: 'Geist', sans-serif !important;
    font-size: 2.6rem !important;
    font-weight: 600 !important;
    letter-spacing: -0.03em !important;
    line-height: 1.05 !important;
    color: #f5f5f5 !important;
    margin: 0 0 0.6rem 0 !important;
    background: linear-gradient(180deg, #ffffff 0%, #c0c0c0 100%);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
}
.auth-sub {
    font-size: 1rem;
    color: #777;
    font-weight: 300;
    margin: 0 !important;
}
.auth-footer {
    margin-top: 1.6rem;
    font-size: 0.88rem;
    color: #666;
    text-align: center;
}
.auth-form-stem { padding-bottom: 5rem; }
</style>
<div class="auth-bg"></div>
""", unsafe_allow_html=True)

if st.session_state.get("logged_in"):
    st.switch_page("pages/dashboard.py")

st.markdown(f"""
<div class="auth-nav">
  <a href="/" class="mm-logo" target="_self" style="text-decoration:none;color:inherit;">
    <div class="mm-logo-mark" style="width:28px;height:28px;">{LOGO_SVG}</div>
    <div class="mm-logo-text">MockMarket</div>
  </a>
  <a href="/" class="mm-nav-link" target="_self">← Back</a>
</div>
<div class="auth-intro">
  <div class="auth-eyebrow">— Get started</div>
  <h1 class="auth-headline">Create your account</h1>
  <p class="auth-sub">Start trading with $10,000 in virtual capital. Free, no credit card.</p>
</div>
""", unsafe_allow_html=True)

_, form_col, _ = st.columns([1, 1, 1])

with form_col:
    with st.form("signup_form"):
        username = st.text_input("Username", placeholder="Pick a username")
        password = st.text_input("Password", type="password", placeholder="••••••••")
        confirm_password = st.text_input(
            "Confirm password", type="password", placeholder="••••••••"
        )
        submitted = st.form_submit_button("Create account")

        if submitted:
            if not username or not password or not confirm_password:
                st.error("Please fill in all fields.")
            elif password != confirm_password:
                st.error("Passwords do not match. Please try again.")
            else:
                username_check = check_username(username=username)
                if username_check["flagged"]:
                    st.error(
                        "Username contains inappropriate content. "
                        "Please choose a different username."
                    )
                else:
                    success, message = create_user(username, password)
                    if success:
                        create_wallet(username)
                        token = create_session(username)
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.session_token = token
                        st.session_state.wallet_balance = INITIAL_BALANCE
                        set_session_cookie(token)
                        st.success(message)
                        st.switch_page("pages/dashboard.py")
                    else:
                        st.error(message)

    st.markdown(
        '<div class="auth-footer">Already have an account? '
        '<a href="/login" class="mm-link" target="_self">Sign in</a></div>',
        unsafe_allow_html=True,
    )

st.markdown('<div class="auth-form-stem"></div>', unsafe_allow_html=True)
