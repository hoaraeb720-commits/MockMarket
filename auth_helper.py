"""Authentication helper for all protected pages."""

import streamlit as st
from session_manager import validate_session
from database import get_wallet_balance
from constants import INITIAL_BALANCE


def restore_session() -> bool:
    """Restore session from session state if valid.

    Checks st.session_state.session_token, validates it,
    and populates session state fields if valid.

    Returns True if a valid session exists.
    """
    # Initialize session state defaults
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.session_token = None
        st.session_state.wallet_balance = INITIAL_BALANCE

    # Already validated this run
    if st.session_state.logged_in and st.session_state.session_token:
        is_valid, username = validate_session(st.session_state.session_token)
        if is_valid:
            return True
        # Token expired — clear state
        _clear_session_state()
        return False

    return False


def require_login():
    """Ensure user is logged in. Redirect to login if not.

    Call at the top of every protected page.
    """
    if restore_session():
        return True

    st.error("Session expired or invalid. Please log in again.")
    st.switch_page("pages/login.py")
    return False


def _clear_session_state():
    """Reset all session-related state."""
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.session_token = None
