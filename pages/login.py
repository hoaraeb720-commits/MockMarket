import streamlit as st
from database import verify_user
from session_manager import create_session

st.header("Welcome to MockMarket")

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.session_token = None

# Redirect if already logged in
if st.session_state.logged_in:
    st.rerun()

with st.form("login_form"):
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    submitted = st.form_submit_button("Login")

    if submitted:
        if not username or not password:
            st.error("Please fill in all fields.")
        else:
            success, message = verify_user(username, password)
            if success:
                # Create persistent session token
                token = create_session(username)
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.session_token = token
                st.success(message)
                # Add token to URL so it persists across refreshes
                st.query_params["session_token"] = token
                st.rerun()
            else:
                st.error(message)

st.divider()
st.write("Don't have an account?")
if st.button("Sign Up"):
    st.switch_page("pages/signup.py")
