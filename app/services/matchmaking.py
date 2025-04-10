from sqlalchemy.orm import Session
from app.models.matchmaking import MatchRequest
from app.schemas.matchmaking import MatchRequestCreate, MatchRequestUpdate
import uuid
import datetime
from fastapi import HTTPException

def create_match_request(db: Session, match_data: MatchRequestCreate):
    match_request = MatchRequest(
        match_id=str(uuid.uuid4()),
        requester_id=match_data.requester_id,
        receiver_id=match_data.receiver_id,
        status="pending",
        created_at=datetime.datetime.utcnow()
    )
    db.add(match_request)
    db.commit()
    db.refresh(match_request)
    return match_request

def respond_to_match(db: Session, match_id: str, update_data: MatchRequestUpdate, current_user):
    match_request = db.query(MatchRequest).filter(MatchRequest.match_id == match_id).first()

    if not match_request:
        return None

    # Check authorization
    if match_request.receiver_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not allowed to respond to this match.")

    # Check if already accepted or rejected
    if match_request.status != "pending":
        raise HTTPException(status_code=409, detail="This match has already been responded to.")

    # 🚨 Here is the new fix:
    if update_data.status not in ["accepted", "rejected"]:
        raise HTTPException(status_code=400, detail="Invalid status. Must be 'accepted' or 'rejected'.")

    match_request.status = update_data.status
    match_request.accepted_at = datetime.datetime.utcnow()

    db.commit()
    db.refresh(match_request)

    return match_request

def get_user_matches(db: Session, user_id: str):
    return db.query(MatchRequest).filter(
        (MatchRequest.requester_id == user_id) | (MatchRequest.receiver_id == user_id)
    ).all()
