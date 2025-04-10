# app/tests/test_location.py

import pytest
import httpx
import uuid

BASE_URL = "http://127.0.0.1:8000"

@pytest.mark.asyncio
async def test_location_flow():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:

        # --- 1. Register User A
        email_a = f"usera_{uuid.uuid4().hex[:8]}@example.com"
        password_a = "PasswordA123"
        register_payload_a = {
            "name": "User A",
            "email": email_a,
            "password": password_a
        }
        register_response_a = await client.post("/auth/register", json=register_payload_a)
        assert register_response_a.status_code == 200
        user_a_id = register_response_a.json()["id"]

        # --- 2. Login User A
        login_response_a = await client.post("/auth/login", params={"email": email_a, "password": password_a})
        assert login_response_a.status_code == 200
        token_a = login_response_a.json()["access_token"]
        headers_a = {"Authorization": f"Bearer {token_a}"}

        # --- 3. Register User B
        email_b = f"userb_{uuid.uuid4().hex[:8]}@example.com"
        password_b = "PasswordB123"
        register_payload_b = {
            "name": "User B",
            "email": email_b,
            "password": password_b
        }
        register_response_b = await client.post("/auth/register", json=register_payload_b)
        assert register_response_b.status_code == 200
        user_b_id = register_response_b.json()["id"]

        # --- 4. Login User B
        login_response_b = await client.post("/auth/login", params={"email": email_b, "password": password_b})
        assert login_response_b.status_code == 200
        token_b = login_response_b.json()["access_token"]
        headers_b = {"Authorization": f"Bearer {token_b}"}

        # --- 5. User A updates their location
        location_payload_a = {
            "user_id": user_a_id,
            "latitude": 12.9716,
            "longitude": 77.5946
        }
        location_update_a = await client.post("/location/update", json=location_payload_a, headers=headers_a)
        assert location_update_a.status_code == 200, f"User A Location Update Failed: {location_update_a.text}"
        location_a = location_update_a.json()
        assert location_a["user_id"] == user_a_id

        # --- 6. User B updates their location
        location_payload_b = {
            "user_id": user_b_id,
            "latitude": 12.9718,
            "longitude": 77.5949
        }
        location_update_b = await client.post("/location/update", json=location_payload_b, headers=headers_b)
        assert location_update_b.status_code == 200, f"User B Location Update Failed: {location_update_b.text}"
        location_b = location_update_b.json()
        assert location_b["user_id"] == user_b_id

        # --- 7. Fetch nearby users for User A
        nearby_users_a = await client.get(f"/location/nearby/{user_a_id}?radius_km=1", headers=headers_a)
        assert nearby_users_a.status_code == 200, f"Nearby users fetch failed: {nearby_users_a.text}"
        nearby_list_a = nearby_users_a.json()
        assert isinstance(nearby_list_a, list)
        # Should at least find user B nearby (because we placed B close to A)
        found_user_ids = [loc["user_id"] for loc in nearby_list_a]
        assert user_b_id in found_user_ids

        # --- 8. Fetch nearby users for User B
        nearby_users_b = await client.get(f"/location/nearby/{user_b_id}?radius_km=1", headers=headers_b)
        assert nearby_users_b.status_code == 200, f"Nearby users fetch failed: {nearby_users_b.text}"
        nearby_list_b = nearby_users_b.json()
        assert isinstance(nearby_list_b, list)
        assert user_a_id in [loc["user_id"] for loc in nearby_list_b]

        # --- 9. Try updating location without auth token (should fail)
        no_auth_update = await client.post("/location/update", json=location_payload_a)
        assert no_auth_update.status_code in [401, 403], "Unauthenticated location update should fail"

        # --- 10. Try fetching nearby users without auth token (should fail)
        no_auth_nearby = await client.get(f"/location/nearby/{user_a_id}?radius_km=1")
        assert no_auth_nearby.status_code in [401, 403], "Unauthenticated nearby users fetch should fail"

        # --- 11. Try User B updating location of User A (should fail)
        malicious_payload = {
            "user_id": user_a_id,
            "latitude": 13.0,
            "longitude": 77.0
        }
        malicious_update = await client.post("/location/update", json=malicious_payload, headers=headers_b)
        assert malicious_update.status_code in [403, 400], "User B should not be able to update User A's location"

        # --- 12. Try User A updating invalid coordinates (edge case)
        invalid_location_payload = {
            "user_id": user_a_id,
            "latitude": 9999,
            "longitude": 9999
        }
        invalid_location_update = await client.post("/location/update", json=invalid_location_payload, headers=headers_a)
        assert invalid_location_update.status_code == 422 or invalid_location_update.status_code == 400, "Invalid location data should fail"

        # --- 13. Try fetching nearby with invalid radius
        invalid_radius_response = await client.get(f"/location/nearby/{user_a_id}?radius_km=-5", headers=headers_a)
        assert invalid_radius_response.status_code in [400, 422]

