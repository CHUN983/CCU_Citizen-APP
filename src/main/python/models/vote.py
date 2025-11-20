"""Vote model"""
from enum import Enum
from datetime import datetime
from pydantic import BaseModel


class VoteType(str, Enum):
    LIKE = "like"
    DISLIKE = "support"


class VoteCreate(BaseModel):
    vote_type: VoteType = VoteType.LIKE


class Vote(BaseModel):
    id: int
    opinion_id: int
    user_id: int
    vote_type: VoteType
    created_at: datetime

    class Config:
        from_attributes = True

class VoteStats(BaseModel):
    opinion_id: int
    like_count: int
    support_count: int