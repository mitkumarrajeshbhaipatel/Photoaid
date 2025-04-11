'''
import pytest
import httpx
import uuid
import json
from datetime import datetime
from fastapi.testclient import TestClient
from app.main import app  # Import your FastAPI app instance


#client = TestClient(app)

BASE_URL = "http://127.0.0.1:8000"

@pytest.mark.asyncio
async def test_chat_functionality():
    
    # -------- SETUP --------
    email_req = f"req_{uuid.uuid4().hex[:8]}@example.com"
    email_help = f"help_{uuid.uuid4().hex[:8]}@example.com"
    password = "Test1234"
    
    # Register users
    req_register = await client.post("/auth/register", json={"name": "Requester", "email": email_req, "password": password})
    req_id = req_register.json()["id"]

    help_register = await client.post("/auth/register", json={"name": "Helper", "email": email_help, "password": password})
    help_id = help_register.json()["id"]

    # Authenticate both users
    req_login = await client.post("/auth/login", params={"email": email_req, "password": password})
    req_token = req_login.json()["access_token"]
    headers_req = {"Authorization": f"Bearer {req_token}"}

    help_login = await client.post("/auth/login", params={"email": email_help, "password": password})
    help_token = help_login.json()["access_token"]
    headers_help = {"Authorization": f"Bearer {help_token}"}

    # Create a match
    fake_match_id = str(uuid.uuid4())  # Fake match ID
    match_payload = {"requester_id": req_id, "helper_id": help_id, "match_id": fake_match_id}
    await client.post("/matchmaking/request", json=match_payload, headers=headers_req)

    # -------- TEST CASE 1: WebSocket Connection for Requester --------
    session_id = fake_match_id  # For this test, using match_id as session_id

    async with client.websocket_connect(f"/chat/ws/{session_id}/{req_id}") as ws_req:
        await ws_req.send_json({"content": "Hello from requester", "message_type": "text"})
        response = await ws_req.receive_text()
        response_data = json.loads(response)
        assert response_data["content"] == "Hello from requester"

    # -------- TEST CASE 2: WebSocket Connection for Helper --------
    async with client.websocket_connect(f"/chat/ws/{session_id}/{help_id}") as ws_help:
        await ws_help.send_json({"content": "Hello from helper", "message_type": "text"})
        response = await ws_help.receive_text()
        response_data = json.loads(response)
        assert response_data["content"] == "Hello from helper"

    # -------- TEST CASE 3: Save Message --------
    message_payload = {
        "session_id": session_id,
        "sender_id": req_id,
        "content": "Message from requester",
        "message_type": "text"
    }
    message_response = await client.post("/chat/messages", json=message_payload, headers=headers_req)
    assert message_response.status_code == 200
    message_data = message_response.json()
    assert message_data["content"] == "Message from requester"
    assert message_data["sender_id"] == req_id

    # -------- TEST CASE 4: Get Messages for a Session --------
    messages = await client.get(f"/chat/messages/{session_id}", headers=headers_req)
    assert messages.status_code == 200
    assert isinstance(messages.json(), list)
    assert len(messages.json()) > 0  # Should return at least one message

    # -------- TEST CASE 5: Unauthorized Access (No Auth) --------
    unauthorized_response = await client.get(f"/chat/messages/{session_id}")
    assert unauthorized_response.status_code in [401, 403]

    # -------- TEST CASE 6: Fetch Chat Messages with Wrong Session ID --------
    wrong_session_id = str(uuid.uuid4())  # Random wrong session ID
    wrong_session_response = await client.get(f"/chat/messages/{wrong_session_id}", headers=headers_req)
    assert wrong_session_response.status_code == 404

    # -------- TEST CASE 7: WebSocket Disconnect --------
    async with client.websocket_connect(f"/chat/ws/{session_id}/{req_id}") as ws_disconnect:
        await ws_disconnect.send_json({"content": "Testing disconnect", "message_type": "text"})
        await ws_disconnect.close()
        assert ws_disconnect.closed

    # -------- TEST CASE 8: Empty or Bad Payload --------
    empty_payload = {"session_id": session_id, "sender_id": req_id}
    empty_payload_response = await client.post("/chat/messages", json=empty_payload, headers=headers_req)
    assert empty_payload_response.status_code == 422  # Missing content

    bad_payload = {"session_id": session_id, "sender_id": req_id, "content": "Invalid message", "message_type": "unknown"}
    bad_payload_response = await client.post("/chat/messages", json=bad_payload, headers=headers_req)
    assert bad_payload_response.status_code == 422  # Invalid message type

    # -------- TEST CASE 9: Try sending a message to a session that doesn't exist --------
    fake_session_id = str(uuid.uuid4())
    fake_session_payload = {
        "session_id": fake_session_id,
        "sender_id": req_id,
        "content": "Fake session message",
        "message_type": "text"
    }
    fake_session_response = await client.post("/chat/messages", json=fake_session_payload, headers=headers_req)
    assert fake_session_response.status_code == 404  # Session not found

    # -------- TEST CASE 10: Invalid message type --------
    invalid_message_payload = {
        "session_id": session_id,
        "sender_id": req_id,
        "content": "This is an invalid message type test",
        "message_type": "invalid_type"
    }
    invalid_message_response = await client.post("/chat/messages", json=invalid_message_payload, headers=headers_req)
    assert invalid_message_response.status_code == 422  # Invalid message type should return a validation error

    # -------- TEST CASE 11: WebSocket message echo --------
    async with client.websocket_connect(f"/chat/ws/{session_id}/{req_id}") as ws_req:
        await ws_req.send_json({"content": "Hello", "message_type": "text"})
        response = await ws_req.receive_text()
        assert "Hello" in response  # Check if message was echoed correctly

    # -------- TEST CASE 12: Chat with an inactive session --------
    fake_session_id = str(uuid.uuid4())  # Fake session ID
    fake_chat_message = {
        "session_id": fake_session_id,
        "sender_id": req_id,
        "content": "Message to inactive session",
        "message_type": "text"
    }
    fake_chat_response = await client.post("/chat/messages", json=fake_chat_message, headers=headers_req)
    assert fake_chat_response.status_code == 404  # Should return session not found

    print("\n✅ Chat functionality test passed!")

'''
