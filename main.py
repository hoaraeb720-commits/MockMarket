import streamlit as st
from auth_helper import restore_session

restore_session()

# Register ALL pages always so URLs always resolve. Each page handles its own
# login-state redirect.
landing = st.Page("pages/landing.py", title="Landing", url_path="landing", default=True)
login = st.Page("pages/login.py", title="Login", url_path="login")
signup = st.Page("pages/signup.py", title="Sign Up", url_path="signup")
dashboard = st.Page("pages/dashboard.py", title="Dashboard", url_path="dashboard")
leaderboard = st.Page("pages/leaderboard.py", title="Leaderboard", url_path="leaderboard")
predict = st.Page("pages/predict.py", title="Make a Prediction", url_path="predict")
monte_carlo = st.Page("pages/monte_carlo.py", title="Monte Carlo Simulation", url_path="monte_carlo")

pages = [landing, login, signup, dashboard, leaderboard, predict, monte_carlo]

pg = st.navigation(pages, position="hidden")
pg.run()
