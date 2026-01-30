import streamlit as st
from database import create_user

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
                # Automatically log in the user
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error(message)

st.divider()
st.write("Already have an account?")
if st.button("Login"):
    st.switch_page("pages/login.py")
