"""Notification model"""
from enum import Enum
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class NotificationType(str, Enum):
    COMMENT = "comment"
    STATUS_CHANGE = "status_change"
    MERGED = "merged"
    APPROVED = "approved"
    REJECTED = "rejected"


class NotificationCreate(BaseModel):
    user_id: int
    opinion_id: Optional[int] = None
    type: NotificationType
    title: str = Field(..., max_length=200)
    content: Optional[str] = None


class Notification(NotificationCreate):
    id: int
    is_read: bool = False
    created_at: datetime

    class Config:
        from_attributes = True
