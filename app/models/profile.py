from sqlalchemy import Column, String, Float, Integer, Text, Boolean
from sqlalchemy.types import JSON
from app.database import Base

class UserProfile(Base):
    __tablename__ = "user_profiles"

    user_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=True)
    is_available = Column(Boolean, default=False) 
    bio = Column(Text, nullable=True)
    avatar_url = Column(String, nullable=True)
    country = Column(String, nullable=True)
    trust_badges = Column(JSON, default=[])  # store list as JSON
    total_sessions = Column(Integer, default=0)
    average_rating = Column(Float, default=0.0)
    verification_status = Column(String, default="pending")  # pending, verified, rejected
