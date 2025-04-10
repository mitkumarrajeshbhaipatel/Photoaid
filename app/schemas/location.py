from pydantic import BaseModel
from datetime import datetime

class LocationCreate(BaseModel):
    user_id: str
    latitude: float
    longitude: float

class LocationOut(LocationCreate):
    updated_at: datetime

    class Config:
        orm_mode = True
