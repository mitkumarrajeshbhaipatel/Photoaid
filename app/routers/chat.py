from fastapi import APIRouter, WebSocket, Depends
from sqlalchemy.orm import Session as DBSession
from app.dependencies import get_db
from app.services.chat import save_message, get_messages_for_session
from app.schemas.chat import MessageCreate
from app.utils.websocket import manager
import json

router = APIRouter(prefix="/chat", tags=["Chat Service"])

@router.websocket("/ws/{session_id}/{sender_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str, sender_id: str, db: DBSession = Depends(get_db)):
    await manager.connect(session_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            parsed_data = json.loads(data)

            # Save incoming message
            msg = MessageCreate(
                session_id=session_id,
                sender_id=sender_id,
                content=parsed_data.get("content"),
                message_type=parsed_data.get("message_type", "text")
            )
            save_message(db, msg)

            # Broadcast back
            await manager.send_personal_message(json.dumps({
                "sender_id": sender_id,
                "content": msg.content,
                "message_type": msg.message_type,
            }), session_id)

    except Exception as e:
        print("WebSocket Error:", e)
    finally:
        manager.disconnect(session_id)

@router.get("/messages/{session_id}")
def get_session_messages(session_id: str, db: DBSession = Depends(get_db)):
    return get_messages_for_session(db, session_id)
