import streamlit as st
from session_manager import validate_session
from database import get_wallet_balance

# Initialize session state for authentication
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.session_token = None
    st.session_state.wallet_balance = 10000

# Check for persistent session token in URL params
if not st.session_state.logged_in and "session_token" in st.query_params:
    token = st.query_params.get("session_token")
    is_valid, username = validate_session(token)
    
    if is_valid:
        # Restore session
        st.session_state.logged_in = True
        st.session_state.username = username
        st.session_state.session_token = token
        # Get wallet balance from database
        wallet_balance = get_wallet_balance(username)
        st.session_state.wallet_balance = wallet_balance if wallet_balance is not None else 10000
    else:
        # Invalid session token, remove it
        st.query_params.pop("session_token", None)

# Define pages based on login status
if st.session_state.logged_in:
    pages = [
        st.Page("pages/dashboard.py", title="Dashboard"),
    ]
else:
    pages = [
        st.Page("pages/login.py", title="Login"),
        st.Page("pages/signup.py", title="Sign Up"),
    ]

pg = st.navigation(pages, position="top")
pg.run()

