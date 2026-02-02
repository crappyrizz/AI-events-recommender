from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.crowd import CrowdEstimator

router = APIRouter(
    prefix="/crowd",
    tags=["Crowd"],
)


@router.get("/{event_id}")
def get_event_crowd(event_id: int, db: Session = Depends(get_db)):
    """
    Get estimated crowd level for a given event.
    """
    estimator = CrowdEstimator(db)
    return estimator.estimate_crowd(event_id)
