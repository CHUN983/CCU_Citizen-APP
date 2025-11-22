"""
Opinion API routes
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List
from ..models.opinion import Opinion, OpinionCreate, OpinionList, OpinionStatus, OpinionWithUser
from ..models.comment import Comment, CommentCreate
from ..models.vote import VoteCreate
from ..services.opinion_service import OpinionService
from ..api.auth import get_current_user

router = APIRouter(prefix="/opinions", tags=["Opinions"])


@router.post("", response_model=Opinion, status_code=201)
async def create_opinion(
    opinion_data: OpinionCreate,
    current_user: dict = Depends(get_current_user)
):
    print("DEBUG opinion_data:", opinion_data)
    print("DEBUG current_user:", current_user)
    """Create a new opinion"""
    opinion = OpinionService.create_opinion(current_user["user_id"], opinion_data)

    if not opinion:
        raise HTTPException(status_code=400, detail="Failed to create opinion")

    return opinion


@router.get("", response_model=OpinionList)
async def get_opinions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[OpinionStatus] = None,
    category_id: Optional[int] = None
):
    """Get paginated list of opinions"""
    return OpinionService.get_opinions(page, page_size, status, category_id)

#固定路徑要放在參數路徑前面，否則會被當成參數處理
@router.get("/collect", response_model=OpinionList)
async def get_bookmarked_opinions(
    page: int = Query(1, ge=1),
    page_size: int = Query(5, ge=1, le=50),
    current_user: dict = Depends(get_current_user)
):
    """Get paginated list of opinions bookmarked by current user"""
    return OpinionService.get_bookmarked_opinions(
        user_id=current_user["user_id"],
        page=page,
        page_size=page_size
    )

@router.get("/{opinion_id}", response_model=OpinionWithUser)
async def get_opinion(opinion_id: int):
    """Get opinion by ID"""
    opinion = OpinionService.get_opinion_by_id(opinion_id, increment_view=True)

    if not opinion:
        raise HTTPException(status_code=404, detail="Opinion not found")

    print("DEBUG opinion:", opinion)
    return opinion


@router.post("/{opinion_id}/comments", response_model=Comment, status_code=201)
async def add_comment(
    opinion_id: int,
    comment_data: CommentCreate,
    current_user: dict = Depends(get_current_user)
):
    """Add a comment to an opinion"""
    # Check if opinion exists
    opinion = OpinionService.get_opinion_by_id(opinion_id)
    if not opinion:
        raise HTTPException(status_code=404, detail="Opinion not found")

    comment = OpinionService.add_comment(opinion_id, current_user["user_id"], comment_data)

    if not comment:
        raise HTTPException(status_code=400, detail="Failed to add comment")

    return comment

@router.get("/{opinion_id}/comments", response_model=List[Comment])
async def get_comments(
    opinion_id: int,
    limit: int = Query(50, ge=1, le=500)
):
    """Get comments for an opinion with limit"""

    # Check if opinion exists
    opinion = OpinionService.get_opinion_by_id(opinion_id)
    if not opinion:
        raise HTTPException(status_code=404, detail="Opinion not found")

    comments = OpinionService.get_comments_by_opinion_id(opinion_id, limit)

    return comments

@router.post("/{opinion_id}/vote", status_code=200)
async def vote_opinion(
    opinion_id: int,
    vote_data: VoteCreate,
    current_user: dict = Depends(get_current_user)
):
    print("DEBUG vote_data:", vote_data)
    """Vote on an opinion"""
    # Check if opinion exists
    opinion = OpinionService.get_opinion_by_id(opinion_id)
    if not opinion:
        raise HTTPException(status_code=404, detail="Opinion not found")

    success = OpinionService.vote_opinion(opinion_id, current_user["user_id"], vote_data)

    if not success:
        raise HTTPException(status_code=400, detail="Failed to vote")

    return {"message": "Vote recorded successfully"}




@router.post("/{opinion_id}/collect", status_code=200)
async def collect_opinion(
    opinion_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Add opinion to collection"""
    # Check if opinion exists
    opinion = OpinionService.get_opinion_by_id(opinion_id)
    if not opinion:
        raise HTTPException(status_code=404, detail="Opinion not found")

    success = OpinionService.collect_opinion(opinion_id, current_user["user_id"])

    if not success:
        raise HTTPException(status_code=400, detail="Failed to collect opinion")

    return {"message": "Opinion collected successfully"}

@router.get("/{opinion_id}/collect")
async def get_collect_status(
    opinion_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Check if current user has collected this opinion"""
    # 確認意見存在
    opinion = OpinionService.get_opinion_by_id(opinion_id)
    if not opinion:
        raise HTTPException(status_code=404, detail="Opinion not found")

    is_collected = OpinionService.is_collected(opinion_id, current_user["user_id"])
    return {"is_collected": is_collected}

@router.delete("/{opinion_id}/collect", status_code=200)
async def uncollect_opinion(
    opinion_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Remove opinion from collection"""
    success = OpinionService.uncollect_opinion(opinion_id, current_user["user_id"])

    if not success:
        raise HTTPException(status_code=404, detail="Collection not found")

    return {"message": "Opinion removed from collection"}
