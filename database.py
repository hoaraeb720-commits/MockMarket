import bcrypt
from datetime import datetime

from ticker import get_current_stock_price
from connections import create_mongodb_connection


def _get_collection(name: str):
    """Return a MongoDB collection from the mockmarket database."""
    client = create_mongodb_connection()
    db = client["mockmarket"]
    return db[name]


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify a password against a stored hash.

    Supports bcrypt hashes and auto-migrates legacy SHA-256 hashes.
    """
    # Try bcrypt first
    try:
        if bcrypt.checkpw(password.encode(), stored_hash.encode()):
            return True
    except (ValueError, TypeError):
        pass

    # Fallback: check legacy SHA-256 hash
    import hashlib
    sha256_hash = hashlib.sha256(password.encode()).hexdigest()
    if sha256_hash == stored_hash:
        # Auto-migrate to bcrypt
        new_hash = hash_password(password)
        users = _get_collection("users")
        users.update_one(
            {"password_hash": stored_hash},
            {"$set": {"password_hash": new_hash}},
        )
        return True

    return False


def create_user(username: str, password: str) -> tuple[bool, str]:
    """Create a new user in MongoDB."""
    users = _get_collection("users")

    if users.find_one({"username": username}):
        return False, "Username already exists. Please choose a different one."

    password_hash = hash_password(password)
    users.insert_one({"username": username, "password_hash": password_hash})
    return True, "Account created successfully!"


def verify_user(username: str, password: str) -> tuple[bool, str]:
    """Verify user credentials in MongoDB."""
    users = _get_collection("users")

    user_doc = users.find_one({"username": username})
    if user_doc is None:
        return False, "Username not found."

    if verify_password(password, user_doc["password_hash"]):
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
    wallets = _get_collection("user_wallets")

    if wallets.find_one({"username": username}):
        return False

    wallets.insert_one(
        {"username": username, "current_funds": initial_funds}
    )
    return True


def get_wallet_balance(username: str) -> float | None:
    """
    Get the current wallet balance for a user from MongoDB.

    Returns:
        Current funds or None if user not found
    """
    wallets = _get_collection("user_wallets")

    wallet_doc = wallets.find_one({"username": username})
    return wallet_doc["current_funds"] if wallet_doc else None


def update_wallet_balance(username: str, new_balance: float) -> bool:
    """
    Update wallet balance for a user in MongoDB.

    Returns:
        True if successful, False otherwise
    """
    wallets = _get_collection("user_wallets")

    result = wallets.update_one(
        {"username": username}, {"$set": {"current_funds": new_balance}}
    )
    return result.modified_count > 0


# ============================================================================
# Portfolio Management
# ============================================================================


def add_stock_to_portfolio(
    username: str, stock_ticker: str, stock_price: float, stock_quantity: int
) -> bool:
    """
    Add a stock purchase to the user's portfolio in MongoDB.

    Returns:
        True if successful, False otherwise
    """
    portfolio = _get_collection("user_portfolio")

    portfolio.insert_one(
        {
            "username": username,
            "stock_ticker": stock_ticker,
            "stock_price": stock_price,
            "stock_quantity": stock_quantity,
            "bought_at": datetime.now(),
        }
    )
    return True


def get_user_portfolio(username: str) -> list[dict]:
    """
    Get all stocks in a user's portfolio from MongoDB.

    Returns:
        List of dictionaries with stock info
    """
    portfolio = _get_collection("user_portfolio")

    cursor = portfolio.find({"username": username}).sort("bought_at", -1)
    return [doc for doc in cursor]


def remove_from_portfolio(username: str, ticker: str, quantity_to_remove: int) -> bool:
    """
    Remove shares using FIFO logic (oldest purchases first) in MongoDB.

    Returns:
        True if successful, False if not enough shares.
    """
    portfolio = _get_collection("user_portfolio")

    # Get all purchases for this user + ticker ordered by oldest first
    cursor = portfolio.find(
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
            portfolio.delete_one({"_id": doc["_id"]})
            remaining_to_sell -= stock_quantity
        else:
            # Partially reduce document
            new_quantity = stock_quantity - remaining_to_sell
            portfolio.update_one(
                {"_id": doc["_id"]}, {"$set": {"stock_quantity": new_quantity}}
            )
            remaining_to_sell = 0

    return True


def calculate_net_worth(username: str) -> float:
    wallet_funds = get_wallet_balance(username)
    if wallet_funds is None:
        wallet_funds = 0.0

    portfolio = _get_collection("user_portfolio")
    user_portfolio_data = list(portfolio.find({"username": username}))
    stock_value = sum(
        get_current_stock_price(ticker=doc["stock_ticker"]) * doc["stock_quantity"]
        for doc in user_portfolio_data
    )
    return stock_value + wallet_funds


def get_all_users_net_worth() -> list[dict]:
    users = _get_collection("users")

    all_users = list(users.find())
    net_worth_list = []
    for user in all_users:
        username = user["username"]
        net_worth = calculate_net_worth(username)
        net_worth_list.append({"username": username, "net_worth": net_worth})

    return net_worth_list


def get_aggregated_portfolio(username: str) -> dict[str, dict]:
    """Get portfolio grouped by ticker with summed quantities and average price."""
    raw = get_user_portfolio(username)
    agg: dict[str, dict] = {}
    for stock in raw:
        ticker = stock["stock_ticker"]
        qty = stock["stock_quantity"]
        price = stock["stock_price"]
        if ticker in agg:
            prev_qty = agg[ticker]["quantity"]
            prev_total = agg[ticker]["avg_price"] * prev_qty
            agg[ticker]["quantity"] = prev_qty + qty
            agg[ticker]["avg_price"] = (prev_total + price * qty) / (prev_qty + qty)
        else:
            agg[ticker] = {"quantity": qty, "avg_price": price}
    return agg
