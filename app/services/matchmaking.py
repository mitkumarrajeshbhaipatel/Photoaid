from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from app.models.matchmaking import MatchRequest
from app.schemas.matchmaking import MatchRequestCreate, MatchRequestUpdate
import uuid
import datetime
from fastapi import HTTPException

from app.schemas.session import SessionCreate
from app.services.session import create_session

def create_match_request(db: Session, match_data: MatchRequestCreate):
    match_request = MatchRequest(
        match_id=str(uuid.uuid4()),
        requester_id=match_data.requester_id,
        receiver_id=match_data.receiver_id,
        request_type=match_data.request_type,  
        distance=match_data.distance,          
        details=match_data.details,            
        latitude=match_data.latitude,          
        longitude=match_data.longitude,        
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
    if update_data.status not in ["accepted", "declined", "cancel", "expired"]:
        raise HTTPException(status_code=400, detail="Invalid status. Must be 'accepted' or 'declined'.")

    match_request.status = update_data.status
    match_request.accepted_at = datetime.datetime.utcnow()

    db.commit()
    db.refresh(match_request)

    # ✅ If accepted, create a session
    if update_data.status == "accepted":
        # Ensure location fields are available
        if not match_request.latitude or not match_request.longitude:
            raise HTTPException(status_code=400, detail="Match location is missing, cannot create session.")

        session_data = SessionCreate(
            requester_id=match_request.requester_id,
            helper_id=match_request.receiver_id,
            match_id=match_request.match_id,
            location={"lat": match_request.latitude, "lng": match_request.longitude}
        )
        create_session(db, session_data)


    return match_request

'''
def get_user_matches(db: Session, user_id: str):
    return db.query(MatchRequest).filter(
        ((MatchRequest.requester_id == user_id) | (MatchRequest.receiver_id == user_id)) &
        (MatchRequest.status == "pending" or MatchRequest.status == "accepted")
    ).all()
'''

def get_user_matches(db: Session, user_id: str):

    cutoff_time = datetime.datetime.utcnow() - datetime.timedelta(minutes=30)

    return db.query(MatchRequest).filter(
        and_(
            or_(
                MatchRequest.requester_id == user_id,
                MatchRequest.receiver_id == user_id
            ),
            or_(
                MatchRequest.status == "pending",
                MatchRequest.status == "accepted"
            ),
            MatchRequest.created_at >= cutoff_time 
        )
    ).all()