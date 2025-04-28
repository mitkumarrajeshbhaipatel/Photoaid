from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class LocationCreate(BaseModel):
    user_id: str
    latitude: float = Field(..., ge=-90, le=90, description="Latitude must be between -90 and 90")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude must be between -180 and 180")

class LocationOut(LocationCreate):
    updated_at: datetime

    class Config:
        orm_mode = True


class ProfileForNearbyUser(BaseModel):
    name : Optional[str] = None 
    bio: Optional[str]
    avatar_url: Optional[str] = None 
    country: Optional[str]
    trust_badges: list[str] = []
    total_sessions: int = 0
    average_rating: float = 0.0
    verification_status: str = "pending"

    class Config:
        orm_mode = True

class NearbyUserOut(BaseModel):
    user_id: str
    latitude: float
    longitude: float
    updated_at: Optional[datetime] = None
    profile: Optional[ProfileForNearbyUser] = None

    class Config:
        orm_mode = True