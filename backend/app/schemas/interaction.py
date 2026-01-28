from pydantic import BaseModel


class EventInteractionCreate(BaseModel):
    user_id: int
    event_id: int
    interaction_type: str
