# app/tests/test_authentication.py

import pytest
import httpx
import uuid

BASE_URL = "http://127.0.0.1:8000"

@pytest.mark.asyncio
async def test_auth_flow():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:

        # --- 1. Register New User
        random_email = f"user_{uuid.uuid4().hex[:8]}@example.com"
        password = "StrongPassword123"
        register_payload = {
            "name": "Test User",
            "email": random_email,
            "password": password
        }

        register_response = await client.post("/auth/register", json=register_payload)
        assert register_response.status_code == 200, f"Register failed: {register_response.text}"
        registered_user = register_response.json()
        user_id = registered_user["id"]
        assert registered_user["email"] == random_email

        # --- 2. Login with correct credentials
        login_payload = {"email": random_email, "password": password}
        login_response = await client.post("/auth/login", params=login_payload)
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        login_data = login_response.json()
        token = login_data["access_token"]
        assert login_data["token_type"] == "bearer"

        # --- 3. Login with wrong password
        wrong_login_payload = {"email": random_email, "password": "wrongpassword"}
        wrong_login_response = await client.post("/auth/login", params=wrong_login_payload)
        assert wrong_login_response.status_code == 401
        assert "Invalid credentials" in wrong_login_response.text

        # --- 4. Get user by ID (valid token)
        headers = {"Authorization": f"Bearer {token}"}
        user_response = await client.get(f"/auth/user/{user_id}", headers=headers)
        assert user_response.status_code == 200, f"Get user failed: {user_response.text}"
        user_data = user_response.json()
        assert user_data["email"] == random_email

        # --- 5. Get user by ID (wrong id)
        wrong_user_response = await client.get("/auth/user/invalid-id", headers=headers)
        assert wrong_user_response.status_code == 404

        # --- 6. List all users
        users_response = await client.get("/auth/users", headers=headers)
        assert users_response.status_code == 200
        assert isinstance(users_response.json(), list)

        # --- 7. Forget password (existing user)
        forget_password_response = await client.post("/auth/forget-password", params={"email": random_email})
        assert forget_password_response.status_code == 200, f"Forget password failed: {forget_password_response.text}"
        reset_token = forget_password_response.json()["reset_token"]

        # --- 8. Forget password (non-existing user)
        forget_password_invalid = await client.post("/auth/forget-password", params={"email": "nonexistent@example.com"})
        assert forget_password_invalid.status_code == 404

        # --- 9. Change password with valid token
        new_password = "NewPassword456"
        change_password_response = await client.post("/auth/change-password", params={
            "token": reset_token,
            "new_password": new_password
        })
        assert change_password_response.status_code == 200, f"Change password failed: {change_password_response.text}"

        # --- 10. Try login with old password (should fail)
        old_password_login = await client.post("/auth/login", params={"email": random_email, "password": password})
        assert old_password_login.status_code == 401, "Old password login should fail"

        # --- 11. Login with new password (should succeed)
        new_password_login = await client.post("/auth/login", params={"email": random_email, "password": new_password})
        assert new_password_login.status_code == 200, "New password login failed"
        new_login_data = new_password_login.json()
        assert "access_token" in new_login_data

        # --- 12. Change password with wrong reset token
        bad_change_password = await client.post("/auth/change-password", params={
            "token": "invalidtoken123",
            "new_password": "AnotherPassword789"
        })
        assert bad_change_password.status_code == 400, "Bad token should not allow password change"
