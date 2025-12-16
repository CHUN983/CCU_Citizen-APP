"""
Notification API routes
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List
from models.notification import Notification
from services.notification_service import NotificationService
from api.auth import get_current_user

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=List[Notification])
async def get_notifications(
    unread_only: bool = False,
    current_user: dict = Depends(get_current_user)
):
    """Get user's notifications"""
    return NotificationService.get_user_notifications(
        current_user["user_id"],
        unread_only
    )


@router.post("/{notification_id}/read", status_code=200)
async def mark_notification_read(
    notification_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Mark notification as read"""
    success = NotificationService.mark_as_read(notification_id, current_user["user_id"])

    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")

    return {"message": "Notification marked as read"}
