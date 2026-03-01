from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependancies import get_current_user_id
from app.models.event_media import EventMedia
import os
import shutil
from uuid import uuid4

router = APIRouter()

MEDIA_FOLDER = "media"
os.makedirs(MEDIA_FOLDER, exist_ok=True)


@router.post("/{event_id}")
def upload_media(
    event_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    file_ext = file.filename.split(".")[-1]
    filename = f"{uuid4()}.{file_ext}"
    file_path = os.path.join(MEDIA_FOLDER, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    media = EventMedia(
        event_id=event_id,
        user_id=user_id,
        file_url=f"/media/{filename}"
    )

    db.add(media)
    db.commit()

    return {"message": "uploaded", "url": media.file_url}


@router.get("/{event_id}")
def get_event_media(
    event_id: str,
    db: Session = Depends(get_db)
):
    media = db.query(EventMedia).filter(EventMedia.event_id == event_id).all()
    return media