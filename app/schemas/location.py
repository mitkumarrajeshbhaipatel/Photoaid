from pydantic import BaseModel, Field
from datetime import datetime

class LocationCreate(BaseModel):
    user_id: str
    latitude: float = Field(..., ge=-90, le=90, description="Latitude must be between -90 and 90")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude must be between -180 and 180")

class LocationOut(LocationCreate):
    updated_at: datetime

    class Config:
        orm_mode = True
