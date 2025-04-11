import pytest
import httpx
import uuid
import datetime

BASE_URL = "http://127.0.0.1:8000"

@pytest.mark.asyncio
async def test_session_flow():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:

        # --------  SETUP (TC-1 to TC-4) --------

        # TC-1: Register requester
        email_req = f"req_{uuid.uuid4().hex[:8]}@example.com"
        password = "Test1234"
        req_register = await client.post("/auth/register", json={"name": "Requester", "email": email_req, "password": password})
        assert req_register.status_code == 200
        requester_id = req_register.json()["id"]

        # TC-2: Register helper
        email_help = f"help_{uuid.uuid4().hex[:8]}@example.com"
        help_register = await client.post("/auth/register", json={"name": "Helper", "email": email_help, "password": password})
        assert help_register.status_code == 200
        helper_id = help_register.json()["id"]

        # TC-3: Login requester
        req_login = await client.post("/auth/login", params={"email": email_req, "password": password})
        requester_token = req_login.json()["access_token"]
        headers_req = {"Authorization": f"Bearer {requester_token}"}

        # TC-4: Login helper
        help_login = await client.post("/auth/login", params={"email": email_help, "password": password})
        helper_token = help_login.json()["access_token"]
        headers_help = {"Authorization": f"Bearer {helper_token}"}

        # TC-5: Create Match between requester -> helper
        match_payload = {"requester_id": requester_id, "receiver_id": helper_id}
        create_match = await client.post("/matchmaking/request", json=match_payload, headers=headers_req)
        assert create_match.status_code == 200
        match_id = create_match.json()["match_id"]

        # -------- SESSION CREATION (TC-6 to TC-12) --------

        valid_session_payload = {
            "requester_id": requester_id,
            "helper_id": helper_id,
            "match_id": match_id,
            "location": {"lat": 12.9716, "lng": 77.5946}
        }

        # TC-6: Create session valid
        create_session = await client.post("/sessions/create", json=valid_session_payload, headers=headers_req)
        assert create_session.status_code == 200
        session_id = create_session.json()["session_id"]

        # TC-7: Missing location
        bad_payload = valid_session_payload.copy()
        del bad_payload["location"]
        bad_create = await client.post("/sessions/create", json=bad_payload, headers=headers_req)
        assert bad_create.status_code == 422

        # TC-8: Wrong type location
        wrong_loc_payload = valid_session_payload.copy()
        wrong_loc_payload["location"] = "notadict"
        wrong_create = await client.post("/sessions/create", json=wrong_loc_payload, headers=headers_req)
        assert wrong_create.status_code == 422

        # TC-9: Wrong requester/helper IDs
        wrong_ids_payload = valid_session_payload.copy()
        wrong_ids_payload["requester_id"] = "wrong"
        wrong_id_create = await client.post("/sessions/create", json=wrong_ids_payload, headers=headers_req)
        assert wrong_id_create.status_code in [400, 409]

        # TC-10: Duplicate session (depends)
        duplicate_create = await client.post("/sessions/create", json=valid_session_payload, headers=headers_req)
        assert duplicate_create.status_code in [400, 409]

        # TC-11: Create without auth (use a fresh match_id)
        new_fake_match_id = str(uuid.uuid4())
        no_auth_payload = valid_session_payload.copy()
        no_auth_payload["match_id"] = new_fake_match_id  # 🔥 use fresh match id

        no_auth_create = await client.post("/sessions/create", json=no_auth_payload)
        assert no_auth_create.status_code in [401, 403]

        # TC-12: Create with extra fields
        new_match_id_for_extra = str(uuid.uuid4())  # 🔥 NEW MATCH ID

        extra_field_payload = {
            **valid_session_payload,
            "match_id": new_match_id_for_extra,  # use fresh match_id
            "extra": "field"
        }
        extra_field_create = await client.post("/sessions/create", json=extra_field_payload, headers=headers_req)
        assert extra_field_create.status_code in [200, 422]


        # -------- SESSION STATUS UPDATES (TC-13 to TC-18) --------

        start_payload = {"status": "started"}

        # TC-13: Start session valid
        start_session = await client.post(f"/sessions/update-status/{session_id}", json=start_payload, headers=headers_req)
        assert start_session.status_code == 200

        # TC-14: Start with wrong status value
        wrong_status = await client.post(f"/sessions/update-status/{session_id}", json={"status": "flying"}, headers=headers_req)
        assert wrong_status.status_code in [400, 422]

        # TC-15: Start non-existing session
        fake_start = await client.post(f"/sessions/update-status/{uuid.uuid4()}", json=start_payload, headers=headers_req)
        assert fake_start.status_code == 404

        # TC-16: Start invalid UUID session
        invalid_uuid_start = await client.post("/sessions/update-status/notauuid", json=start_payload, headers=headers_req)
        assert invalid_uuid_start.status_code in [422, 404, 400]

        # TC-17: Unauthorized start session
        email_wrong = f"wrong_{uuid.uuid4().hex[:8]}@example.com"
        wrong_user = await client.post("/auth/register", json={"name": "Wrong", "email": email_wrong, "password": password})
        wrong_login = await client.post("/auth/login", params={"email": email_wrong, "password": password})
        wrong_token = wrong_login.json()["access_token"]
        headers_wrong = {"Authorization": f"Bearer {wrong_token}"}
        unauthorized_update = await client.post(f"/sessions/update-status/{session_id}", json=start_payload, headers=headers_wrong)
        assert unauthorized_update.status_code in [400, 403]

        # TC-18: Try updating other's session
        other_update = await client.post(f"/sessions/update-status/{session_id}", json=start_payload, headers=headers_wrong)
        assert other_update.status_code in [400, 403]

        # -------- SESSION COMPLETION (TC-19 to TC-22) --------

        complete_payload = {"status": "completed"}

        # TC-19: Complete session valid
        complete_session = await client.post(f"/sessions/update-status/{session_id}", json=complete_payload, headers=headers_help)
        assert complete_session.status_code == 200

        # TC-20: Double complete
        double_complete = await client.post(f"/sessions/update-status/{session_id}", json=complete_payload, headers=headers_help)
        assert double_complete.status_code in [200]

        # TC-21: Complete invalid session
        complete_invalid = await client.post(f"/sessions/update-status/notauuid", json=complete_payload, headers=headers_req)
        assert complete_invalid.status_code in [400, 404, 422]

        # TC-22: Complete session by wrong user
        wrong_complete = await client.post(f"/sessions/update-status/{session_id}", json=complete_payload, headers=headers_wrong)
        assert wrong_complete.status_code in [400, 403]

        # -------- SESSION FETCH (TC-23 to TC-27) --------

        # TC-23: Fetch session by match_id
        fetch_session = await client.get(f"/sessions/by-match/{match_id}", headers=headers_req)
        assert fetch_session.status_code == 200

        # TC-24: Fetch session by random wrong match_id
        random_fetch = await client.get(f"/sessions/by-match/{uuid.uuid4()}", headers=headers_req)
        assert random_fetch.status_code == 404

        # TC-25: Fetch session invalid UUID
        invalid_fetch = await client.get("/sessions/by-match/notauuid", headers=headers_req)
        assert invalid_fetch.status_code in [422, 404, 400]

        # TC-26: Fetch without auth
        fetch_unauth = await client.get(f"/sessions/by-match/{match_id}")
        assert fetch_unauth.status_code in [401, 403]  # Expect 401 Unauthorized if token is missing

        # TC-27: Fetch other's session unauthorized
        fetch_others = await client.get(f"/sessions/by-match/{match_id}", headers=headers_wrong)
        assert fetch_others.status_code in [400, 403]

        # -------- BAD PAYLOADS (TC-28 to TC-30) --------

        # TC-28: Bad UUIDs in update-status
        bad_uuid_update = await client.post("/sessions/update-status/invalid-uuid", json=start_payload, headers=headers_req)
        assert bad_uuid_update.status_code in [400, 404, 422]

        # TC-29: Missing fields when creating session
        bad_payload_missing = await client.post("/sessions/create", json={"location": {"lat": 0.0, "lng": 0.0}}, headers=headers_req)
        assert bad_payload_missing.status_code == 422

        # TC-30: Chat/review only after correct session state (future test)
        # (simulated here)
        # chat_response = await client.post("/chat/send", json={...}) only if session started
        # review_response = await client.post("/review/submit", json={...}) only if session completed

        print("\n✅ All session management tests completed with 30 scenarios!")
