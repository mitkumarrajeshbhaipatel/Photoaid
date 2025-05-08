from sqlalchemy.orm import Session
from app.models.profile import UserProfile
from app.models.user import User
from app.schemas.profile import UserProfileCreate, UserProfileUpdate
from fastapi import APIRouter, Depends, HTTPException

from app.schemas.notification import NotificationCreate
from app.services.notification import create_notification


def create_user_profile(db: Session, profile: UserProfileCreate):
    # First check if the user exists
    user = db.query(User).filter(User.id == profile.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if profile already exists for this user
    existing_profile = db.query(UserProfile).filter(UserProfile.user_id == profile.user_id).first()
    if existing_profile:
        raise HTTPException(status_code=400, detail="Profile already exists for this user")

    # If everything is okay, create the profile
    db_profile = UserProfile(**profile.dict())
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)


    notification = NotificationCreate(
        user_id=profile.user_id,
        title="Profile Created",
        message="Your user profile was successfully created.",
        notification_type="system"
    )
    create_notification(db, notification)

    return db_profile

def get_user_profile(db: Session, user_id: str):
    return db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

def update_user_profile(db: Session, user_id: str, profile_update: UserProfileUpdate):
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        return None
    for key, value in profile_update.dict(exclude_unset=True).items():
        setattr(profile, key, value)
    db.commit()
    db.refresh(profile)
    
    notification = NotificationCreate(
        user_id=user_id,
        title="Profile Updated",
        message="Your profile information was successfully updated.",
        notification_type="system"
    )
    create_notification(db, notification)

    return profile

def delete_user_profile(db: Session, user_id: str):
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        return None
    db.delete(profile)
    db.commit()
    return True
