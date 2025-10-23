"""
Authentication API routes
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional
from models.user import User, UserCreate, UserLogin, Token
from services.auth_service import AuthService
from utils.security import get_user_from_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    """Dependency to get current user from JWT token"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    user_data = get_user_from_token(token)
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return user_data


@router.post("/register", response_model=User, status_code=201)
async def register(user_data: UserCreate):
    """Register a new user"""
    user = AuthService.create_user(user_data)

    if not user:
        raise HTTPException(
            status_code=400,
            detail="Username or email already exists"
        )

    return user


@router.post("/login", response_model=Token)
async def login(login_data: UserLogin):
    """Login user and get JWT token"""
    token = AuthService.login(login_data)

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password"
        )

    return token


@router.get("/me", response_model=User)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    user = AuthService.get_user_by_id(current_user["user_id"])

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user
