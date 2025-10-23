"""Comment model"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class CommentBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000)


class CommentCreate(CommentBase):
    pass


class Comment(CommentBase):
    id: int
    opinion_id: int
    user_id: int
    is_deleted: bool = False
    deleted_by: Optional[int] = None
    deleted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    username: Optional[str] = None

    class Config:
        from_attributes = True
