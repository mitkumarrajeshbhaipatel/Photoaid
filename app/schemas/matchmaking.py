'''

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MatchRequestCreate(BaseModel):
    requester_id: str
    receiver_id: str

class MatchRequestUpdate(BaseModel):
    status: str  # accepted or declined

class MatchRequestOut(BaseModel):
    match_id: str
    requester_id: str
    receiver_id: str
    status: str
    created_at: datetime
    accepted_at: Optional[datetime]

    class Config:
        orm_mode = True
'''

# src/schemas/matchmaking.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MatchRequestCreate(BaseModel):
    requester_id: str
    receiver_id: str  # ✅ Now required at creation
    request_type: str  # ✅ Photo or Video
    distance: str      # ✅ like '100m', '500m', etc.
    details: Optional[str] = None
    latitude: float
    longitude: float

class MatchRequestUpdate(BaseModel):
    status: str  # accepted | declined

class MatchRequestOut(BaseModel):
    match_id: str
    requester_id: str
    receiver_id: str
    request_type: str
    distance: str
    details: Optional[str]
    latitude: float
    longitude: float
    status: str
    created_at: datetime
    accepted_at: Optional[datetime]

    class Config:
        orm_mode = True
