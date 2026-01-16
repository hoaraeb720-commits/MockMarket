import streamlit as st

pages = [
    st.Page("pages/login.py", title="Login"),
    st.Page("pages/signup.py", title="Sign Up"),
]

pg = st.navigation(pages, position="top")
pg.run()
