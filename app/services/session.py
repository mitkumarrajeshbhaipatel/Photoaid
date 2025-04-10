from sqlalchemy.orm import Session as DBSession
from app.models.session import Session
from app.schemas.session import SessionCreate, SessionUpdateStatus
import uuid
import datetime

def create_session(db: DBSession, session_data: SessionCreate):
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

def update_session_status(db: DBSession, session_id: str, status_update: SessionUpdateStatus):
    session = db.query(Session).filter(Session.session_id == session_id).first()
    if not session:
        return None
    session.status = status_update.status

    if status_update.status == "started":
        session.check_in_time = datetime.datetime.utcnow()
    elif status_update.status == "completed":
        session.check_out_time = datetime.datetime.utcnow()

    db.commit()
    db.refresh(session)
    return session

def get_session_by_match_id(db: DBSession, match_id: str):
    return db.query(Session).filter(Session.match_id == match_id).first()
