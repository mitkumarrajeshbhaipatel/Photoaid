from sqlalchemy import Column, String, DateTime
from app.database import Base
import datetime

class Message(Base):
    __tablename__ = "messages"

    message_id = Column(String, primary_key=True, index=True)
    session_id = Column(String, nullable=False)
    sender_id = Column(String, nullable=False)
    content = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    message_type = Column(String, default="text")  # text | image | file
