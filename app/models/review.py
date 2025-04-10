from sqlalchemy import Column, String, Integer, DateTime
from app.database import Base
import datetime

class Review(Base):
    __tablename__ = "reviews"

    review_id = Column(String, primary_key=True, index=True)
    session_id = Column(String, index=True)
    reviewer_id = Column(String, index=True)
    target_user_id = Column(String, index=True)
    rating = Column(Integer, nullable=False)
    comment = Column(String, nullable=True)
    submitted_at = Column(DateTime, default=datetime.datetime.utcnow)

class Badge(Base):
    __tablename__ = "badges"

    user_id = Column(String, primary_key=True, index=True)
    badge_type = Column(String)  # Trusted | 5-Star Rated | Session Expert
    awarded_at = Column(DateTime, default=datetime.datetime.utcnow)
