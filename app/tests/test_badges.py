import pytest
import httpx
import uuid
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

@pytest.mark.asyncio
async def test_review_and_badge_functionality():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        # -------- SETUP --------
        email_req = f"req_{uuid.uuid4().hex[:8]}@example.com"
        email_target = f"target_{uuid.uuid4().hex[:8]}@example.com"
        password = "Test1234"

        # Register requester
        req_register = await client.post("/auth/register", json={"name": "Requester", "email": email_req, "password": password})
        req_id = req_register.json()["id"]

        # Register target user
        target_register = await client.post("/auth/register", json={"name": "Target", "email": email_target, "password": password})
        target_id = target_register.json()["id"]

        # Log in requester to get the access token
        req_login = await client.post("/auth/login", params={"email": email_req, "password": password})
        req_token = req_login.json()["access_token"]
        headers_req = {"Authorization": f"Bearer {req_token}"}  # Add Authorization header

        # Create a valid active session for testing
        session_payload = {
            "requester_id": req_id,
            "helper_id": target_id,
            "match_id": str(uuid.uuid4()),  # Generate a fresh match_id
            "location": {"lat": 12.9716, "lng": 77.5946}
        }

        # Create session
        create_session = await client.post("/sessions/create", json=session_payload, headers=headers_req)
        assert create_session.status_code == 200
        session_id = create_session.json()["session_id"]

        # Update session status to 'completed'
        complete_payload = {"status": "completed"}
        complete_session = await client.post(f"/sessions/update-status/{session_id}", json=complete_payload, headers=headers_req)
        assert complete_session.status_code == 200

        # -------- TEST 1: Submit Review --------
        review_payload_1 = {
            "session_id": session_id,
            "reviewer_id": req_id,
            "target_user_id": target_id,
            "rating": 5,
            "comment": "Great job! Excellent communication."
        }

        # Submit review
        submit_review = await client.post("/reviews/", json=review_payload_1, headers=headers_req)
        assert submit_review.status_code == 200
        review_data = submit_review.json()

        # Check if the review is saved correctly
        assert review_data["rating"] == 5
        assert review_data["comment"] == "Great job! Excellent communication."
        assert review_data["reviewer_id"] == req_id
        assert review_data["target_user_id"] == target_id

        # -------- TEST 2: Submit Review with Invalid Rating --------
        invalid_review_payload = {
            "session_id": session_id,
            "reviewer_id": req_id,
            "target_user_id": target_id,
            "rating": 6,  # Invalid rating, should be between 1-5
            "comment": "Rating is too high!"
        }
        invalid_review = await client.post("/reviews/", json=invalid_review_payload, headers=headers_req)
        assert invalid_review.status_code in [401, 422]  # Invalid rating should return 422

        # -------- TEST 3: List Reviews for a User --------
        list_reviews = await client.get(f"/reviews/{target_id}", headers=headers_req)
        assert list_reviews.status_code == 200
        reviews = list_reviews.json()
        assert len(reviews) >= 1  # There should be at least one review
        assert reviews[0]["target_user_id"] == target_id

        # -------- TEST 4: List Reviews for Non-Existent User --------
        non_existent_user_id = str(uuid.uuid4())
        non_existent_reviews = await client.get(f"/reviews/{non_existent_user_id}", headers=headers_req)
        assert non_existent_reviews.status_code == 200  # Empty list expected
        assert len(non_existent_reviews.json()) == 0  # No reviews for non-existent user

        # -------- TEST 5: Unauthorized Review Submission --------
        unauthorized_review_payload = {
            "session_id": session_id,
            "reviewer_id": req_id,
            "target_user_id": target_id,
            "rating": 5,
            "comment": "Unauthorized review!"
        }
        # Try submitting without authentication
        unauthorized_review = await client.post("/reviews/", json=unauthorized_review_payload)
        assert unauthorized_review.status_code == 401  # Unauthorized should return 401

        # -------- TEST 6: Create Review Without Active Session --------
        fake_inactive_session_id = str(uuid.uuid4())  # Fake session ID (inactive)
        review_without_active_session_payload = {
            "session_id": fake_inactive_session_id,
            "reviewer_id": req_id,
            "target_user_id": target_id,
            "rating": 4,
            "comment": "Review without active session"
        }
        review_without_active_session = await client.post("/reviews/", json=review_without_active_session_payload, headers=headers_req)
        assert review_without_active_session.status_code == 404  # Should not allow review without active session

        # -------- TEST 7: Review After Session Completion --------
        review_without_active_session_payload = {
            "session_id": session_id,
            "reviewer_id": req_id,
            "target_user_id": target_id,
            "rating": 4,
            "comment": "Review without active session"
        }
        # Simulate session completion
        session_complete_payload = {"status": "completed"}
        complete_session = await client.post(f"/sessions/update-status/{session_id}", json=session_complete_payload, headers=headers_req)
        assert complete_session.status_code == 200
        assert complete_session.json()["status"] == "completed"

        # Now, try submitting the review after the session completion
        review_after_session_complete = await client.post("/reviews/", json=review_without_active_session_payload, headers=headers_req)
        assert review_after_session_complete.status_code == 200  # Review should be allowed after session completion

        # -------- TEST 8: Empty or Bad Payload --------
        empty_payload = {"session_id": fake_inactive_session_id, "reviewer_id": req_id, "target_user_id": target_id}
        empty_payload_response = await client.post("/reviews/", json=empty_payload, headers=headers_req)
        assert empty_payload_response.status_code == 422  # Missing content

        bad_payload = {"session_id": fake_inactive_session_id, "reviewer_id": req_id, "target_user_id": target_id, "content": "Invalid message", "rating": 6}
        bad_payload_response = await client.post("/reviews/", json=bad_payload, headers=headers_req)
        assert bad_payload_response.status_code == 422  # Invalid rating value (greater than 5)

        # -------- TEST 9: Check if Badge is Awarded --------
        badges_response = await client.get(f"/reviews/badges/{target_id}", headers=headers_req)
        assert badges_response.status_code == 200
        badge = badges_response.json()
        assert badge["badge_type"] == "Newbie"  # Badge should reflect Newbie for initial reviews

        print("\n✅ Review functionality test passed!")
