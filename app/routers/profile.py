# app/routers/profile.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.schemas.profile import UserProfileCreate, UserProfileOut, UserProfileUpdate
from app.services.profile import create_user_profile, get_user_profile, update_user_profile, delete_user_profile
from app.models.user import User

router = APIRouter(prefix="/profiles", tags=["Profiles"])

@router.post("/", response_model=UserProfileOut)
def create_profile(profile: UserProfileCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if profile.user_id != current_user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot create profile for another user")
    return create_user_profile(db, profile)

@router.get("/{user_id}", response_model=UserProfileOut)
def read_profile(user_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this profile")
    
    profile = get_user_profile(db, user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

@router.put("/{user_id}", response_model=UserProfileOut)
def update_profile(user_id: str, profile_update: UserProfileUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this profile")
    
    updated_profile = update_user_profile(db, user_id, profile_update)
    if not updated_profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return updated_profile

@router.delete("/{user_id}")
def delete_profile(user_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this profile")
    
    success = delete_user_profile(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Profile not found")
    return {"message": "Profile deleted successfully"}