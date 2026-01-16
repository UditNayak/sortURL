"""Authentication service for user management."""
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from fastapi import Request, HTTPException, status

from src.database import get_db_connection
from src.utils.password import hash_password, verify_password
from src.utils.jwt_handler import verify_token
from src.models.schemas import UserSignup, UserLogin
from src.config import settings


def create_user(user_data: UserSignup) -> Dict[str, Any]:
    """Create a new user.
    
    Args:
        user_data: User signup data
        
    Returns:
        Created user information
        
    Raises:
        HTTPException: If email already exists
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Check if email already exists
        cursor.execute("SELECT id FROM users WHERE email = ?", (user_data.email,))
        if cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create user
        user_id = str(uuid.uuid4())
        password_hash = hash_password(user_data.password)
        created_at = datetime.now(timezone.utc).isoformat()
        
        cursor.execute(
            "INSERT INTO users (id, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
            (user_id, user_data.email, password_hash, created_at)
        )
        
        conn.commit()
        
        return {
            "id": user_id,
            "email": user_data.email,
            "created_at": created_at
        }


def authenticate_user(user_data: UserLogin) -> Dict[str, Any]:
    """Authenticate a user.
    
    Args:
        user_data: User login credentials
        
    Returns:
        User information if authenticated
        
    Raises:
        HTTPException: If credentials are invalid
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, email, password_hash, created_at FROM users WHERE email = ?",
            (user_data.email,)
        )
        user = cursor.fetchone()
        
        if not user or not verify_password(user_data.password, user['password_hash']):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        return {
            "id": user['id'],
            "email": user['email'],
            "created_at": user['created_at']
        }


def get_current_user(request: Request) -> Optional[Dict[str, Any]]:
    """Get current authenticated user from request.
    
    Args:
        request: FastAPI request object
        
    Returns:
        User information if authenticated, None otherwise
    """
    token = request.cookies.get(settings.COOKIE_NAME)
    if not token:
        return None
    
    payload = verify_token(token)
    if not payload:
        return None
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, email, created_at FROM users WHERE id = ?",
            (payload.get("sub"),)
        )
        user = cursor.fetchone()
        
        if user:
            return dict(user)
    
    return None