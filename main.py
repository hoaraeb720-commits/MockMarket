import streamlit as st

# Initialize session state for authentication
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None

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
