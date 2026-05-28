import streamlit as st
from auth_helper import restore_session

restore_session()

if st.session_state.logged_in:
    pages = [
        st.Page("pages/dashboard.py", title="Dashboard"),
        st.Page("pages/leaderboard.py", title="Leaderboard"),
        st.Page("pages/predict.py", title="Make a Prediction"),
        st.Page("pages/monte_carlo.py", title="Monte Carlo Simulation"),
    ]
else:
    pages = [
        st.Page("pages/login.py", title="Login"),
        st.Page("pages/signup.py", title="Sign Up"),
        st.Page("pages/landing.py", title="Landing"),
    ]

pg = st.navigation(pages, position="top")
pg.run()
