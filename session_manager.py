"""Session management for persistent login across page refreshes."""

import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path

SESSION_FILE = Path(".sessions.json")
SESSION_TIMEOUT_HOURS = 24


def _load_sessions() -> dict:
    """Load all sessions from file."""
    if SESSION_FILE.exists():
        with open(SESSION_FILE, "r") as f:
            return json.load(f)
    return {}


def _save_sessions(sessions: dict):
    """Save sessions to file."""
    with open(SESSION_FILE, "w") as f:
        json.dump(sessions, f, indent=2)


def _cleanup_expired_sessions():
    """Remove expired sessions from storage."""
    sessions = _load_sessions()
    current_time = datetime.now()
    
    expired_keys = []
    for token, data in sessions.items():
        created_at = datetime.fromisoformat(data["created_at"])
        if current_time - created_at > timedelta(hours=SESSION_TIMEOUT_HOURS):
            expired_keys.append(token)
    
    for token in expired_keys:
        del sessions[token]
    
    if expired_keys:
        _save_sessions(sessions)


def create_session(username: str) -> str:
    """Create a new session token for a user.
    
    Args:
        username: The username to create a session for
        
    Returns:
        Session token (UUID)
    """
    _cleanup_expired_sessions()
    sessions = _load_sessions()
    
    token = str(uuid.uuid4())
    sessions[token] = {
        "username": username,
        "created_at": datetime.now().isoformat(),
        "wallet_balance": 10000,
    }
    
    _save_sessions(sessions)
    return token


def validate_session(token: str) -> tuple[bool, str | None]:
    """Validate a session token.
    
    Args:
        token: The session token to validate
        
    Returns:
        Tuple of (is_valid, username)
    """
    _cleanup_expired_sessions()
    sessions = _load_sessions()
    
    if token in sessions:
        data = sessions[token]
        created_at = datetime.fromisoformat(data["created_at"])
        if datetime.now() - created_at <= timedelta(hours=SESSION_TIMEOUT_HOURS):
            return True, data["username"]
    
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
        sessions = _load_sessions()
        return sessions.get(token)
    return None


def update_session_data(token: str, **kwargs):
    """Update session data.
    
    Args:
        token: The session token
        **kwargs: Fields to update (e.g., wallet_balance=5000)
    """
    sessions = _load_sessions()
    if token in sessions:
        sessions[token].update(kwargs)
        _save_sessions(sessions)


def logout_session(token: str):
    """Clear a session token.
    
    Args:
        token: The session token to clear
    """
    sessions = _load_sessions()
    if token in sessions:
        del sessions[token]
        _save_sessions(sessions)
