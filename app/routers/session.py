from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession
from app.dependencies import get_db, get_current_user
from app.schemas.session import SessionCreate, SessionUpdateStatus, SessionOut
from app.services.session import create_session, update_session_status, get_session_by_match_id
from app.models.user import User
from app.models.session import Session

router = APIRouter(prefix="/sessions", tags=["Session Management"])


@router.post("/create", response_model=SessionOut)
def create_new_session(
    session_data: SessionCreate,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user)  
):
    return create_session(db, session_data)

@router.post("/update-status/{session_id}", response_model=SessionOut)
def update_status(
    session_id: str,
    status_update: SessionUpdateStatus,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session = update_session_status(db, session_id, status_update, current_user)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@router.get("/by-match/{match_id}", response_model=SessionOut)
def get_by_match(match_id: str, db: DBSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    session = db.query(Session).filter(Session.match_id == match_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Check if the current user is authorized to access the session (requester or helper)
    if session.requester_id != current_user.id and session.helper_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to view this session")

    return session
