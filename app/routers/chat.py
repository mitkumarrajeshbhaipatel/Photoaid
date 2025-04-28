from fastapi import APIRouter, WebSocket, Depends
from sqlalchemy.orm import Session as DBSession
from app.dependencies import get_db
from app.services.chat import save_message, get_messages_for_session
from app.schemas.chat import MessageCreate, MessageOut
from app.utils.websocket import manager
import json
from datetime import datetime

router = APIRouter(prefix="/chat", tags=["Chat Service"])


@router.websocket("/ws/{session_id}/{sender_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str, sender_id: str, db: DBSession = Depends(get_db)):
    await manager.connect(session_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            parsed_data = json.loads(data)

            msg_type = parsed_data.get("type")

            # 1️⃣ Handle NEW chat message
            if msg_type == "chat":
                msg = MessageCreate(
                    message_id=parsed_data.get("message_id"),
                    session_id=session_id,
                    sender_id=sender_id,
                    content=parsed_data.get("content"),
                    message_type=parsed_data.get("message_type", "text")
                )
                saved_msg = save_message(db, msg)
                saved_msg_timestamp = saved_msg.timestamp.isoformat()
                print(saved_msg_timestamp)

                # 2️⃣ Send ACK to sender
                await websocket.send_text(json.dumps({
                    "type": "ack",
                    "message_id": saved_msg.message_id,
                    "timestamp": str(saved_msg_timestamp),
                    "status": "sent"
                }))

                # 3️⃣ Broadcast chat message to other clients
                await manager.send_personal_message(json.dumps({
                    "type": "chat",
                    "sender_id": sender_id,
                    "content": saved_msg.content,
                    "message_id": saved_msg.message_id,
                    "message_type": saved_msg.message_type,
                    "timestamp": str(saved_msg_timestamp),
                    "status": "delivered"
                }), session_id)

            # 4️⃣ Handle DELIVERED status from receiver
            elif msg_type == "delivered":
                await manager.send_personal_message(json.dumps({
                    "type": "status",
                    "message_id": parsed_data["message_id"],
                    "status": "delivered"
                }), session_id)

            # 5️⃣ Handle READ status from receiver
            elif msg_type == "read":
                await manager.send_personal_message(json.dumps({
                    "type": "status",
                    "message_id": parsed_data["message_id"],
                    "status": "read"
                }), session_id)

    except Exception as e:
        print("WebSocket Error:", e)
    finally:
        manager.disconnect(session_id)


@router.get("/messages/{session_id}")
def get_session_messages(session_id: str, db: DBSession = Depends(get_db)):
    return get_messages_for_session(db, session_id)
