# app/tests/test_profile.py

import pytest
import httpx
import uuid

BASE_URL = "http://127.0.0.1:8000"

@pytest.mark.asyncio
async def test_profile_flow():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:

        # --- 1. Register a new user
        random_email = f"user_{uuid.uuid4().hex[:8]}@example.com"
        password = "TestPassword123"
        register_payload = {
            "name": "Test Profile User",
            "email": random_email,
            "password": password
        }
        register_response = await client.post("/auth/register", json=register_payload)
        assert register_response.status_code == 200, f"User registration failed: {register_response.text}"
        user_id = register_response.json()["id"]

        # --- 2. Login to get access token
        login_response = await client.post("/auth/login", params={"email": random_email, "password": password})
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # --- 3. Fetch own profile
        get_profile_response = await client.get(f"/profiles/{user_id}", headers=headers)
        assert get_profile_response.status_code == 200
        profile_data = get_profile_response.json()
        assert profile_data["user_id"] == user_id

        # --- 4. Partial update - bio
        update_payload = {"bio": "This is my new bio"}
        update_response = await client.put(f"/profiles/{user_id}", json=update_payload, headers=headers)
        assert update_response.status_code == 200
        assert update_response.json()["bio"] == "This is my new bio"

        # --- 5. Partial update - country
        update_payload = {"country": "Australia"}
        update_country = await client.put(f"/profiles/{user_id}", json=update_payload, headers=headers)
        assert update_country.status_code == 200
        assert update_country.json()["country"] == "Australia"

        # --- 6. Partial update - avatar
        update_payload = {"avatar_url": "https://example.com/avatar.png"}
        update_avatar = await client.put(f"/profiles/{user_id}", json=update_payload, headers=headers)
        assert update_avatar.status_code == 200
        assert update_avatar.json()["avatar_url"] == "https://example.com/avatar.png"

        # --- 7. Full update
        full_update = {
            "bio": "Full updated bio",
            "country": "Canada",
            "avatar_url": "https://example.com/full.png"
        }
        full_response = await client.put(f"/profiles/{user_id}", json=full_update, headers=headers)
        assert full_response.status_code == 200
        profile_full = full_response.json()
        assert profile_full["bio"] == "Full updated bio"
        assert profile_full["country"] == "Canada"
        assert profile_full["avatar_url"] == "https://example.com/full.png"

        # --- 8. Empty update
        empty_update = await client.put(f"/profiles/{user_id}", json={}, headers=headers)
        assert empty_update.status_code == 200

        # --- 9. Refetch updated profile
        refetch_profile = await client.get(f"/profiles/{user_id}", headers=headers)
        assert refetch_profile.status_code == 200
        refetch_data = refetch_profile.json()
        assert refetch_data["country"] == "Canada"

        # --- 10. Try to fetch profile without token (should fail)
        unauth_fetch = await client.get(f"/profiles/{user_id}")
        assert unauth_fetch.status_code == 401

        # --- 11. Try to update profile without token (should fail)
        unauth_update = await client.put(f"/profiles/{user_id}", json={"bio": "hack"})
        assert unauth_update.status_code == 401

        # --- 12. Try to delete profile without token (should fail)
        unauth_delete = await client.delete(f"/profiles/{user_id}")
        assert unauth_delete.status_code == 401

        # --- 13. Delete own profile
        delete_response = await client.delete(f"/profiles/{user_id}", headers=headers)
        assert delete_response.status_code == 200

        # --- 14. Fetch deleted profile (should 404)
        fetch_deleted = await client.get(f"/profiles/{user_id}", headers=headers)
        assert fetch_deleted.status_code == 404

        # --- 15. Update deleted profile (should 404)
        update_deleted = await client.put(f"/profiles/{user_id}", json={"bio": "fail"}, headers=headers)
        assert update_deleted.status_code == 404

        # --- 16. Delete already deleted profile (should 404)
        delete_again = await client.delete(f"/profiles/{user_id}", headers=headers)
        assert delete_again.status_code == 404

        # --- 17. Register a second user
        second_email = f"user_{uuid.uuid4().hex[:8]}@example.com"
        second_password = "AnotherPass456"
        second_register = await client.post("/auth/register", json={
            "name": "Second User",
            "email": second_email,
            "password": second_password
        })
        assert second_register.status_code == 200
        second_user_id = second_register.json()["id"]

        # --- 18. Login second user
        second_login = await client.post("/auth/login", params={"email": second_email, "password": second_password})
        assert second_login.status_code == 200
        second_token = second_login.json()["access_token"]
        second_headers = {"Authorization": f"Bearer {second_token}"}

        # --- 19. Second user fetches own profile
        second_fetch = await client.get(f"/profiles/{second_user_id}", headers=second_headers)
        assert second_fetch.status_code == 200

        # --- 20. Try second user accessing first user's deleted profile (should 403 or 404)
        second_malicious_fetch = await client.get(f"/profiles/{user_id}", headers=second_headers)
        assert second_malicious_fetch.status_code in [403, 404]

        # --- 21. Try second user updating first user's profile (should 403)
        second_malicious_update = await client.put(f"/profiles/{user_id}", json={"bio": "hacked"}, headers=second_headers)
        assert second_malicious_update.status_code in [403, 404]

        # --- 22. Try second user deleting first user's profile (should 403)
        second_malicious_delete = await client.delete(f"/profiles/{user_id}", headers=second_headers)
        assert second_malicious_delete.status_code in [403, 404]

        # --- 23. Update second user's profile country
        second_country_update = await client.put(f"/profiles/{second_user_id}", json={"country": "USA"}, headers=second_headers)
        assert second_country_update.status_code == 200
        assert second_country_update.json()["country"] == "USA"

        # --- 24. Set empty avatar_url
        empty_avatar = await client.put(f"/profiles/{second_user_id}", json={"avatar_url": ""}, headers=second_headers)
        assert empty_avatar.status_code == 200
        assert empty_avatar.json()["avatar_url"] == ""

        # --- 25. Refetch second user's profile
        refetch_second = await client.get(f"/profiles/{second_user_id}", headers=second_headers)
        assert refetch_second.status_code == 200
        assert refetch_second.json()["country"] == "USA"

        # --- 26. Delete second user's profile
        delete_second = await client.delete(f"/profiles/{second_user_id}", headers=second_headers)
        assert delete_second.status_code == 200
