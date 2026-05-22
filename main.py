import streamlit as st
from session_manager import validate_session
from database import get_wallet_balance

# Initialize session state for authentication
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.session_token = None
    st.session_state.wallet_balance = 10000

# Always check for persistent session token in URL params (on every page load)
token_from_url = st.query_params.get("session_token")
if token_from_url:
    is_valid, username = validate_session(token_from_url)
    
    if is_valid:
        # Restore session
        st.session_state.logged_in = True
        st.session_state.username = username
        st.session_state.session_token = token_from_url
        # Get wallet balance from database
        wallet_balance = get_wallet_balance(username)
        st.session_state.wallet_balance = (
            wallet_balance if wallet_balance is not None else 10000
        )
    else:
        # Invalid session token, clear it
        st.query_params.clear()
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.session_token = None
elif st.session_state.session_token:
    # Validate existing session in state
    is_valid, username = validate_session(st.session_state.session_token)
    if not is_valid:
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.session_token = None

# Define pages based on login status
if st.session_state.logged_in:
    pages = [
        st.Page("pages/dashboard.py", title="Dashboard"),
        st.Page("pages/leaderboard.py", title="Leaderboard"),
        st.Page("pages/predict.py", title="Make a Prediction"),
        st.Page("pages/monte_carlo.py", title="Monte Carlo Simulation"),
    ]
else:
    pages = [
        st.Page("pages/login.py", title="Login"),
        st.Page("pages/signup.py", title="Sign Up"),
    ]

pg = st.navigation(pages, position="top")
pg.run()
