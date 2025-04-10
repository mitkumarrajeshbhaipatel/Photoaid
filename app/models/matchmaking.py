from sqlalchemy import Column, String, DateTime
from app.database import Base
import datetime

class MatchRequest(Base):
    __tablename__ = "match_requests"

    match_id = Column(String, primary_key=True, index=True)
    requester_id = Column(String, nullable=False)
    receiver_id = Column(String, nullable=False)
    status = Column(String, default="pending")  # pending | accepted | declined | expired
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    accepted_at = Column(DateTime, nullable=True)
