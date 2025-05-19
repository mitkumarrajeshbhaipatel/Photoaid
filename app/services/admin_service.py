from sqlalchemy.orm import Session
from app.models.user import User
from app.models.profile import UserProfile
from app.models.session import Session as PhotoSession
from app.models.report import Report
from app.models.review import Review
from app.models.matchmaking import MatchRequest
from app.models.chat import Message
from app.schemas.admin_schema import AdminStatsResponse
from app.schemas.report import ReportResponse
from app.schemas.user import UserOut
from datetime import datetime

def get_dashboard_statistics(db: Session) -> AdminStatsResponse:
    users = db.query(User).all()
    sessions = db.query(PhotoSession).all()
    reports = db.query(Report).all()
    reviews = db.query(Review).all()
    match_requests = db.query(MatchRequest).all()
    messages = db.query(Message).all()

    verified_users = [u for u in users if u.is_verified]
    banned_users = [u for u in users if u.is_banned]
    active_sessions = [s for s in sessions if s.status == "created"]
    completed_sessions = [s for s in sessions if s.status == "completed"]
    unresolved_reports = [r for r in reports if not r.resolved]
    average_trust = sum(r.rating for r in reviews) / len(reviews) if reviews else 0

    return AdminStatsResponse(
        total_users=len(users),
        total_verified_users=len(verified_users),
        total_banned_users=len(banned_users),
        total_sessions=len(sessions),
        active_sessions=len(active_sessions),
        completed_sessions=len(completed_sessions),
        total_reports=len(reports),
        unresolved_reports=len(unresolved_reports),
        total_reviews=len(reviews),
        average_trust_score=round(average_trust, 2),
        match_requests_sent=len(match_requests),
        match_requests_received=len(match_requests),
        total_messages_sent=len(messages)
    )

def get_all_reports(db: Session) -> list[ReportResponse]:
    reports = db.query(Report).all()
    return [
        ReportResponse(
            user_id=r.target_user_id,
            reported_by=r.reporter_id,
            reason=r.reason,
            timestamp=r.timestamp
        )
        for r in reports
    ]

def ban_user_by_id(user_id: str, db: Session):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError("User not found")
    user.is_banned = True
    db.commit()
    return {"user_id": user_id, "status": "banned"}

def get_unverified_users(db: Session) -> list[UserOut]:
    users = db.query(User).filter(User.is_verified == False).all()
    return users

def verify_user_by_id(user_id: str, db: Session):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError("User not found")
    user.is_verified = True
    db.commit()
    return {"user_id": user_id, "status": "verified"}
