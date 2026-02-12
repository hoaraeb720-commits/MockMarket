import streamlit as st
from database import create_user
from session_manager import create_session

st.header("Create an Account")

with st.form("signup_form"):
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    submitted = st.form_submit_button("Sign Up")

    if submitted:
        if not username or not password or not confirm_password:
            st.error("Please fill in all fields.")
        elif password != confirm_password:
            st.error("Passwords do not match. Please try again.")
        else:
            success, message = create_user(username, password)
            if success:
                st.success(message)
                # Create persistent session token
                token = create_session(username)
                # Automatically log in the user
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.session_token = token
                # Add token to URL so it persists across refreshes
                st.query_params["session_token"] = token
                st.rerun()
            else:
                st.error(message)

st.divider()
st.write("Already have an account?")
if st.button("Login"):
    st.switch_page("pages/login.py")

