import os
from fastapi import UploadFile
from uuid import uuid4

UPLOAD_DIR = "uploads"

def save_upload(file: UploadFile, subfolder: str = "") -> str:
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

    if subfolder:
        full_dir = os.path.join(UPLOAD_DIR, subfolder)
        os.makedirs(full_dir, exist_ok=True)
    else:
        full_dir = UPLOAD_DIR

    filename = f"{uuid4().hex}_{file.filename}"
    file_path = os.path.join(full_dir, filename)

    with open(file_path, "wb") as f:
        content = file.file.read()
        f.write(content)

    return file_path
