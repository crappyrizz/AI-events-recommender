from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class EventInteraction(Base):
    __tablename__ = "event_interactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    event_id = Column(String, nullable=False, index=True)  # matches Event.id (String)
    interaction_type = Column(String, nullable=False)              # INTERESTED | NOT_INTERESTED
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
