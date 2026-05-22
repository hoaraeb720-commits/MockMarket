"""Session management for persistent login across page refreshes using MongoDB."""

import uuid
from datetime import datetime, timedelta
import streamlit as st
from connections import create_mongodb_connection

SESSION_TIMEOUT_HOURS = 1


@st.cache_resource
def _get_sessions_collection():
    """Get the sessions collection from MongoDB."""
    client = create_mongodb_connection()
    db = client["mockmarket"]
    sessions_collection = db["sessions"]
    
    # Create TTL index to automatically delete expired sessions
    sessions_collection.create_index(
        "created_at",
        expireAfterSeconds=SESSION_TIMEOUT_HOURS * 3600
    )
    
    return sessions_collection


def _cleanup_expired_sessions():
    """Remove expired sessions from storage (MongoDB handles this via TTL index)."""
    sessions_collection = _get_sessions_collection()
    # MongoDB TTL index automatically handles cleanup, but we can manually delete if needed
    cutoff_time = datetime.now() - timedelta(hours=SESSION_TIMEOUT_HOURS)
    sessions_collection.delete_many({"created_at": {"$lt": cutoff_time}})


def create_session(username: str) -> str:
    """Create a new session token for a user.
    
    Args:
        username: The username to create a session for
        
    Returns:
        Session token (UUID)
    """
    sessions_collection = _get_sessions_collection()
    token = str(uuid.uuid4())
    
    sessions_collection.insert_one({
        "token": token,
        "username": username,
        "created_at": datetime.now(),
        "wallet_balance": 10000,
    })
    
    return token


def validate_session(token: str) -> tuple[bool, str | None]:
    """Validate a session token.
    
    Args:
        token: The session token to validate
        
    Returns:
        Tuple of (is_valid, username)
    """
    sessions_collection = _get_sessions_collection()
    session = sessions_collection.find_one({"token": token})
    
    if session:
        created_at = session["created_at"]
        if datetime.now() - created_at <= timedelta(hours=SESSION_TIMEOUT_HOURS):
            return True, session["username"]
    
    return False, None


def get_session_data(token: str) -> dict | None:
    """Get session data including wallet balance.
    
    Args:
        token: The session token
        
    Returns:
        Session data dict or None if invalid
    """
    is_valid, username = validate_session(token)
    if is_valid:
        sessions_collection = _get_sessions_collection()
        session = sessions_collection.find_one({"token": token})
        if session:
            # Convert MongoDB ObjectId to string for JSON serialization
            session.pop("_id", None)
            return session
    return None


def update_session_data(token: str, **kwargs):
    """Update session data.
    
    Args:
        token: The session token
        **kwargs: Fields to update (e.g., wallet_balance=5000)
    """
    sessions_collection = _get_sessions_collection()
    sessions_collection.update_one({"token": token}, {"$set": kwargs})


def logout_session(token: str):
    """Clear a session token.
    
    Args:
        token: The session token to clear
    """
    sessions_collection = _get_sessions_collection()
    sessions_collection.delete_one({"token": token})
