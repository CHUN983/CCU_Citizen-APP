"""
Opinion model for citizen submissions
"""

from enum import Enum
from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, Field


class OpinionStatus(str, Enum):
    """Opinion status enumeration"""
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    RESOLVED = "resolved"


class MediaType(str, Enum):
    """Media type enumeration"""
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"


class OpinionMediaBase(BaseModel):
    """Base opinion media model"""
    file_path: str
    file_size: int
    filename: Optional[str] = None
    media_type: MediaType
    mime_type: Optional[str] = None
    url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    
    
    
    


class OpinionMediaCreate(OpinionMediaBase):
    """Opinion media creation model"""
    pass


class OpinionMedia(OpinionMediaBase):
    """Complete opinion media model"""

    id: int
    opinion_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class OpinionBase(BaseModel):
    """Base opinion model"""
    title: str = Field(..., min_length=5, max_length=200)
    content: str = Field(..., min_length=10)
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    region: Optional[str] = Field(None, max_length=100)
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    is_public: bool = True


class OpinionCreate(OpinionBase):
    """Opinion creation model"""
    tags: Optional[List[str]] = []
    media_files: Optional[List[dict]] = []  # List of uploaded media file info
    status: str = "pending"  # Accept string status for easier frontend integration

    media: Optional[List[OpinionMediaCreate]] = None


class OpinionUpdate(BaseModel):
    """Opinion update model"""
    title: Optional[str] = Field(None, min_length=5, max_length=200)
    content: Optional[str] = Field(None, min_length=10)
    category_id: Optional[int] = None
    region: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    status: Optional[OpinionStatus] = None
    is_public: Optional[bool] = None


class Opinion(OpinionBase):
    """Complete opinion model"""
    id: int
    user_id: int
    status: OpinionStatus
    view_count: int = 0
    merged_to_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    # Related data
    media: List[OpinionMedia] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    upvotes: Optional[int] = 0
    downvotes: Optional[int] = 0
    comment_count: Optional[int] = 0

    class Config:
        from_attributes = True


class OpinionWithUser(Opinion):
    """Opinion with user information"""
    username: str
    user_full_name: Optional[str] = None

    media: List[OpinionMedia] = Field(default_factory=list)


class OpinionList(BaseModel):
    """Paginated opinion list"""
    total: int
    page: int
    page_size: int
    items: List[OpinionWithUser]
