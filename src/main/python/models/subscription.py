"""Subscription model"""
from datetime import datetime
from pydantic import BaseModel


class Subscription(BaseModel):
    id: int
    user_id: int
    opinion_id: int
    created_at: datetime

    class Config:
        from_attributes = True
