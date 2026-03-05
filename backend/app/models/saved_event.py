from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class SavedEvent(Base):
    __tablename__ = "saved_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id  = Column(Integer, index=True, nullable=False)
    event_id = Column(String, index=True, nullable=False)   # matches Event.id (String)
    saved_at = Column(DateTime(timezone=True), server_default=func.now())
