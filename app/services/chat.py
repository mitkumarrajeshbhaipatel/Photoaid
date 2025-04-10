from sqlalchemy.orm import Session as DBSession
from app.models.chat import Message
from app.schemas.chat import MessageCreate
import uuid
import datetime

def save_message(db: DBSession, message_data: MessageCreate):
    message = Message(
        message_id=str(uuid.uuid4()),
        session_id=message_data.session_id,
        sender_id=message_data.sender_id,
        content=message_data.content,
        message_type=message_data.message_type,
        timestamp=datetime.datetime.utcnow()
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message

def get_messages_for_session(db: DBSession, session_id: str):
    return db.query(Message).filter(Message.session_id == session_id).order_by(Message.timestamp.asc()).all()
