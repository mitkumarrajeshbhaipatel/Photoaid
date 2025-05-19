from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.services.admin_service import (
    get_dashboard_statistics,
    get_all_reports,
    ban_user_by_id,
    get_unverified_users,
    verify_user_by_id
)
from app.schemas.admin_schema import AdminStatsResponse, ReportResponse
from app.schemas.user import UserOut
from app.models.user import User

router = APIRouter(prefix="/admin_service", tags=["AdminService"])

# ✅ Totally bypass auth — return a fake admin user
def fake_admin_user():
    return User(id="admin-id", email="admin@local")

@router.get("/stats", response_model=AdminStatsResponse)
def admin_stats(db: Session = Depends(get_db), current_user: User = Depends(fake_admin_user)):
    return get_dashboard_statistics(db)

@router.get("/reports", response_model=list[ReportResponse])
def reports(db: Session = Depends(get_db), current_user: User = Depends(fake_admin_user)):
    return get_all_reports(db)

@router.post("/ban/{user_id}")
def ban_user(user_id: str, db: Session = Depends(get_db), current_user: User = Depends(fake_admin_user)):
    return ban_user_by_id(user_id, db)

@router.get("/unverified-users", response_model=list[UserOut])
def list_unverified_users(db: Session = Depends(get_db), current_user: User = Depends(fake_admin_user)):
    return get_unverified_users(db)

@router.post("/verify-user/{user_id}")
def verify_user(user_id: str, db: Session = Depends(get_db), current_user: User = Depends(fake_admin_user)):
    return verify_user_by_id(user_id, db)


'''
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.services.admin_service import (
    get_dashboard_statistics,
    get_all_reports,
    ban_user_by_id,
    get_unverified_users,
    verify_user_by_id
)
from app.schemas.admin_schema import AdminStatsResponse, ReportResponse
from app.schemas.user import UserOut

router = APIRouter(prefix="/admin_service", tags=["AdminService"])

# ✅ Testing override: make everyone an admin inside this router
def verify_admin(current_user=Depends(get_current_user)):
    # For testing only — this forces is_admin=True
    current_user.is_admin = True
    return current_user

@router.get("/stats", response_model=AdminStatsResponse)
def admin_stats(db: Session = Depends(get_db), current_user=Depends(verify_admin)):
    return get_dashboard_statistics(db)

@router.get("/reports", response_model=list[ReportResponse])
def reports(db: Session = Depends(get_db), current_user=Depends(verify_admin)):
    return get_all_reports(db)

@router.post("/ban/{user_id}")
def ban_user(user_id: str, db: Session = Depends(get_db), current_user=Depends(verify_admin)):
    return ban_user_by_id(user_id, db)

@router.get("/unverified-users", response_model=list[UserOut])
def list_unverified_users(db: Session = Depends(get_db), current_user=Depends(verify_admin)):
    return get_unverified_users(db)

@router.post("/verify-user/{user_id}")
def verify_user(user_id: str, db: Session = Depends(get_db), current_user=Depends(verify_admin)):
    return verify_user_by_id(user_id, db)
'''