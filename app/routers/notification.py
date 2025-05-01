from fastapi import APIRouter, Depends, HTTPException, WebSocket
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.schemas.notification import NotificationCreate, NotificationOut
from app.services.notification import create_notification, get_notifications, mark_notification_read
from typing import List


router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.websocket("/ws/notifications/{user_id}")
async def notifications_ws(websocket: WebSocket, user_id: str):
    await manager.connect(user_id, websocket)
    try:
        while True:
            await websocket.receive_text()  # Just to keep the connection alive
    except Exception as e:
        print("Notification WS Error:", e)
    finally:
        manager.disconnect(user_id)

@router.post("/", response_model=NotificationOut)
def send_notification(notification: NotificationCreate, db: Session = Depends(get_db)):
    return create_notification(db, notification)

@router.get("/{user_id}", response_model=List[NotificationOut])
def list_notifications(user_id: str, db: Session = Depends(get_db)):
    return get_notifications(db, user_id)

@router.post("/mark-read/{notification_id}", response_model=NotificationOut)
def read_notification(notification_id: str, db: Session = Depends(get_db)):
    notification = mark_notification_read(db, notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification
