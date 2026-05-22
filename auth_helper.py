"""Authentication helper for all protected pages."""

import streamlit as st
from session_manager import validate_session
from database import get_wallet_balance


def require_login():
    """Ensure user is logged in. Redirect to login if not.
    
    This should be called at the top of every protected page.
    It will also preserve the session token in URL query params.
    """
    # Check for session token in URL params
    token_from_url = st.query_params.get("session_token")
    
    if token_from_url:
        is_valid, username = validate_session(token_from_url)
        if is_valid:
            # Update session state
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.session_token = token_from_url
            wallet_balance = get_wallet_balance(username)
            st.session_state.wallet_balance = (
                wallet_balance if wallet_balance is not None else 10000
            )
            # Session is valid, proceed
            return True
    
    # Check if session token exists in state (from previous page)
    if st.session_state.get("session_token"):
        token = st.session_state.session_token
        is_valid, username = validate_session(token)
        if is_valid:
            # Restore URL params
            st.query_params["session_token"] = token
            return True
        else:
            st.session_state.logged_in = False
    
    # No valid session, redirect to login
    st.error("Session expired or invalid. Please log in again.")
    st.switch_page("pages/login.py")
    return False
