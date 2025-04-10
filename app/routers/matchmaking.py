from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.schemas.matchmaking import MatchRequestCreate, MatchRequestUpdate, MatchRequestOut
from app.services.matchmaking import create_match_request, respond_to_match, get_user_matches
from typing import List
from app.models.user import User

router = APIRouter(prefix="/matchmaking", tags=["Matchmaking"])

@router.post("/request", response_model=MatchRequestOut)
def create_request(
    match_data: MatchRequestCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)  
):
    if match_data.requester_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only create matches for yourself.")
    return create_match_request(db, match_data)


@router.post("/respond/{match_id}", response_model=MatchRequestOut)
def respond(
    match_id: str,
    update_data: MatchRequestUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)  # ✅
):
    match = respond_to_match(db, match_id, update_data, current_user)  # ✅ pass user
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    return match



@router.get("/my-matches/{user_id}", response_model=List[MatchRequestOut])
def my_matches(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden to access others' matches")
    return get_user_matches(db, user_id)