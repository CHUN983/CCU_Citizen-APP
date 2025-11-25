"""
Moderation API routes (admin only)
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from services.moderation_service import ModerationService
from models.user import UserRole
from api.auth import get_current_user
from models.opinion_history import OpinionHistoryList

router = APIRouter(prefix="/admin", tags=["Moderation"])


def require_moderator(current_user: dict = Depends(get_current_user)) -> dict:
    """Dependency to require moderator or admin role"""
    if current_user["role"] not in [UserRole.ADMIN.value, UserRole.MODERATOR.value]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return current_user


class RejectRequest(BaseModel):
    reason: str = ""


class MergeRequest(BaseModel):
    target_id: int


class UpdateCategoryRequest(BaseModel):
    category_id: int

@router.get("/dashboard/stats", status_code=200)
async def get_dashboard_stats(
    moderator: dict = Depends(require_moderator)
):
    """Get dashboard statistics"""
    stats = ModerationService.get_dashboard_stats()
    return stats

@router.post("/opinions/{opinion_id}/approve", status_code=200)
async def approve_opinion(
    opinion_id: int,
    moderator: dict = Depends(require_moderator)
):
    """Approve an opinion"""
    success = ModerationService.approve_opinion(opinion_id, moderator["user_id"])

    if not success:
        raise HTTPException(status_code=400, detail="Failed to approve opinion")

    return {"message": "Opinion approved successfully"}


@router.post("/opinions/{opinion_id}/reject", status_code=200)
async def reject_opinion(
    opinion_id: int,
    request: RejectRequest,
    moderator: dict = Depends(require_moderator)
):
    
    """Reject an opinion"""
    success = ModerationService.reject_opinion(
        opinion_id, moderator["user_id"], request.reason
    )

    if not success:
        raise HTTPException(status_code=400, detail="Failed to reject opinion")

    return {"message": "Opinion rejected successfully"}


@router.post("/opinions/{opinion_id}/merge", status_code=200)
async def merge_opinions(
    opinion_id: int,
    request: MergeRequest,
    moderator: dict = Depends(require_moderator)
):
    """Merge opinion into another"""
    success = ModerationService.merge_opinions(
        opinion_id, request.target_id, moderator["user_id"]
    )

    if not success:
        raise HTTPException(status_code=400, detail="Failed to merge opinions")

    return {"message": "Opinions merged successfully"}


@router.delete("/comments/{comment_id}", status_code=200)
async def delete_comment(
    comment_id: int,
    moderator: dict = Depends(require_moderator)
):
    """Delete a comment"""
    success = ModerationService.delete_comment(comment_id, moderator["user_id"])

    if not success:
        raise HTTPException(status_code=404, detail="Comment not found")

    return {"message": "Comment deleted successfully"}


@router.put("/opinions/{opinion_id}/category", status_code=200)
async def update_opinion_category(
    opinion_id: int,
    request: UpdateCategoryRequest,
    moderator: dict = Depends(require_moderator)
):
    """Update opinion category"""
    success = ModerationService.update_opinion_category(
        opinion_id, request.category_id, moderator["user_id"]
    )

    if not success:
        raise HTTPException(status_code=400, detail="Failed to update category")

    return {"message": "Category updated successfully"}


@router.get("/history", response_model=OpinionHistoryList)
def get_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    opinion_id: Optional[int] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    moderator: dict = Depends(require_moderator)
) -> OpinionHistoryList:
    """Get moderation history with optional filters"""
    total = ModerationService.get_moderation_history(
        page=page,
        page_size=page_size,
        opinion_id=opinion_id,
        start_time=start_time,
        end_time=end_time
    )

    return total
    