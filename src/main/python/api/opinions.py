"""
Opinion API routes
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from models.opinion import Opinion, OpinionCreate, OpinionList, OpinionStatus
from models.comment import Comment, CommentCreate
from models.vote import VoteCreate
from services.opinion_service import OpinionService
from api.auth import get_current_user

router = APIRouter(prefix="/opinions", tags=["Opinions"])


@router.post("", response_model=Opinion, status_code=201)
async def create_opinion(
    opinion_data: OpinionCreate,
    current_user: dict = Depends(get_current_user)
):
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


@router.get("/{opinion_id}", response_model=Opinion)
async def get_opinion(opinion_id: int):
    """Get opinion by ID"""
    opinion = OpinionService.get_opinion_by_id(opinion_id, increment_view=True)

    if not opinion:
        raise HTTPException(status_code=404, detail="Opinion not found")

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


@router.post("/{opinion_id}/vote", status_code=200)
async def vote_opinion(
    opinion_id: int,
    vote_data: VoteCreate,
    current_user: dict = Depends(get_current_user)
):
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
