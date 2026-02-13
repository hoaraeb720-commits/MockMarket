import sqlite3
import hashlib
from datetime import datetime


DATABASE_PATH = "mockmarket.db"


def get_connection():
    """Get a connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE_PATH)
    return conn


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
    Create a new user in the database.
    Returns (success, message) tuple.
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        password_hash = hash_password(password)
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, password_hash),
        )
        conn.commit()
        return True, "Account created successfully!"
    except sqlite3.IntegrityError:
        return False, "Username already exists. Please choose a different one."
    finally:
        conn.close()


def verify_user(username: str, password: str) -> tuple[bool, str]:
    """
    Verify user credentials.
    Returns (success, message) tuple.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()

    if result is None:
        return False, "Username not found."

    password_hash = hash_password(password)
    if result[0] == password_hash:
        return True, "Login successful!"
    else:
        return False, "Incorrect password."


# ============================================================================
# Wallet Management
# ============================================================================


def create_wallet(username: str, initial_funds: float = 10000) -> bool:
    """
    Create a wallet for a new user.

    Returns:
        True if successful, False otherwise
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO user_wallets (username, current_funds) VALUES (?, ?)",
            (username, initial_funds),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def get_wallet_balance(username: str) -> float | None:
    """
    Get the current wallet balance for a user.

    Returns:
        Current funds or None if user not found
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT current_funds FROM user_wallets WHERE username = ?", (username,)
    )
    result = cursor.fetchone()
    conn.close()

    return result[0] if result else None


def update_wallet_balance(username: str, new_balance: float) -> bool:
    """
    Update wallet balance for a user.

    Returns:
        True if successful, False otherwise
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "UPDATE user_wallets SET current_funds = ? WHERE username = ?",
            (new_balance, username),
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def deduct_from_wallet(username: str, amount: float) -> bool:
    """
    Deduct funds from a user's wallet.

    Returns:
        True if successful, False if insufficient funds
    """
    balance = get_wallet_balance(username)
    if balance is None or balance < amount:
        return False
    return update_wallet_balance(username, balance - amount)


def add_to_wallet(username: str, amount: float) -> bool:
    """
    Add funds to a user's wallet.

    Returns:
        True if successful, False otherwise
    """
    balance = get_wallet_balance(username)
    if balance is None:
        return False
    return update_wallet_balance(username, balance + amount)


# ============================================================================
# Portfolio Management
# ============================================================================


def add_stock_to_portfolio(
    username: str, stock_ticker: str, stock_price: float, stock_quantity: int
) -> bool:
    """
    Add a stock purchase to the user's portfolio.

    Returns:
        True if successful, False otherwise
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """INSERT INTO user_portfolio 
               (username, stock_ticker, stock_price, stock_quantity, bought_at) 
               VALUES (?, ?, ?, ?, ?)""",
            (username, stock_ticker, stock_price, stock_quantity, datetime.now()),
        )
        conn.commit()
        return True
    finally:
        conn.close()


def get_user_portfolio(username: str) -> list[dict]:
    """
    Get all stocks in a user's portfolio.

    Returns:
        List of dictionaries with stock info
    """
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        """SELECT id, stock_ticker, stock_price, stock_quantity, bought_at 
           FROM user_portfolio WHERE username = ? ORDER BY bought_at DESC""",
        (username,),
    )
    results = cursor.fetchall()
    conn.close()

    return [dict(row) for row in results]


def get_portfolio_by_ticker(username: str, stock_ticker: str) -> list[dict]:
    """
    Get all holdings of a specific stock for a user.

    Returns:
        List of dictionaries with stock info
    """
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        """SELECT id, stock_ticker, stock_price, stock_quantity, bought_at 
           FROM user_portfolio 
           WHERE username = ? AND stock_ticker = ? 
           ORDER BY bought_at ASC""",
        (username, stock_ticker),
    )
    results = cursor.fetchall()
    conn.close()

    return [dict(row) for row in results]


def remove_from_portfolio(portfolio_id: int, quantity_to_remove: int) -> bool:
    """
    Remove or reduce quantity from a portfolio entry.
    If quantity matches, delete the entry. Otherwise, reduce the quantity.

    Returns:
        True if successful, False otherwise

    @TODO: implement FIFO logic for selling stocks (currently just reduces quantity from the specified entry)
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Get current quantity
        cursor.execute(
            "SELECT stock_quantity FROM user_portfolio WHERE id = ?", (portfolio_id,)
        )
        result = cursor.fetchone()

        if not result:
            return False

        current_quantity = result[0]

        if quantity_to_remove >= current_quantity:
            # Delete the entry
            cursor.execute("DELETE FROM user_portfolio WHERE id = ?", (portfolio_id,))
        else:
            # Reduce quantity
            new_quantity = current_quantity - quantity_to_remove
            cursor.execute(
                "UPDATE user_portfolio SET stock_quantity = ? WHERE id = ?",
                (new_quantity, portfolio_id),
            )

        conn.commit()
        return True
    finally:
        conn.close()


def delete_portfolio_entry(portfolio_id: int) -> bool:
    """
    Delete a portfolio entry completely.

    Returns:
        True if successful, False otherwise
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM user_portfolio WHERE id = ?", (portfolio_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


# Initialize the database when this module is imported
init_db()
