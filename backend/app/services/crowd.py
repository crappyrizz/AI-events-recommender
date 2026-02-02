from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.event_interaction import EventInteraction


class CrowdEstimator:
    """
    Estimates how crowded an event is based on user interest signals.
    """

    def __init__(self, db: Session):
        self.db = db

    def estimate_crowd(self, event_id: int) -> dict:
        interest_count = (
            self.db.query(func.count(EventInteraction.id))
            .filter(
                EventInteraction.event_id == event_id,
                EventInteraction.interaction_type == "INTERESTED",
            )
            .scalar()
        )

        crowd_score = min(interest_count / 50, 1.0)

        if crowd_score < 0.3:
            level = "LOW"
        elif crowd_score < 0.6:
            level = "MEDIUM"
        else:
            level = "HIGH"

        return {
            "score": round(crowd_score, 2),
            "level": level,
            "interest_count": interest_count,
        }
