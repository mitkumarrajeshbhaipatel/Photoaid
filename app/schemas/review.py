from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ReviewCreate(BaseModel):
    session_id: str
    reviewer_id: str
    target_user_id: str
    rating: int
    comment: Optional[str] = None

class ReviewOut(BaseModel):
    review_id: str
    session_id: str
    reviewer_id: str
    target_user_id: str
    rating: int
    comment: Optional[str]
    submitted_at: datetime

    class Config:
        orm_mode = True

class BadgeOut(BaseModel):
    user_id: str
    badge_type: str
    awarded_at: datetime

    class Config:
        orm_mode = True
