"""
Security utilities for authentication and authorization
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Optional
import bcrypt
import jwt
from jwt.exceptions import PyJWTError

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))  # 24 hours


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt

    Args:
        password: Plain text password

    Returns:
        Hashed password string
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash

    Args:
        plain_password: Plain text password
        hashed_password: Hashed password to verify against

    Returns:
        True if password matches, False otherwise
    """
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token

    Args:
        data: Data to encode in the token
        expires_delta: Token expiration time

    Returns:
        JWT token string
    """
    to_encode = data.copy()

    # python 3.12 before
    # datatime.utcnow() <==> datetime.now(timezone.utc)
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and verify a JWT access token

    Args:
        token: JWT token string

    Returns:
        Decoded token data or None if invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except PyJWTError:
        return None


def get_user_from_token(token: str) -> Optional[dict]:
    """
    Extract user information from JWT token

    Args:
        token: JWT token string

    Returns:
        User data dictionary or None if invalid
    """
    payload = decode_access_token(token)
    if payload is None:
        return None

    user_id: int = payload.get("user_id")
    username: str = payload.get("username")
    role: str = payload.get("role")

    if user_id is None or username is None:
        return None

    return {
        "user_id": user_id,
        "username": username,
        "role": role
    }


# Permission dependencies
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Get current authenticated user from JWT token
    Required for all protected endpoints
    """
    from ..models.user import User
    from ..utils.database import get_db_connection

    token = credentials.credentials
    user_data = get_user_from_token(token)

    if user_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get full user data from database
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT * FROM users WHERE id = %s AND is_active = TRUE",
            (user_data["user_id"],)
        )
        user_row = cursor.fetchone()

        if not user_row:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )

        return User(**user_row)

    finally:
        cursor.close()
        conn.close()


async def get_current_active_user(current_user = Depends(get_current_user)):
    """
    Get current active user
    Alias for get_current_user for compatibility
    """
    return current_user


async def require_admin(current_user = Depends(get_current_user)):
    """
    Require admin role
    Use this dependency for admin-only endpoints
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user


async def require_moderator(current_user = Depends(get_current_user)):
    """
    Require moderator or admin role
    Use this dependency for moderation endpoints
    """
    if current_user.role not in ["admin", "moderator", "government_staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Moderator or admin privileges required"
        )
    return current_user


async def require_government_staff(current_user = Depends(get_current_user)):
    """
    Require government staff, moderator, or admin role
    Use this dependency for government staff endpoints
    """
    if current_user.role not in ["admin", "moderator", "government_staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Government staff privileges required"
        )
    return current_user


def check_permission(user_role: str, required_roles: list) -> bool:
    """
    Check if user role has required permissions

    Args:
        user_role: User's current role
        required_roles: List of roles that are allowed

    Returns:
        True if user has permission, False otherwise
    """
    return user_role in required_roles
