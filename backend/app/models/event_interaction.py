from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base


class EventInteraction(Base):
    __tablename__ = "event_interactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    event_id = Column(Integer, nullable=False)
    interaction_type = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
