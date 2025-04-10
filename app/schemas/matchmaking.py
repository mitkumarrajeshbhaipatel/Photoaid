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
