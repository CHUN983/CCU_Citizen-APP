"""Tag model"""
from datetime import datetime
from pydantic import BaseModel, Field


class TagBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)


class TagCreate(TagBase):
    pass


class Tag(TagBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class OpinionTag(BaseModel):
    opinion_id: int
    tag_id: int
    created_at: datetime

    class Config:
        from_attributes = True
