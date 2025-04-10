from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.media import save_upload

router = APIRouter(prefix="/media", tags=["Media Uploads"])

@router.post("/upload-avatar/")
async def upload_avatar(file: UploadFile = File(...)):
    path = save_upload(file, subfolder="avatars")
    return {"filename": file.filename, "saved_path": path}

@router.post("/upload-document/")
async def upload_document(file: UploadFile = File(...)):
    path = save_upload(file, subfolder="documents")
    return {"filename": file.filename, "saved_path": path}

@router.post("/upload-chat-media/")
async def upload_chat_media(file: UploadFile = File(...)):
    path = save_upload(file, subfolder="chat_media")
    return {"filename": file.filename, "saved_path": path}
