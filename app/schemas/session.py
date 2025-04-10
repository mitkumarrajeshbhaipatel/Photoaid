from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime
from enum import Enum

class SessionStatusEnum(str, Enum):
    created = "created"
    started = "started"
    completed = "completed"
    cancelled = "cancelled"

class SessionUpdateStatus(BaseModel):
    status: SessionStatusEnum


class SessionCreate(BaseModel):
    requester_id: str
    helper_id: str
    match_id: str
    location: Dict[str, float]  # {"lat": float, "lng": float}


class SessionOut(BaseModel):
    session_id: str
    requester_id: str
    helper_id: str
    match_id: str
    status: str
    location: Dict[str, float]
    check_in_time: Optional[datetime]
    check_out_time: Optional[datetime]
    created_at: datetime

    class Config:
        orm_mode = True
