import pytest
import httpx
import os
import uuid
from fastapi import status

BASE_URL = "http://127.0.0.1:8000"

'''
@pytest.mark.asyncio
async def test_upload_avatar():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        # -------- SETUP --------
        file_name = f"avatar_{uuid.uuid4().hex}.png"
        file_path = f"/path/to/your/test/files/{file_name}"  # Replace this with a real file path for testing

        # Open the file to upload
        with open(file_path, "rb") as f:
            files = {"file": (file_name, f, "image/png")}

            # Submit the request to upload the avatar
            response = await client.post("/media/upload-avatar/", files=files)

        # -------- ASSERTIONS --------
        assert response.status_code == 200
        assert "filename" in response.json()
        assert "saved_path" in response.json()
        assert response.json()["filename"] == file_name
        assert os.path.exists(response.json()["saved_path"])  # Ensure the file was saved correctly


@pytest.mark.asyncio
async def test_upload_document():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        # -------- SETUP --------
        file_name = f"document_{uuid.uuid4().hex}.pdf"
        file_path = f"/path/to/your/test/files/{file_name}"  # Replace this with a real file path for testing

        # Open the file to upload
        with open(file_path, "rb") as f:
            files = {"file": (file_name, f, "application/pdf")}

            # Submit the request to upload the document
            response = await client.post("/media/upload-document/", files=files)

        # -------- ASSERTIONS --------
        assert response.status_code == 200
        assert "filename" in response.json()
        assert "saved_path" in response.json()
        assert response.json()["filename"] == file_name
        assert os.path.exists(response.json()["saved_path"])  # Ensure the file was saved correctly


@pytest.mark.asyncio
async def test_upload_chat_media():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        # -------- SETUP --------
        file_name = f"chat_media_{uuid.uuid4().hex}.mp4"
        file_path = f"/path/to/your/test/files/{file_name}"  # Replace this with a real file path for testing

        # Open the file to upload
        with open(file_path, "rb") as f:
            files = {"file": (file_name, f, "video/mp4")}

            # Submit the request to upload the chat media
            response = await client.post("/media/upload-chat-media/", files=files)

        # -------- ASSERTIONS --------
        assert response.status_code == 200
        assert "filename" in response.json()
        assert "saved_path" in response.json()
        assert response.json()["filename"] == file_name
        assert os.path.exists(response.json()["saved_path"])  # Ensure the file was saved correctly


@pytest.mark.asyncio
async def test_upload_invalid_file_format():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        # -------- SETUP --------
        invalid_file_name = f"invalid_{uuid.uuid4().hex}.exe"
        invalid_file_path = f"/path/to/your/test/files/{invalid_file_name}"

        # Open the file to upload (simulating an invalid file format)
        with open(invalid_file_path, "wb") as f:
            f.write(b"Dummy data")

        with open(invalid_file_path, "rb") as f:
            files = {"file": (invalid_file_name, f, "application/x-msdownload")}

            # Submit the request to upload the invalid file format
            response = await client.post("/media/upload-avatar/", files=files)

        # -------- ASSERTIONS --------
        assert response.status_code == 422  # Expect 422 Unprocessable Entity for invalid file format


@pytest.mark.asyncio
async def test_upload_missing_file():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        # Submit the request without a file
        response = await client.post("/media/upload-avatar/")

        # -------- ASSERTIONS --------
        assert response.status_code == 422  # Expect 422 Unprocessable Entity for missing file


@pytest.mark.asyncio
async def test_upload_large_file():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        # -------- SETUP --------
        large_file_name = f"large_{uuid.uuid4().hex}.mp4"
        large_file_path = f"/path/to/your/test/files/{large_file_name}"

        # Create a large file (1GB)
        with open(large_file_path, "wb") as f:
            f.write(b"Dummy data" * 1024 * 1024 * 100)  # Write 100MB of dummy data

        with open(large_file_path, "rb") as f:
            files = {"file": (large_file_name, f, "video/mp4")}

            # Submit the request to upload a large file
            response = await client.post("/media/upload-chat-media/", files=files)

        # -------- ASSERTIONS --------
        assert response.status_code == 413  # Expect 413 Payload Too Large if the file exceeds the allowed size


@pytest.mark.asyncio
async def test_upload_multiple_files():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        # -------- SETUP --------
        file_name_1 = f"avatar_{uuid.uuid4().hex}.png"
        file_name_2 = f"document_{uuid.uuid4().hex}.pdf"
        file_path_1 = f"/path/to/your/test/files/{file_name_1}"  # Replace with real path
        file_path_2 = f"/path/to/your/test/files/{file_name_2}"  # Replace with real path

        # Create files for uploading
        with open(file_path_1, "wb") as f:
            f.write(b"Dummy data")
        with open(file_path_2, "wb") as f:
            f.write(b"Dummy data")

        # Open files to upload
        with open(file_path_1, "rb") as f1, open(file_path_2, "rb") as f2:
            files = {
                "file": [
                    (file_name_1, f1, "image/png"),
                    (file_name_2, f2, "application/pdf")
                ]
            }

            # Submit the request to upload multiple files
            response = await client.post("/media/upload-avatar/", files=files)

        # -------- ASSERTIONS --------
        assert response.status_code == 200
        assert "filename" in response.json()
        assert os.path.exists(response.json()["saved_path"])


@pytest.mark.asyncio
async def test_upload_avatar_with_invalid_auth():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        # -------- SETUP --------
        invalid_token = "invalid_token"

        # Invalid headers with no valid Authorization
        headers_invalid = {"Authorization": f"Bearer {invalid_token}"}

        # -------- TEST: Try upload avatar with invalid auth
        file_name = f"avatar_{uuid.uuid4().hex}.png"
        file_path = f"/path/to/your/test/files/{file_name}"

        with open(file_path, "rb") as f:
            files = {"file": (file_name, f, "image/png")}

            response = await client.post("/media/upload-avatar/", files=files, headers=headers_invalid)

        # -------- ASSERTIONS --------
        assert response.status_code == 401  # Unauthorized should return 401
'''
