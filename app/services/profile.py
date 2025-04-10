from sqlalchemy.orm import Session
from app.models.profile import UserProfile
from app.schemas.profile import UserProfileCreate, UserProfileUpdate

def create_user_profile(db: Session, profile: UserProfileCreate):
    db_profile = UserProfile(**profile.dict())
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
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
    return profile

def delete_user_profile(db: Session, user_id: str):
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        return None
    db.delete(profile)
    db.commit()
    return True
