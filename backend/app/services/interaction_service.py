from sqlalchemy.orm import Session
from app.models.event_interaction import EventInteraction


def log_interaction(
    db: Session,
    user_id: int,
    event_id: int,
    interaction_type: str,
):
    interaction = EventInteraction(
        user_id=user_id,
        event_id=event_id,
        interaction_type=interaction_type,
    )
    db.add(interaction)
    db.commit()
    db.refresh(interaction)
    return interaction
