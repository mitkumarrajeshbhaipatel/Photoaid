from pydantic import BaseModel
from typing import Optional, List

class UserProfileBase(BaseModel):
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    country: Optional[str] = None
    trust_badges: List[str] = []
    total_sessions: int = 0
    average_rating: float = 0.0
    verification_status: str = "pending"

class UserProfileCreate(UserProfileBase):
    user_id: str

class UserProfileUpdate(UserProfileBase):
    pass

class UserProfileOut(UserProfileBase):
    user_id: str

    class Config:
        orm_mode = True
