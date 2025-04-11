# app/test_main.py

import pytest
import httpx
import uuid

BASE_URL = "http://127.0.0.1:8000"

@pytest.mark.asyncio
async def test_end_to_end_flow():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        
        # 1. REGISTER new user
        random_email = f"user_{uuid.uuid4().hex[:8]}@example.com"
        password = "testpassword"
        register_payload = {
            "name": "John Tester",
            "email": random_email,
            "password": password
        }
        register_response = await client.post("/auth/register", json=register_payload)
        assert register_response.status_code == 200, f"Register Failed: {register_response.text}"
        user_data = register_response.json()
        user_id = user_data['id']

        # 2. LOGIN to get access token
        login_response = await client.post("/auth/login", params={"email": random_email, "password": password})
        assert login_response.status_code == 200, f"Login Failed: {login_response.text}"
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 3. GET Own PROFILE (authentication required)
        profile_response = await client.get(f"/profiles/{user_id}", headers=headers)
        assert profile_response.status_code == 200, f"Profile fetch failed: {profile_response.text}"
        profile_data = profile_response.json()
        assert profile_data["user_id"] == user_id

        # 4. TRY ACCESSING PROFILE without token (should fail)
        no_token_profile = await client.get(f"/profiles/{user_id}")
        assert no_token_profile.status_code in [401, 403], "Accessing profile without token should be forbidden"

        # 5. CREATE MATCH with own user ID
        match_payload = {
            "requester_id": user_id,
            "receiver_id": user_id
        }
        match_response = await client.post("/matchmaking/request", json=match_payload, headers=headers)
        assert match_response.status_code == 200, f"Match request failed: {match_response.text}"
        match_id = match_response.json()["match_id"]

        # 6. CREATE SESSION from match
        session_payload = {
            "requester_id": user_id,
            "helper_id": user_id,
            "match_id": match_id,
            "location": {"lat": 10.0, "lng": 20.0}
        }
        session_response = await client.post("/sessions/create", json=session_payload, headers=headers)
        assert session_response.status_code == 200, f"Session creation failed: {session_response.text}"
        session_id = session_response.json()["session_id"]

        # 7. SEND a SYSTEM NOTIFICATION
        notification_payload = {
            "user_id": user_id,
            "title": "Test Notification",
            "message": "This is a test system notification.",
            "notification_type": "system"
        }
        notification_response = await client.post("/notifications/", json=notification_payload, headers=headers)
        assert notification_response.status_code == 200, f"Notification failed: {notification_response.text}"

        # 8. SUBMIT REVIEW after session 
        review_payload = {
            "session_id": session_id,
            "reviewer_id": user_id,
            "target_user_id": user_id,
            "rating": 5,
            "comment": "Excellent service!"
        }
        review_response = await client.post("/reviews/", json=review_payload, headers=headers)
        assert review_response.status_code == 400, f"Review submission failed: {review_response.text}"
