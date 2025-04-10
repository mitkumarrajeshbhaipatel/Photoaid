from sqlalchemy import Column, String, Boolean, DateTime
from app.database import Base
import datetime

class Notification(Base):
    __tablename__ = "notifications"

    notification_id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True)
    title = Column(String)
    message = Column(String)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    notification_type = Column(String)  # session | chat | admin | system
