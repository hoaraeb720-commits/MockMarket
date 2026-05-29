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
    """Check password against bcrypt hash. Returns True/False only."""
    # BUG 7 FIX: No longer performs migration here (avoids wrong-document update
    # when two users share the same legacy hash). Migration is done in verify_user
    # where the username is in scope.
    try:
        if bcrypt.checkpw(password.encode(), stored_hash.encode()):
            return True
    except (ValueError, TypeError):
        pass

    # Fallback check for legacy SHA-256
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest() == stored_hash


def _migrate_to_bcrypt(username: str, password: str) -> None:
    """Re-hash a verified password with bcrypt and persist."""
    username = username.strip().lower()
    users = _get_collection("users")
    users.update_one(
        {"username": username},
        {"$set": {"password_hash": hash_password(password)}},
    )


def create_user(username: str, password: str) -> tuple[bool, str]:
    """Create a new user in MongoDB."""
    username = username.strip().lower()
    users = _get_collection("users")

    if users.find_one({"username": username}):
        return False, "Username already exists. Please choose a different one."

    password_hash = hash_password(password)
    users.insert_one({"username": username, "password_hash": password_hash})
    return True, "Account created successfully!"


def verify_user(username: str, password: str) -> tuple[bool, str]:
    """Verify user credentials in MongoDB."""
    username = username.strip().lower()
    users = _get_collection("users")

    user_doc = users.find_one({"username": username})
    if user_doc is None:
        return False, "Username not found."

    if not verify_password(password, user_doc["password_hash"]):
        return False, "Incorrect password."

    # BUG 7 FIX: Auto-migrate legacy SHA-256 hashes to bcrypt using username
    # as the filter, so only the correct document is updated.
    if not user_doc["password_hash"].startswith("$2"):
        _migrate_to_bcrypt(username, password)

    return True, "Login successful!"


# ============================================================================
# Wallet Management
# ============================================================================


def create_wallet(username: str, initial_funds: float = 10000) -> bool:
    """
    Create a wallet for a new user in MongoDB.

    Returns:
        True if successful, False otherwise
    """
    username = username.strip().lower()
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
    username = username.strip().lower()
    wallets = _get_collection("user_wallets")

    wallet_doc = wallets.find_one({"username": username})
    return wallet_doc["current_funds"] if wallet_doc else None


def update_wallet_balance(username: str, new_balance: float) -> bool:
    """
    Update wallet balance for a user in MongoDB.

    Returns:
        True if successful, False otherwise
    """
    username = username.strip().lower()
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
    username = username.strip().lower()
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
    log_transaction(username, "BUY", stock_ticker, stock_quantity, stock_price)
    return True


def log_transaction(
    username: str,
    kind: str,
    ticker: str,
    quantity: int,
    price: float,
    profit_loss: float | None = None,
) -> None:
    """Append a buy/sell entry to the user's transaction history.

    `kind` is "BUY" or "SELL". `profit_loss` is only meaningful for sells.
    """
    username = username.strip().lower()
    txns = _get_collection("transactions")
    txns.insert_one(
        {
            "username": username,
            "kind": kind,
            "stock_ticker": ticker,
            "stock_quantity": quantity,
            "stock_price": price,
            "profit_loss": profit_loss,
            "at": datetime.now(),
        }
    )


def get_recent_transactions(username: str, limit: int = 8) -> list[dict]:
    """Return the most recent transactions (buys + sells) for a user.

    Falls back to portfolio entries when the transactions log is empty so
    legacy holdings (created before the log existed) still appear.
    """
    username = username.strip().lower()
    txns = _get_collection("transactions")
    rows = list(txns.find({"username": username}).sort("at", -1).limit(limit))
    if rows:
        return rows

    # Fallback: synthesize BUY entries from the user's portfolio
    portfolio = _get_collection("user_portfolio")
    cursor = portfolio.find({"username": username}).sort("bought_at", -1).limit(limit)
    return [
        {
            "kind": "BUY",
            "stock_ticker": p["stock_ticker"],
            "stock_quantity": p["stock_quantity"],
            "stock_price": p["stock_price"],
            "at": p.get("bought_at"),
            "profit_loss": None,
        }
        for p in cursor
    ]


def get_user_portfolio(username: str) -> list[dict]:
    """
    Get all stocks in a user's portfolio from MongoDB.

    Returns:
        List of dictionaries with stock info
    """
    username = username.strip().lower()
    portfolio = _get_collection("user_portfolio")

    cursor = portfolio.find({"username": username}).sort("bought_at", -1)
    return [doc for doc in cursor]


def remove_from_portfolio(username: str, ticker: str, quantity_to_remove: int) -> bool:
    """Remove shares using FIFO logic (oldest purchases first) in MongoDB.

    NOTE: This function is not race-safe. Two concurrent sells may both pass
    the total_available check. Acceptable for a single-user simulator;
    requires a MongoDB transaction or atomic compare-and-swap for production.

    Returns:
        True if successful, False if not enough shares.
    """
    username = username.strip().lower()
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
    username = username.strip().lower()
    wallet_funds = get_wallet_balance(username)
    if wallet_funds is None:
        wallet_funds = 0.0

    portfolio = _get_collection("user_portfolio")
    user_portfolio_data = list(portfolio.find({"username": username}))
    # BUG 6 FIX: Wrap price lookup in try/except so a delisted or bad ticker
    # doesn't crash the leaderboard for all users. Treat bad tickers as $0.
    stock_value = 0.0
    for doc in user_portfolio_data:
        try:
            price = get_current_stock_price(ticker=doc["stock_ticker"])
        except Exception:
            price = 0.0
        stock_value += price * doc["stock_quantity"]
    return stock_value + wallet_funds


def get_all_users_net_worth() -> list[dict]:
    users = _get_collection("users")
    wallets = _get_collection("user_wallets")
    portfolios = _get_collection("user_portfolio")

    user_docs = list(users.find())
    # Collect all unique tickers
    all_portfolio_docs = list(portfolios.find())
    unique_tickers = {doc["stock_ticker"] for doc in all_portfolio_docs}

    # Fetch prices once per unique ticker (with error tolerance)
    price_map = {}
    for ticker in unique_tickers:
        try:
            price_map[ticker] = get_current_stock_price(ticker)
        except Exception:
            price_map[ticker] = 0.0

    # Build wallet map
    wallet_map = {
        w["username"]: w.get("current_funds", 0.0)
        for w in wallets.find()
    }

    # Group portfolio by username
    portfolio_by_user: dict[str, list[dict]] = {}
    for doc in all_portfolio_docs:
        portfolio_by_user.setdefault(doc["username"], []).append(doc)

    result = []
    for user in user_docs:
        username = user["username"]
        wallet_funds = wallet_map.get(username, 0.0)
        stock_value = sum(
            price_map.get(doc["stock_ticker"], 0.0) * doc["stock_quantity"]
            for doc in portfolio_by_user.get(username, [])
        )
        result.append({"username": username, "net_worth": stock_value + wallet_funds})
    return result


def get_aggregated_portfolio(username: str) -> dict[str, dict]:
    """Get portfolio grouped by ticker with summed quantities and average price."""
    username = username.strip().lower()
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
