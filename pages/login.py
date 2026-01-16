import streamlit as st

st.header("Welcome to MockMarket")


with st.form("my_form"):
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    # Every form must have a submit button.
    submitted = st.form_submit_button("Submit")
    if submitted:
        st.write(f"Welcome, {username}!")
