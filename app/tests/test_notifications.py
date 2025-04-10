# app/tests/test_notifications.py

import pytest
import httpx
import uuid

BASE_URL = "http://127.0.0.1:8000"


@pytest.mark.asyncio
async def test_notifications_flow():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:

        # -------- Setup: Register a user --------
        email = f"user_{uuid.uuid4().hex[:8]}@example.com"
        password = "SecurePassword123"
        register = await client.post("/auth/register", json={"name": "Notification Tester", "email": email, "password": password})
        assert register.status_code == 200
        user_id = register.json()["id"]

        login = await client.post("/auth/login", params={"email": email, "password": password})
        assert login.status_code == 200
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # --------- Tests: Sending Notifications ---------

        # 1. Create a notification
        notification_payload = {
            "user_id": user_id,
            "title": "New Match Request",
            "message": "Someone nearby wants to connect!",
            "notification_type": "system"
        }
        create_notif = await client.post("/notifications/", json=notification_payload, headers=headers)
        assert create_notif.status_code == 200
        notif_data = create_notif.json()
        assert notif_data["title"] == "New Match Request"
        assert notif_data["is_read"] is False

        notification_id = notif_data["notification_id"]

        # 2. Try creating notification without auth (should succeed if allowed)
        unauth_notif = await client.post("/notifications/", json=notification_payload)
        assert unauth_notif.status_code == 200

        # 3. Create another notification
        second_payload = {
            "user_id": user_id,
            "title": "Reminder",
            "message": "Don't miss your pending matches!",
            "notification_type": "system"
        }
        create_second = await client.post("/notifications/", json=second_payload, headers=headers)
        assert create_second.status_code == 200

        # --------- Tests: Listing Notifications ---------

        # 4. Fetch notifications list
        notifications = await client.get(f"/notifications/{user_id}", headers=headers)
        assert notifications.status_code == 200
        notif_list = notifications.json()
        assert isinstance(notif_list, list)
        assert len(notif_list) >= 2

        # 5. Unauthorized notification list access
        unauth_list = await client.get(f"/notifications/{user_id}")
        assert unauth_list.status_code == 200  # assuming public allowed

        # 6. Fetch notifications for random user
        random_user_fetch = await client.get(f"/notifications/{uuid.uuid4()}", headers=headers)
        assert random_user_fetch.status_code == 200
        assert isinstance(random_user_fetch.json(), list)
        assert len(random_user_fetch.json()) == 0

        # --------- Tests: Marking as Read ---------

        # 7. Mark a notification as read
        mark_read = await client.post(f"/notifications/mark-read/{notification_id}", headers=headers)
        assert mark_read.status_code == 200
        read_data = mark_read.json()
        assert read_data["is_read"] is True

        # 8. Try marking the same notification again
        re_mark = await client.post(f"/notifications/mark-read/{notification_id}", headers=headers)
        assert re_mark.status_code == 200
        assert re_mark.json()["is_read"] is True

        # 9. Mark a non-existing notification
        fake_mark = await client.post(f"/notifications/mark-read/{uuid.uuid4()}", headers=headers)
        assert fake_mark.status_code == 404

        # 10. Invalid UUID for mark-read
        invalid_uuid_mark = await client.post("/notifications/mark-read/notauuid", headers=headers)
        assert invalid_uuid_mark.status_code in [404]

        # --------- Special use-cases for matchmaking ---------

        # 11. Simulate "match request notification" for nearby users
        email_b = f"userb_{uuid.uuid4().hex[:8]}@example.com"
        register_b = await client.post("/auth/register", json={"name": "Nearby User", "email": email_b, "password": "PasswordB123"})
        assert register_b.status_code == 200
        user_b_id = register_b.json()["id"]

        match_alert = {
            "user_id": user_b_id,
            "title": "Help Matchmaking",
            "message": f"Please help match {user_id}!",
            "notification_type": "session"
        }
        create_alert = await client.post("/notifications/", json=match_alert, headers=headers)
        assert create_alert.status_code == 200

        # 12. Fetch user B's notifications
        login_b = await client.post("/auth/login", params={"email": email_b, "password": "PasswordB123"})
        token_b = login_b.json()["access_token"]
        headers_b = {"Authorization": f"Bearer {token_b}"}

        b_notifications = await client.get(f"/notifications/{user_b_id}", headers=headers_b)
        assert b_notifications.status_code == 200
        assert len(b_notifications.json()) >= 1
        titles = [notif["title"] for notif in b_notifications.json()]
        assert "Help Matchmaking" in titles

        # 13. Mark user B's notification as read
        notif_b_id = b_notifications.json()[0]["notification_id"]
        b_read = await client.post(f"/notifications/mark-read/{notif_b_id}", headers=headers_b)
        assert b_read.status_code == 200
        assert b_read.json()["is_read"] is True

        # --------- More Negative Edge Cases ---------

        # 14. Send notification with missing fields
        incomplete_payload = {
            "user_id": user_id,
            "title": "Missing Content"
            # Missing message and notification_type
        }
        incomplete_send = await client.post("/notifications/", json=incomplete_payload, headers=headers)
        assert incomplete_send.status_code == 422

        # 15. Try sending notification with invalid user_id
        bad_user_id_send = await client.post("/notifications/", json={
            "user_id": "notauuid",
            "title": "Bad Data",
            "message": "Invalid user id format",
            "notification_type": "system"
        }, headers=headers)
        assert bad_user_id_send.status_code in [422, 200, 400]

        # 16. Try reading notification without auth (optional)
        unauth_read = await client.post(f"/notifications/mark-read/{notification_id}")
        assert unauth_read.status_code in [200, 401, 403]
