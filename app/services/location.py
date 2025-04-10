from sqlalchemy.orm import Session
from app.models.location import UserLocation
from app.schemas.location import LocationCreate
from app.utils.geolocation import calculate_distance
import datetime

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

def get_nearby_users(db: Session, user_id: str, radius_km: float):
    user = db.query(UserLocation).filter(UserLocation.user_id == user_id).first()
    if not user:
        return []

    nearby_users = []
    users = db.query(UserLocation).filter(UserLocation.user_id != user_id).all()

    for other_user in users:
        distance = calculate_distance(user.latitude, user.longitude, other_user.latitude, other_user.longitude)
        if distance <= radius_km:
            nearby_users.append(other_user)

    return nearby_users
