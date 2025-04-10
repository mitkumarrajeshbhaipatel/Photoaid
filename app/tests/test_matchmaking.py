# app/tests/test_matchmaking.py

import pytest
import httpx
import uuid

BASE_URL = "http://127.0.0.1:8000"

@pytest.mark.asyncio
async def test_matchmaking_full_flow():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:

        # -------- Setup: Register two users --------
        # Register User A
        email_a = f"usera_{uuid.uuid4().hex[:8]}@example.com"
        password_a = "PasswordA123"
        register_a = await client.post("/auth/register", json={"name": "User A", "email": email_a, "password": password_a})
        assert register_a.status_code == 200
        user_a_id = register_a.json()["id"]

        # Login User A
        login_a = await client.post("/auth/login", params={"email": email_a, "password": password_a})
        token_a = login_a.json()["access_token"]
        headers_a = {"Authorization": f"Bearer {token_a}"}

        # Register User B
        email_b = f"userb_{uuid.uuid4().hex[:8]}@example.com"
        password_b = "PasswordB123"
        register_b = await client.post("/auth/register", json={"name": "User B", "email": email_b, "password": password_b})
        assert register_b.status_code == 200
        user_b_id = register_b.json()["id"]

        # Login User B
        login_b = await client.post("/auth/login", params={"email": email_b, "password": password_b})
        token_b = login_b.json()["access_token"]
        headers_b = {"Authorization": f"Bearer {token_b}"}

        # -------- Tests: Match Creation --------
        # 1. Valid match request (A -> B)
        match_payload = {"requester_id": user_a_id, "receiver_id": user_b_id}
        create_match = await client.post("/matchmaking/request", json=match_payload, headers=headers_a)
        assert create_match.status_code == 200
        match_data = create_match.json()
        match_id = match_data["match_id"]  # Correct key here!

        # 2. Unauthorized match request (no token)
        no_auth_create = await client.post("/matchmaking/request", json=match_payload)
        assert no_auth_create.status_code in [401, 403]

        # 3. Self-match (A -> A)
        self_match = await client.post("/matchmaking/request", json={"requester_id": user_a_id, "receiver_id": user_a_id}, headers=headers_a)
        assert self_match.status_code == 200

        # 4. Match request with invalid requester ID
        bad_match = await client.post("/matchmaking/request", json={"requester_id": str(uuid.uuid4()), "receiver_id": user_b_id}, headers=headers_a)
        assert bad_match.status_code in [400, 403, 404]

        # 5. Match request missing fields
        incomplete_match = await client.post("/matchmaking/request", json={"requester_id": user_a_id}, headers=headers_a)
        assert incomplete_match.status_code == 422

        # -------- Tests: Fetch My Matches --------
        # 6. Fetch matches for User A
        matches_a = await client.get(f"/matchmaking/my-matches/{user_a_id}", headers=headers_a)
        assert matches_a.status_code == 200
        assert isinstance(matches_a.json(), list)

        # 7. Fetch matches for User B
        matches_b = await client.get(f"/matchmaking/my-matches/{user_b_id}", headers=headers_b)
        assert matches_b.status_code == 200
        assert isinstance(matches_b.json(), list)

        # 8. Unauthorized fetch my-matches
        no_auth_fetch = await client.get(f"/matchmaking/my-matches/{user_a_id}")
        assert no_auth_fetch.status_code in [401, 403]

        # 9. Fetch matches for random invalid user
        random_user_fetch = await client.get(f"/matchmaking/my-matches/{uuid.uuid4()}", headers=headers_a)
        assert random_user_fetch.status_code == 403
        assert "detail" in random_user_fetch.json()
        assert random_user_fetch.json()["detail"] == "Forbidden to access others' matches"


        # -------- Tests: Respond to Match --------
        # 10. Accept match by B
        accept_payload = {"status": "accepted"}
        accept_match = await client.post(f"/matchmaking/respond/{match_id}", json=accept_payload, headers=headers_b)
        assert accept_match.status_code == 200
        assert accept_match.json()["status"] == "accepted"

        # 11. Reject match (create new match first)
        new_match = await client.post("/matchmaking/request", json={"requester_id": user_a_id, "receiver_id": user_b_id}, headers=headers_a)
        new_match_id = new_match.json()["match_id"]
        reject_payload = {"status": "rejected"}
        reject_match = await client.post(f"/matchmaking/respond/{new_match_id}", json=reject_payload, headers=headers_b)
        assert reject_match.status_code == 200
        assert reject_match.json()["status"] == "rejected"

        # 12. Unauthorized respond
        unauth_respond = await client.post(f"/matchmaking/respond/{new_match_id}", json=accept_payload)
        assert unauth_respond.status_code in [401, 403]

        # 13. Respond to non-existing match
        fake_response = await client.post(f"/matchmaking/respond/{uuid.uuid4()}", json=accept_payload, headers=headers_b)
        assert fake_response.status_code == 404

        # 14. Respond with invalid status
        invalid_status_response = await client.post(f"/matchmaking/respond/{new_match_id}", json={"status": "maybe"}, headers=headers_b)
        assert invalid_status_response.status_code in [400, 409, 422]

        # 15. Double respond to already accepted match
        double_respond = await client.post(f"/matchmaking/respond/{match_id}", json={"status": "rejected"}, headers=headers_b)
        assert double_respond.status_code in [400, 409, 422]

        # -------- Negative Cases and Other Validations --------
        # 16. Bad UUID format in my-matches
        invalid_uuid_fetch = await client.get("/matchmaking/my-matches/notauuid", headers=headers_a)
        assert invalid_uuid_fetch.status_code in [403, 422]

        # 17. Respond without body
        empty_body_respond = await client.post(f"/matchmaking/respond/{match_id}", headers=headers_b)
        assert empty_body_respond.status_code in [400, 422]

        # 18. Create match without body
        empty_body_create = await client.post("/matchmaking/request", headers=headers_a)
        assert empty_body_create.status_code in [400, 422]

        # 19. Fetch matches without token
        unauth_fetch = await client.get(f"/matchmaking/my-matches/{user_a_id}")
        assert unauth_fetch.status_code in [401, 403]

        # 20. Respond with extra unexpected fields
        extra_field_respond = await client.post(f"/matchmaking/respond/{new_match_id}", json={"status": "accepted", "extra_field": "unexpected"}, headers=headers_b)
        assert extra_field_respond.status_code in [200, 409]

        # -------- Security Checks --------
        # 21. User A tries to respond to their own match (should fail)
        illegal_response = await client.post(f"/matchmaking/respond/{new_match_id}", json={"status": "accepted"}, headers=headers_a)
        assert illegal_response.status_code in [400, 403]

        # 22. User B requests match with User A (reverse)
        reverse_match = await client.post("/matchmaking/request", json={"requester_id": user_b_id, "receiver_id": user_a_id}, headers=headers_b)
        assert reverse_match.status_code == 200

        # 23. Match request with invalid receiver
        invalid_receiver_match = await client.post("/matchmaking/request", json={"requester_id": user_a_id, "receiver_id": "invalid-id"}, headers=headers_a)
        assert invalid_receiver_match.status_code in [400, 200, 422]

        # 24. Create match with missing requester_id
        missing_requester = await client.post("/matchmaking/request", json={"receiver_id": user_b_id}, headers=headers_a)
        assert missing_requester.status_code == 422

        # 25. Respond using integer instead of string status
        wrong_type_status = await client.post(f"/matchmaking/respond/{match_id}", json={"status": 123}, headers=headers_b)
        assert wrong_type_status.status_code == 422

        # 26. Multiple valid matches
        another_match = await client.post("/matchmaking/request", json={"requester_id": user_a_id, "receiver_id": user_b_id}, headers=headers_a)
        assert another_match.status_code == 200

        # 27. Fetch and check total matches for A
        updated_matches = await client.get(f"/matchmaking/my-matches/{user_a_id}", headers=headers_a)
        assert updated_matches.status_code == 200
        assert isinstance(updated_matches.json(), list)

        # 28. Fetch and check total matches for B
        updated_matches_b = await client.get(f"/matchmaking/my-matches/{user_b_id}", headers=headers_b)
        assert updated_matches_b.status_code == 200

        # 29. Create match with same users again
        duplicate_match = await client.post("/matchmaking/request", json={"requester_id": user_a_id, "receiver_id": user_b_id}, headers=headers_a)
        assert duplicate_match.status_code == 200

        # 30. Respond to duplicated match
        duplicate_match_id = duplicate_match.json()["match_id"]
        duplicate_respond = await client.post(f"/matchmaking/respond/{duplicate_match_id}", json={"status": "accepted"}, headers=headers_b)
        assert duplicate_respond.status_code == 200
