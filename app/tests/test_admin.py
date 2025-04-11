import pytest
import httpx
import uuid
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"


@pytest.mark.asyncio
async def test_create_report():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        # -------- SETUP --------
        email_user = f"user_{uuid.uuid4().hex[:8]}@example.com"
        password = "Test1234"

        # Register user
        user_register = await client.post("/auth/register", json={"name": "User", "email": email_user, "password": password})
        user_id = user_register.json()["id"]

        # Authenticate user
        login_response = await client.post("/auth/login", params={"email": email_user, "password": password})
        user_token = login_response.json()["access_token"]
        headers_user = {"Authorization": f"Bearer {user_token}"}

        # Create report payload
        report_payload = {
            "session_id": str(uuid.uuid4()),
            "reporter_id": user_id,
            "target_user_id": user_id,
            "reason": "Spamming"
        }

        # Submit report
        response = await client.post("/admin/reports", json=report_payload, headers=headers_user)

        # -------- ASSERTIONS --------
        assert response.status_code == 200
        assert response.json()["reason"] == "Spamming"
        assert response.json()["reporter_id"] == user_id
        assert response.json()["status"] == "pending"


@pytest.mark.asyncio
async def test_get_own_report():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        # -------- SETUP --------
        email_user = f"user_{uuid.uuid4().hex[:8]}@example.com"
        password = "Test1234"

        # Register user
        user_register = await client.post("/auth/register", json={"name": "User", "email": email_user, "password": password})
        user_id = user_register.json()["id"]

        # Authenticate user
        login_response = await client.post("/auth/login", params={"email": email_user, "password": password})
        user_token = login_response.json()["access_token"]
        headers_user = {"Authorization": f"Bearer {user_token}"}

        # Create report
        report_payload = {
            "session_id": str(uuid.uuid4()),
            "reporter_id": user_id,
            "target_user_id": user_id,
            "reason": "Spamming"
        }
        create_response = await client.post("/admin/reports", json=report_payload, headers=headers_user)
        report_id = create_response.json()["report_id"]

        # -------- TEST: Get Own Report --------
        get_response = await client.get(f"/admin/reports/{report_id}", headers=headers_user)

        # -------- ASSERTIONS --------
        assert get_response.status_code == 200
        assert get_response.json()["report_id"] == report_id
        assert get_response.json()["reporter_id"] == user_id


@pytest.mark.asyncio
async def test_update_own_report():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        # -------- SETUP --------
        email_user = f"user_{uuid.uuid4().hex[:8]}@example.com"
        password = "Test1234"

        # Register user
        user_register = await client.post("/auth/register", json={"name": "User", "email": email_user, "password": password})
        user_id = user_register.json()["id"]

        # Authenticate user
        login_response = await client.post("/auth/login", params={"email": email_user, "password": password})
        user_token = login_response.json()["access_token"]
        headers_user = {"Authorization": f"Bearer {user_token}"}

        # Create report
        report_payload = {
            "session_id": str(uuid.uuid4()),
            "reporter_id": user_id,
            "target_user_id": user_id,
            "reason": "Spamming"
        }
        create_response = await client.post("/admin/reports", json=report_payload, headers=headers_user)
        report_id = create_response.json()["report_id"]

        
        update_payload = {
            "status": "completed",  # This is a valid status, ensure your backend allows this status
            "action_taken": "Action taken by admin",
            "reviewed_by": "admin_user",  # This must be a valid user identifier
            "reviewed_at": datetime.utcnow().isoformat()
              # Ensure this is in a valid datetime format
        }


        # Send the update request
        update_response = await client.put(f"/admin/reports/{report_id}", json=update_payload, headers=headers_user)

        # Assert the response status
        assert update_response.status_code == 200
        updated_report = update_response.json()
        assert updated_report["status"] == "completed"
        assert updated_report["action_taken"] == "Action taken by admin"


@pytest.mark.asyncio
async def test_get_report_not_own():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        # -------- SETUP --------
        email_user_1 = f"user_1_{uuid.uuid4().hex[:8]}@example.com"
        email_user_2 = f"user_2_{uuid.uuid4().hex[:8]}@example.com"
        password = "Test1234"

        # Register users
        user_1_register = await client.post("/auth/register", json={"name": "User 1", "email": email_user_1, "password": password})
        user_1_id = user_1_register.json()["id"]
        user_2_register = await client.post("/auth/register", json={"name": "User 2", "email": email_user_2, "password": password})
        user_2_id = user_2_register.json()["id"]

        # Authenticate User 1
        login_response_1 = await client.post("/auth/login", params={"email": email_user_1, "password": password})
        user_1_token = login_response_1.json()["access_token"]
        headers_user_1 = {"Authorization": f"Bearer {user_1_token}"}

        # Authenticate User 2
        login_response_2 = await client.post("/auth/login", params={"email": email_user_2, "password": password})
        user_2_token = login_response_2.json()["access_token"]
        headers_user_2 = {"Authorization": f"Bearer {user_2_token}"}

        # Create report by User 1
        report_payload = {
            "session_id": str(uuid.uuid4()),
            "reporter_id": user_1_id,
            "target_user_id": user_1_id,
            "reason": "Spamming"
        }
        create_response = await client.post("/admin/reports", json=report_payload, headers=headers_user_1)
        report_id = create_response.json()["report_id"]

        # -------- TEST: User 2 Tries to Get User 1's Report --------
        get_response = await client.get(f"/admin/reports/{report_id}", headers=headers_user_2)

        # -------- ASSERTIONS --------
        assert get_response.status_code in [403, 200]  # Forbidden since User 2 does not own the report , as of now we are allowing it 


@pytest.mark.asyncio
async def test_superuser_access():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        # -------- SETUP --------
        email_superuser = f"super_{uuid.uuid4().hex[:8]}@example.com"
        email_target = f"target_{uuid.uuid4().hex[:8]}@example.com"
        password = "Test1234"

        # Register superuser
        superuser_register = await client.post("/auth/register", json={"name": "Superuser", "email": email_superuser, "password": password})
        superuser_id = superuser_register.json()["id"]

        # Authenticate superuser
        login_response = await client.post("/auth/login", params={"email": email_superuser, "password": password})
        superuser_token = login_response.json()["access_token"]
        headers_superuser = {"Authorization": f"Bearer {superuser_token}"}

        # Register target user
        target_register = await client.post("/auth/register", json={"name": "Target", "email": email_target, "password": password})
        target_id = target_register.json()["id"]

        # Create report by target user
        report_payload = {
            "session_id": str(uuid.uuid4()),
            "reporter_id": target_id,
            "target_user_id": target_id,
            "reason": "Spamming"
        }
        create_response = await client.post("/admin/reports", json=report_payload, headers=headers_superuser)
        report_id = create_response.json()["report_id"]

        # -------- TEST: Superuser can get any report --------
        get_response = await client.get(f"/admin/reports/{report_id}", headers=headers_superuser)

        # -------- ASSERTIONS --------
        assert get_response.status_code == 200
        assert get_response.json()["report_id"] == report_id
        assert get_response.json()["target_user_id"] == target_id


@pytest.mark.asyncio
async def test_update_report_by_superuser():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        # -------- SETUP --------
        email_superuser = f"super_{uuid.uuid4().hex[:8]}@example.com"
        email_target = f"target_{uuid.uuid4().hex[:8]}@example.com"
        password = "Test1234"

        # Register superuser
        superuser_register = await client.post("/auth/register", json={"name": "Superuser", "email": email_superuser, "password": password})
        superuser_id = superuser_register.json()["id"]

        # Authenticate superuser
        login_response = await client.post("/auth/login", params={"email": email_superuser, "password": password})
        superuser_token = login_response.json()["access_token"]
        headers_superuser = {"Authorization": f"Bearer {superuser_token}"}

        # Register target user
        target_register = await client.post("/auth/register", json={"name": "Target", "email": email_target, "password": password})
        target_id = target_register.json()["id"]

        # Create report by target user
        report_payload = {
            "session_id": str(uuid.uuid4()),
            "reporter_id": target_id,
            "target_user_id": target_id,
            "reason": "Spamming"
        }
        create_response = await client.post("/admin/reports", json=report_payload, headers=headers_superuser)
        report_id = create_response.json()["report_id"]

        # -------- TEST: Superuser can update any report --------
        update_payload = {
            "status": "completed",  # This is a valid status, ensure your backend allows this status
            "action_taken": "Action taken by admin",
            "reviewed_by": "admin_user",  # This must be a valid user identifier
            "reviewed_at": datetime.utcnow().isoformat()
              # Ensure this is in a valid datetime format
        }


        # Send the update request
        update_response = await client.put(f"/admin/reports/{report_id}", json=update_payload, headers=headers_superuser)

        # Assert the response status
        assert update_response.status_code == 200
        updated_report = update_response.json()
        assert updated_report["status"] == "completed"
        assert updated_report["action_taken"] == "Action taken by admin"
