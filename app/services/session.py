from sqlalchemy.orm import Session as DBSession
from app.models.session import Session
from app.schemas.session import SessionCreate, SessionUpdateStatus
import uuid
import datetime
from fastapi import HTTPException
from app.models.user import User
from app.models.matchmaking import MatchRequest

def create_session(db: DBSession, session_data: SessionCreate):
    # Check if a session already exists for the same match_id
    existing = db.query(Session).filter(Session.match_id == session_data.match_id).first()
    if existing:
        raise HTTPException(status_code=409, detail="Session already exists for this match")
    
    session = Session(
        session_id=str(uuid.uuid4()),
        requester_id=session_data.requester_id,
        helper_id=session_data.helper_id,
        match_id=session_data.match_id,
        status="created",
        location=session_data.location,
        created_at=datetime.datetime.utcnow()
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session



def update_session_status(db: DBSession, session_id: str, status_update: SessionUpdateStatus, current_user: User):
    session = db.query(Session).filter(Session.session_id == session_id).first()
    if not session:
        return None

    # Check authorization: only requester or helper can update
    if current_user.id not in [session.requester_id, session.helper_id]:
        raise HTTPException(status_code=403, detail="Unauthorized to update session.")

    # Prevent modifying completed/cancelled sessions
    if session.status in ["end", "cancelled"]:
        raise HTTPException(status_code=409, detail="Session already finalized.")

    # Validate status transition
    if status_update.status not in ["started", "completed","end", "cancelled"]:
        raise HTTPException(status_code=400, detail="Invalid session status update.")

    if status_update.status == "started":
        session.check_in_time = datetime.datetime.utcnow()
    elif status_update.status == "completed":
        session.check_out_time = datetime.datetime.utcnow()

    session.status = status_update.status

    db.commit()
    db.refresh(session)
    return session





def get_session_by_match_id(db: DBSession, match_id: str):
    return db.query(Session).filter(Session.match_id == match_id).first()
