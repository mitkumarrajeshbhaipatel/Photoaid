from sqlalchemy.orm import Session
from app.models.notification import Notification
from app.schemas.notification import NotificationCreate
import uuid
import datetime
from app.utils.websocket import manager  

async def create_notification(db: Session, notification: NotificationCreate):
    ...
    # After saving in DB:
    await manager.send_personal_message({
        "type": "notification",
        "title": notification.title,
        "message": notification.message,
        "notification_id": db_notification.notification_id,
        "notification_type": notification.notification_type,
        "created_at": db_notification.created_at.isoformat()
    }, notification.user_id)


def create_notification(db: Session, notification: NotificationCreate):
    db_notification = Notification(
        notification_id=str(uuid.uuid4()),
        user_id=notification.user_id,
        title=notification.title,
        message=notification.message,
        is_read=False,
        created_at=datetime.datetime.utcnow(),
        notification_type=notification.notification_type
    )
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification

def get_notifications(db: Session, user_id: str):
    return db.query(Notification).filter(Notification.user_id == user_id).all()

def mark_notification_read(db: Session, notification_id: str):
    notification = db.query(Notification).filter(Notification.notification_id == notification_id).first()
    if notification:
        notification.is_read = True
        db.commit()
        db.refresh(notification)
    return notification
