from pydantic import BaseModel
from datetime import datetime

class MessageCreate(BaseModel):
    message_id: str
    session_id: str
    sender_id: str
    content: str
    message_type: str = "text"

class MessageOut(BaseModel):
    message_id: str
    session_id: str
    sender_id: str
    content: str
    timestamp: datetime
    message_type: str

    class Config:
        orm_mode = True
