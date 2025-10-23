"""
User model and authentication
"""

from enum import Enum
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserRole(str, Enum):
    """
    User role enumeration - 4-tier permission system
    - citizen: 市民 (一般用戶，可發表意見)
    - government_staff: 行政人員 (政府相關人員，可審核與合併意見)
    - moderator: 版主 (版面管理員)
    - admin: 管理員 (系統管理員，最高權限)
    """
    CITIZEN = "citizen"
    GOVERNMENT_STAFF = "government_staff"
    MODERATOR = "moderator"
    ADMIN = "admin"


class UserBase(BaseModel):
    """Base user model"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=100)
    role: UserRole = UserRole.CITIZEN


class UserCreate(UserBase):
    """User creation model"""
    password: str = Field(..., min_length=6)


class UserUpdate(BaseModel):
    """User update model"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None


class User(UserBase):
    """Complete user model"""
    id: int
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserInDB(User):
    """User model with password hash"""
    password_hash: str


class UserLogin(BaseModel):
    """User login model"""
    username: str
    password: str


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload data"""
    user_id: Optional[int] = None
    username: Optional[str] = None
    role: Optional[UserRole] = None
