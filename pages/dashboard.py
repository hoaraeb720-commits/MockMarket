import streamlit as st

# Check if user is logged in
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in to access this page.")
    if st.button("Go to Login"):
        st.switch_page("pages/login.py")
else:
    st.header(f"Hello, {st.session_state.username}! 👋")
    st.write("Welcome to your MockMarket dashboard.")

    st.divider()

    if st.button("Log Out"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.success("You have been logged out.")
        st.switch_page("pages/login.py")
