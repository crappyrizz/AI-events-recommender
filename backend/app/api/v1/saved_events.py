from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.saved_event import SavedEvent
from app.models.event import Event
from pydantic import BaseModel
from app.core.dependancies import get_current_user_id

router = APIRouter()

class SaveEventRequest(BaseModel):
    event_id: str

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
        event_id=data.event_id  # ← removed old fields
    )

    db.add(saved)
    db.commit()

    return {"message": "Event saved"}

@router.get("/")
def get_saved_events(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    saved = (
        db.query(SavedEvent)
        .filter(SavedEvent.user_id == user_id)
        .order_by(SavedEvent.saved_at.desc())
        .all()
    )

    results = []
    for s in saved:
        event = db.query(Event).filter(Event.id == s.event_id).first()
        results.append({
            "id": s.id,
            "event_id": s.event_id,
            "saved_at": s.saved_at,
            "event": event.to_dict() if event else None
        })

    return results

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