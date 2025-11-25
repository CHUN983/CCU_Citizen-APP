"""Opinion history/audit log model"""
from enum import Enum
from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel


class ActionType(str, Enum):
    CREATED = "created"
    UPDATED = "updated"
    APPROVED = "approved"
    REJECTED = "rejected"
    MERGED = "merged"
    STATUS_CHANGED = "status_changed"


class OpinionHistoryItem(BaseModel):
    id: int
    opinion_id: int
    opinion_title: Optional[str] = None
    user_id: int
    username: Optional[str] = None
    action: ActionType
    old_status: Optional[str] = None
    new_status: Optional[str] = None
    changes: Optional[Any] = None
    created_at: datetime

class OpinionHistoryList(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[OpinionHistoryItem]
