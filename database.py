import sqlite3
import hashlib
from datetime import datetime

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import streamlit as st

DATABASE_PATH = "mockmarket.db"


def get_connection():
    """Get a connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE_PATH)
    return conn


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


def init_db():
    """Initialize the database and create tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)

    # User Wallet table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_wallets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            current_funds REAL NOT NULL DEFAULT 10000,
            FOREIGN KEY (username) REFERENCES users(username)
        )
    """)

    # User Portfolio table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_portfolio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            stock_ticker TEXT NOT NULL,
            stock_price REAL NOT NULL,
            stock_quantity INTEGER NOT NULL,
            bought_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (username) REFERENCES users(username)
        )
    """)

    conn.commit()
    conn.close()


def hash_password(password: str) -> str:
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def create_user(username: str, password: str) -> tuple[bool, str]:
    """
    Create a new user in MongoDB.
    Returns (success, message) tuple.
    """
    client = create_mongodb_connection()
    db = client["mockmarket"]
    users_collection = db["users"]

    if users_collection.find_one({"username": username}):
        return False, "Username already exists. Please choose a different one."

    password_hash = hash_password(password)
    users_collection.insert_one({"username": username, "password_hash": password_hash})
    return True, "Account created successfully!"


def verify_user(username: str, password: str) -> tuple[bool, str]:
    """
    Verify user credentials in MongoDB.
    Returns (success, message) tuple.
    """
    client = create_mongodb_connection()
    db = client["mockmarket"]
    users_collection = db["users"]

    user_doc = users_collection.find_one({"username": username})
    if user_doc is None:
        return False, "Username not found."

    password_hash = hash_password(password)
    if user_doc["password_hash"] == password_hash:
        return True, "Login successful!"
    else:
        return False, "Incorrect password."


# ============================================================================
# Wallet Management
# ============================================================================


def create_wallet(username: str, initial_funds: float = 10000) -> bool:
    """
    Create a wallet for a new user in MongoDB.

    Returns:
        True if successful, False otherwise
    """
    client = create_mongodb_connection()
    db = client["mockmarket"]
    wallets_collection = db["user_wallets"]

    if wallets_collection.find_one({"username": username}):
        return False

    wallets_collection.insert_one(
        {"username": username, "current_funds": initial_funds}
    )
    return True


def get_wallet_balance(username: str) -> float | None:
    """
    Get the current wallet balance for a user from MongoDB.

    Returns:
        Current funds or None if user not found
    """
    client = create_mongodb_connection()
    db = client["mockmarket"]
    wallets_collection = db["user_wallets"]

    wallet_doc = wallets_collection.find_one({"username": username})
    return wallet_doc["current_funds"] if wallet_doc else None


# def update_wallet_balance(username: str, new_balance: float) -> bool:
#     """
#     Update wallet balance for a user.

#     Returns:
#         True if successful, False otherwise
#     """
#     conn = get_connection()
#     cursor = conn.cursor()

#     try:
#         cursor.execute(
#             "UPDATE user_wallets SET current_funds = ? WHERE username = ?",
#             (new_balance, username),
#         )
#         conn.commit()
#         return cursor.rowcount > 0
#     finally:
#         conn.close()


def update_wallet_balance(username: str, new_balance: float) -> bool:
    """
    Update wallet balance for a user in MongoDB.

    Returns:
        True if successful, False otherwise
    """
    client = create_mongodb_connection()
    db = client["mockmarket"]
    wallets_collection = db["user_wallets"]

    result = wallets_collection.update_one(
        {"username": username}, {"$set": {"current_funds": new_balance}}
    )
    return result.modified_count > 0


# ============================================================================
# Portfolio Management
# ============================================================================


# def add_stock_to_portfolio(
#     username: str, stock_ticker: str, stock_price: float, stock_quantity: int
# ) -> bool:
#     """
#     Add a stock purchase to the user's portfolio.

#     Returns:
#         True if successful, False otherwise
#     """
#     conn = get_connection()
#     cursor = conn.cursor()

#     try:
#         cursor.execute(
#             """INSERT INTO user_portfolio
#                (username, stock_ticker, stock_price, stock_quantity, bought_at)
#                VALUES (?, ?, ?, ?, ?)""",
#             (username, stock_ticker, stock_price, stock_quantity, datetime.now()),
#         )
#         conn.commit()
#         return True
#     finally:
#         conn.close()


def add_stock_to_portfolio(
    username: str, stock_ticker: str, stock_price: float, stock_quantity: int
) -> bool:
    """
    Add a stock purchase to the user's portfolio in MongoDB.

    Returns:
        True if successful, False otherwise
    """
    client = create_mongodb_connection()
    db = client["mockmarket"]
    portfolio_collection = db["user_portfolio"]

    portfolio_collection.insert_one(
        {
            "username": username,
            "stock_ticker": stock_ticker,
            "stock_price": stock_price,
            "stock_quantity": stock_quantity,
            "bought_at": datetime.now(),
        }
    )
    return True


# def get_user_portfolio(username: str) -> list[dict]:
#     """
#     Get all stocks in a user's portfolio.

#     Returns:
#         List of dictionaries with stock info
#     """
#     conn = get_connection()
#     conn.row_factory = sqlite3.Row
#     cursor = conn.cursor()

#     cursor.execute(
#         """SELECT id, stock_ticker, stock_price, stock_quantity, bought_at
#            FROM user_portfolio WHERE username = ? ORDER BY bought_at DESC""",
#         (username,),
#     )
#     results = cursor.fetchall()
#     conn.close()

#     return [dict(row) for row in results]


def get_user_portfolio(username: str) -> list[dict]:
    """
    Get all stocks in a user's portfolio from MongoDB.

    Returns:
        List of dictionaries with stock info
    """
    client = create_mongodb_connection()
    db = client["mockmarket"]
    portfolio_collection = db["user_portfolio"]

    cursor = portfolio_collection.find({"username": username}).sort("bought_at", -1)
    return [doc for doc in cursor]


# def remove_from_portfolio(username: str, ticker: str, quantity_to_remove: int) -> bool:
#     """
#     Remove shares using FIFO logic (oldest purchases first).

#     Returns:
#         True if successful, False if not enough shares.
#     """
#     conn = get_connection()
#     cursor = conn.cursor()

#     try:
#         # Get all purchases for this user + ticker ordered by oldest first
#         cursor.execute(
#             """
#             SELECT id, stock_quantity
#             FROM user_portfolio
#             WHERE username = ? AND stock_ticker = ?
#             ORDER BY id ASC
#             """,
#             (username, ticker),
#         )

#         rows = cursor.fetchall()

#         total_available = sum(row[1] for row in rows)

#         # Not enough shares
#         if quantity_to_remove > total_available:
#             return False

#         remaining_to_sell = quantity_to_remove

#         for portfolio_id, stock_quantity in rows:
#             if remaining_to_sell <= 0:
#                 break

#             if stock_quantity <= remaining_to_sell:
#                 # Sell entire row
#                 cursor.execute(
#                     "DELETE FROM user_portfolio WHERE id = ?",
#                     (portfolio_id,),
#                 )
#                 remaining_to_sell -= stock_quantity
#             else:
#                 # Partially reduce row
#                 new_quantity = stock_quantity - remaining_to_sell
#                 cursor.execute(
#                     "UPDATE user_portfolio SET stock_quantity = ? WHERE id = ?",
#                     (new_quantity, portfolio_id),
#                 )
#                 remaining_to_sell = 0

#         conn.commit()
#         return True

#     except Exception as e:
#         print("Error in FIFO sell:", e)
#         return False

#     finally:
#         conn.close()


def remove_from_portfolio(username: str, ticker: str, quantity_to_remove: int) -> bool:
    """
    Remove shares using FIFO logic (oldest purchases first) in MongoDB.

    Returns:
        True if successful, False if not enough shares.
    """
    client = create_mongodb_connection()
    db = client["mockmarket"]
    portfolio_collection = db["user_portfolio"]

    # Get all purchases for this user + ticker ordered by oldest first
    cursor = portfolio_collection.find(
        {"username": username, "stock_ticker": ticker}
    ).sort("bought_at", 1)

    total_available = sum(doc["stock_quantity"] for doc in cursor)

    # Not enough shares
    if quantity_to_remove > total_available:
        return False

    remaining_to_sell = quantity_to_remove

    cursor.rewind()  # Reset cursor to iterate again

    for doc in cursor:
        if remaining_to_sell <= 0:
            break

        stock_quantity = doc["stock_quantity"]

        if stock_quantity <= remaining_to_sell:
            # Sell entire document
            portfolio_collection.delete_one({"_id": doc["_id"]})
            remaining_to_sell -= stock_quantity
        else:
            # Partially reduce document
            new_quantity = stock_quantity - remaining_to_sell
            portfolio_collection.update_one(
                {"_id": doc["_id"]}, {"$set": {"stock_quantity": new_quantity}}
            )
            remaining_to_sell = 0

    return True


# Initialize the database when this module is imported
init_db()
