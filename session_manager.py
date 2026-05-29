"""Session management for persistent login across page refreshes using MongoDB."""

import uuid
from datetime import datetime, timedelta
import streamlit as st
from connections import create_mongodb_connection

SESSION_TIMEOUT_HOURS = 24


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


def logout_session(token: str):
    """Clear a session token.
    
    Args:
        token: The session token to clear
    """
    sessions_collection = _get_sessions_collection()
    sessions_collection.delete_one({"token": token})
