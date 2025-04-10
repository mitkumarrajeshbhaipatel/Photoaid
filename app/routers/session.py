from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from app.dependencies import get_db
from app.schemas.session import SessionCreate, SessionUpdateStatus, SessionOut
from app.services.session import create_session, update_session_status, get_session_by_match_id

router = APIRouter(prefix="/sessions", tags=["Session Management"])

@router.post("/create", response_model=SessionOut)
def create_new_session(session_data: SessionCreate, db: DBSession = Depends(get_db)):
    return create_session(db, session_data)

@router.post("/update-status/{session_id}", response_model=SessionOut)
def update_status(session_id: str, status_update: SessionUpdateStatus, db: DBSession = Depends(get_db)):
    session = update_session_status(db, session_id, status_update)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@router.get("/by-match/{match_id}", response_model=SessionOut)
def get_by_match(match_id: str, db: DBSession = Depends(get_db)):
    session = get_session_by_match_id(db, match_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session
