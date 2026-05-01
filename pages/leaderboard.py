# generate leaderboard page gathering data from mongodb and displaying it in a table and ranking off of
# net worth
import streamlit as st
from database import get_all_users_net_worth

def display_leaderboard():
    st.title("Leaderboard")
    st.write("Top users by net worth")

    net_worth_data = get_all_users_net_worth()
    sorted_data = sorted(net_worth_data, key=lambda x: x["net_worth"], reverse=True)

    for rank, user in enumerate(sorted_data, start=1):
        st.write(f"{rank}. {user['username']} - Net Worth: ${user['net_worth']:.2f}")


display_leaderboard()
