from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.saved_event import SavedEvent

router = APIRouter(prefix="/saved", tags=["Saved"])

# Temporary user (until auth exists)
USER_ID = 1


@router.post("/{event_id}")
def save_event(event_id: str, db: Session = Depends(get_db)):
    existing = (
        db.query(SavedEvent)
        .filter_by(user_id=USER_ID, event_id=event_id)
        .first()
    )

    if existing:
        return {"message": "Already saved"}

    saved = SavedEvent(user_id=USER_ID, event_id=event_id)
    db.add(saved)
    db.commit()

    return {"message": "Saved"}


@router.delete("/{event_id}")
def unsave_event(event_id: str, db: Session = Depends(get_db)):
    db.query(SavedEvent).filter_by(
        user_id=USER_ID, event_id=event_id
    ).delete()

    db.commit()
    return {"message": "Removed"}


@router.get("/")
def get_saved(db: Session = Depends(get_db)):
    events = (
        db.query(SavedEvent)
        .filter_by(user_id=USER_ID)
        .all()
    )

    return [e.event_id for e in events]
