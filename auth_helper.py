"""Authentication helper for all protected pages."""

import streamlit as st
import streamlit.components.v1 as components

from session_manager import validate_session
from database import get_wallet_balance
from constants import INITIAL_BALANCE

SESSION_COOKIE_NAME = "mm_session"
COOKIE_MAX_AGE_SECONDS = 24 * 3600


def set_session_cookie(token: str) -> None:
    """Write the session token to a browser cookie via JS on the parent frame.

    components.html mounts an iframe; we must reach window.parent to set
    the cookie on the actual Streamlit app's origin.
    """
    components.html(
        f"""
        <script>
            try {{
                window.parent.document.cookie =
                    "{SESSION_COOKIE_NAME}={token}; "
                    + "max-age={COOKIE_MAX_AGE_SECONDS}; "
                    + "path=/; "
                    + "SameSite=Lax";
            }} catch (e) {{ console.error("cookie set failed", e); }}
        </script>
        """,
        height=0,
    )


def clear_session_cookie() -> None:
    """Delete the session cookie."""
    components.html(
        f"""
        <script>
            try {{
                window.parent.document.cookie =
                    "{SESSION_COOKIE_NAME}=; max-age=0; path=/; SameSite=Lax";
            }} catch (e) {{ console.error("cookie clear failed", e); }}
        </script>
        """,
        height=0,
    )


def _read_cookie_token() -> str | None:
    """Read the session token from the browser cookie."""
    try:
        return st.context.cookies.get(SESSION_COOKIE_NAME)
    except Exception:
        return None


def restore_session() -> bool:
    """Restore session from state or cookie if valid.

    Order:
    1. If session_state already has a valid token, return True.
    2. Otherwise check the browser cookie. If valid, populate state.

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
        is_valid, _ = validate_session(st.session_state.session_token)
        if is_valid:
            return True
        _clear_session_state()

    # Try restoring from cookie (handles browser refresh)
    token = _read_cookie_token()
    if token:
        is_valid, username = validate_session(token)
        if is_valid:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.session_token = token
            wallet_balance = get_wallet_balance(username)
            st.session_state.wallet_balance = (
                wallet_balance if wallet_balance is not None else INITIAL_BALANCE
            )
            return True

    return False


def require_login() -> bool:
    """Ensure user is logged in. Redirect to login if not.

    Call at the top of every protected page.
    """
    if restore_session():
        return True

    st.error("Session expired or invalid. Please log in again.")
    st.switch_page("pages/login.py")
    return False


def _clear_session_state() -> None:
    """Reset all session-related state."""
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.session_token = None
    st.session_state.wallet_balance = INITIAL_BALANCE
