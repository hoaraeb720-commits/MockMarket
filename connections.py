from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import streamlit as st

@st.cache_resource
def create_mongodb_connection():
    username = st.secrets["mongodb"]["USERNAME"]
    password = st.secrets["mongodb"]["PASSWORD"]
    uri = f"mongodb+srv://{username}:{password}@mock-market-cluster.wkndkr1.mongodb.net/?appName=mock-market-cluster"
    client = MongoClient(uri, server_api=ServerApi("1"))
    try:
        client.admin.command("ping")
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)
    return client
