"""Collection/Bookmark model"""
from datetime import datetime
from pydantic import BaseModel


class Collection(BaseModel):
    id: int
    opinion_id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True
