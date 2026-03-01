from fastapi import APIRouter, Depends,HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.saved_event import SavedEvent
from pydantic import BaseModel
from app.core.dependancies import get_current_user_id
router = APIRouter()





class SaveEventRequest(BaseModel):
    event_id: str
    event_name: str
    event_date: str
    event_genre: str

@router.post("/")
def save_event(
    data: SaveEventRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    existing = (
        db.query(SavedEvent)
        .filter(
            SavedEvent.user_id == user_id,
            SavedEvent.event_id == data.event_id
        )
        .first()
    )

    if existing:
        return {"message": "Already saved"}

    saved = SavedEvent(
        user_id=user_id,
        event_id=data.event_id,
        event_name=data.event_name,
        event_date=data.event_date,
        event_genre=data.event_genre
    )

    db.add(saved)
    db.commit()

    return {"message": "Event saved"}

@router.get("/")
def get_saved_events(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    events = (
        db.query(SavedEvent)
        .filter(SavedEvent.user_id == user_id)
        .all()
    )

    return events



@router.delete("/{event_id}")
def unsave_event(
    event_id: str,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
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




