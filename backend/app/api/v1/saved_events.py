from fastapi import APIRouter, Depends,HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.saved_event import SavedEvent
from pydantic import BaseModel
router = APIRouter()


# Temporary user (until auth exists)
USER_ID = 1


class SaveEventRequest(BaseModel):
    user_id: int
    event_id: str
    event_name: str
    event_date: str
    event_genre: str

@router.post("/")
def save_event(
    data: SaveEventRequest,
    db: Session = Depends(get_db)
):
    existing = (
        db.query(SavedEvent)
        .filter(
            SavedEvent.user_id == data.user_id,
            SavedEvent.event_id == data.event_id
        )
        .first()
    )

    if existing:
        return {"message": "Already saved"}

    saved = SavedEvent(
        user_id=data.user_id,
        event_id=data.event_id,
        event_name=data.event_name,
        event_date=data.event_date,
        event_genre=data.event_genre
    )

    db.add(saved)
    db.commit()

    return {"message": "Event saved"}

@router.get("/{user_id}")
def get_saved_events(user_id: int, db: Session = Depends(get_db)):
    events = (
        db.query(SavedEvent)
        .filter(SavedEvent.user_id == user_id)
        .all()
    )

    return events



@router.delete("/{user_id}/{event_id}")
def unsave_event(user_id: int, event_id: str, db: Session = Depends(get_db)):
    event = (
        db.query(SavedEvent)
        .filter(
            SavedEvent.user_id == user_id,
            SavedEvent.event_id == event_id
        )
        .first()
    )

    if not event:
        raise HTTPException(status_code=404, detail="Not saved")

    db.delete(event)
    db.commit()

    return {"message": "Removed"}




