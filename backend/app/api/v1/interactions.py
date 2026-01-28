from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.interaction import EventInteractionCreate
from app.services.interaction_service import log_interaction

router = APIRouter(prefix="/interactions", tags=["Interactions"])


@router.post("/")
def create_interaction(
    interaction: EventInteractionCreate,
    db: Session = Depends(get_db),
):
    return log_interaction(
        db=db,
        user_id=interaction.user_id,
        event_id=interaction.event_id,
        interaction_type=interaction.interaction_type,
    )
