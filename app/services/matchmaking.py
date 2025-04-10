from sqlalchemy.orm import Session
from app.models.matchmaking import MatchRequest
from app.schemas.matchmaking import MatchRequestCreate, MatchRequestUpdate
import uuid
import datetime

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

def respond_to_match(db: Session, match_id: str, update_data: MatchRequestUpdate):
    match_request = db.query(MatchRequest).filter(MatchRequest.match_id == match_id).first()
    if not match_request:
        return None
    match_request.status = update_data.status
    match_request.accepted_at = datetime.datetime.utcnow()
    db.commit()
    db.refresh(match_request)
    return match_request

def get_user_matches(db: Session, user_id: str):
    return db.query(MatchRequest).filter(
        (MatchRequest.requester_id == user_id) | (MatchRequest.receiver_id == user_id)
    ).all()
