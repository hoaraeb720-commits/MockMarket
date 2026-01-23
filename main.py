import streamlit as st

pages = [
    st.Page("pages/login.py", title="Login"),
    st.Page("pages/signup.py", title="Sign Up"),
    st.Page("pages/dashboard.py", title="Dashboard"),
]

pg = st.navigation(pages, position="top")
pg.run()
