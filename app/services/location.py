from sqlalchemy.orm import Session
from app.models.location import UserLocation
from app.schemas.location import LocationCreate
from app.utils.geolocation import calculate_distance
from app.models.profile import UserProfile  
from app.schemas.profile import UserProfileOut  
import datetime
from app.utils.distance import calculate_distance
from typing import List


def update_user_location(db: Session, location: LocationCreate):
    db_location = db.query(UserLocation).filter(UserLocation.user_id == location.user_id).first()
    if db_location:
        db_location.latitude = location.latitude
        db_location.longitude = location.longitude
        db_location.updated_at = datetime.datetime.utcnow()
    else:
        db_location = UserLocation(
            user_id=location.user_id,
            latitude=location.latitude,
            longitude=location.longitude,
            updated_at=datetime.datetime.utcnow()
        )
        db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location


'''

def get_nearby_users(db: Session, user_id: str, radius_km: float) -> List[dict]:
    user_location = db.query(UserLocation).filter(UserLocation.user_id == user_id).first()
    if not user_location:
        return []

    nearby_users = []
    other_users = db.query(UserLocation).filter(UserLocation.user_id != user_id).all()

    for other_user in other_users:
        distance = calculate_distance(
            user_location.latitude, user_location.longitude,
            other_user.latitude, other_user.longitude
        )
        if distance <= radius_km:
            profile = db.query(UserProfile).filter(UserProfile.user_id == other_user.user_id).first()

            nearby_users.append({
                "user_id": other_user.user_id,
                "latitude": other_user.latitude,
                "longitude": other_user.longitude,
                "profile": {
                    "name": profile.name if profile else None,
                    "bio": profile.bio if profile else None,
                    "avatar_url": profile.avatar_url if profile else None,
                    "country": profile.country if profile and profile.country else None,  # ✅ add country always
                    "trust_badges": profile.trust_badges if profile else [],
                    "total_sessions": profile.total_sessions if profile else 0,
                    "average_rating": profile.average_rating if profile else 0.0,
                    "verification_status": profile.verification_status if profile else "pending",
                }
            })

    return nearby_users
'''
def get_nearby_users(db: Session, user_id: str, radius_km: float) -> List[dict]:
    user_location = db.query(UserLocation).filter(UserLocation.user_id == user_id).first()
    if not user_location:
        return []

    now = datetime.datetime.utcnow()
    recent_threshold = now - datetime.timedelta(minutes=5)

    nearby_users = []
    other_users = db.query(UserLocation).filter(
        UserLocation.user_id != user_id,
        UserLocation.updated_at >= recent_threshold
    ).all()

    for other_user in other_users:
        profile = db.query(UserProfile).filter(
            UserProfile.user_id == other_user.user_id,
            UserProfile.is_available == True
        ).first()

        if not profile:
            continue  # skip if user is not available or profile not found

        distance = calculate_distance(
            user_location.latitude, user_location.longitude,
            other_user.latitude, other_user.longitude
        )

        if distance <= radius_km:
            nearby_users.append({
                "user_id": other_user.user_id,
                "latitude": other_user.latitude,
                "longitude": other_user.longitude,
                "profile": {
                    "name": profile.name,
                    "bio": profile.bio,
                    "avatar_url": profile.avatar_url,
                    "country": profile.country,
                    "trust_badges": profile.trust_badges,
                    "total_sessions": profile.total_sessions,
                    "average_rating": profile.average_rating,
                    "verification_status": profile.verification_status,
                }
            })

    return nearby_users
