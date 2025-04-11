from sqlalchemy import Column, String, DateTime, JSON
from app.database import Base
import datetime

class Session(Base):
    __tablename__ = "sessions"

    session_id = Column(String, primary_key=True, index=True)
    requester_id = Column(String, nullable=False)
    helper_id = Column(String, nullable=False)
    match_id = Column(String, nullable=False)
    status = Column(String, default="created")  # created | started | completed | cancelled | end
    location = Column(JSON, nullable=False)  # {"lat": float, "lng": float}
    check_in_time = Column(DateTime, nullable=True)
    check_out_time = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
