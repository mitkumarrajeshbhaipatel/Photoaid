from sqlalchemy import Column, String, Float, DateTime
from app.database import Base
import datetime

class UserLocation(Base):
    __tablename__ = "locations"

    user_id = Column(String, primary_key=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)
