from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.schemas.location import LocationCreate, LocationOut
from app.services.location import update_user_location, get_nearby_users
from typing import List

router = APIRouter(prefix="/location", tags=["Location"])

@router.post("/update", response_model=LocationOut)
def update_location(location: LocationCreate, db: Session = Depends(get_db)):
    return update_user_location(db, location)

@router.get("/nearby/{user_id}", response_model=List[LocationOut])
def get_nearby(user_id: str, radius_km: float = 5, db: Session = Depends(get_db)):
    return get_nearby_users(db, user_id, radius_km)
