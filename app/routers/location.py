from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.schemas.location import LocationCreate, LocationOut
from app.services.location import update_user_location, get_nearby_users
from typing import List
from app.models.user import User

router = APIRouter(prefix="/location", tags=["Location"])
'''
@router.post("/update", response_model=LocationOut)
def update_location(location: LocationCreate, db: Session = Depends(get_db)):
    return update_user_location(db, location)

@router.get("/nearby/{user_id}", response_model=List[LocationOut])
def get_nearby(user_id: str, radius_km: float = 5, db: Session = Depends(get_db)):
    return get_nearby_users(db, user_id, radius_km)
'''
@router.post("/update", response_model=LocationOut)
def update_location(
    location: LocationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Only allow user to update their own location
    if location.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this location")
    return update_user_location(db, location)

@router.get("/nearby/{user_id}", response_model=List[LocationOut])
def get_nearby(
    user_id: str,
    radius_km: float = Query(5, gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Optionally, we could check if user_id == current_user.id
    return get_nearby_users(db, user_id, radius_km)
