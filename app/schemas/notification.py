from pydantic import BaseModel
from datetime import datetime

class NotificationCreate(BaseModel):
    user_id: str
    title: str
    message: str
    notification_type: str  # session | chat | admin | system

class NotificationOut(BaseModel):
    notification_id: str
    user_id: str
    title: str
    message: str
    is_read: bool
    created_at: datetime
    notification_type: str

    class Config:
        orm_mode = True
