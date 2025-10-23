"""Opinion history/audit log model"""
from enum import Enum
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel


class ActionType(str, Enum):
    CREATED = "created"
    UPDATED = "updated"
    APPROVED = "approved"
    REJECTED = "rejected"
    MERGED = "merged"
    STATUS_CHANGED = "status_changed"


class OpinionHistoryCreate(BaseModel):
    opinion_id: int
    user_id: int
    action: ActionType
    old_status: Optional[str] = None
    new_status: Optional[str] = None
    changes: Optional[Dict[str, Any]] = None


class OpinionHistory(OpinionHistoryCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
