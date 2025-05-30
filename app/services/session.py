from sqlalchemy.orm import Session as DBSession
from app.models.session import Session
from app.schemas.session import SessionCreate, SessionUpdateStatus
import uuid
import datetime
from fastapi import HTTPException
from app.models.user import User
from app.models.matchmaking import MatchRequest

from app.schemas.notification import NotificationCreate
from app.services.notification import create_notification

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

    for uid, role in [(session_data.requester_id, "Requester"), (session_data.helper_id, "Helper")]:
        notification = NotificationCreate(
            user_id=uid,
            title="New Session Created",
            message=f"You have been added as a {role.lower()} in a new session.",
            notification_type="session"
        )
        create_notification(db, notification)

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
    if status_update.status not in ["started", "completed", "cancelled"]:
        raise HTTPException(status_code=400, detail="Invalid session status update.")

    if status_update.status == "started":
        session.check_in_time = datetime.datetime.utcnow()
    elif status_update.status == "completed":
        session.check_out_time = datetime.datetime.utcnow()

    session.status = status_update.status

    db.commit()
    db.refresh(session)

    for uid in [session.requester_id, session.helper_id]:
        notification = NotificationCreate(
            user_id=uid,
            title="Session Updated",
            message=f"The session was marked as {status_update.status}.",
            notification_type="session"
        )
        create_notification(db, notification)
    return session



'''

def get_session_by_match_id(db: DBSession, match_id: str):
    allowed_statuses = ["created", "started", "completed", "cancelled"]
    return db.query(Session).filter(
        Session.match_id == match_id,
        Session.status.in_(allowed_statuses)
    ).first()

    #return db.query(Session).filter(Session.match_id == match_id).first()
'''
def get_session_by_match_id(db: DBSession, match_id: str):
    allowed_statuses = ["created", "started"]

    # Get current time and threshold
    now = datetime.datetime.utcnow()
    cutoff = now - datetime.timedelta(days=1)

    # Fetch active or recent sessions only
    return db.query(Session).filter(
        Session.match_id == match_id,
        (
            or_( (Session.status.in_(allowed_statuses)) ,

                and_(
                    (Session.status.in_(["completed", "cancelled"])) ,
                    (Session.updated_at >= cutoff)
                )
            )
        )
    ).first()
