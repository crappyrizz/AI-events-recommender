from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.core.database import Base


class SavedEvent(Base):
    __tablename__ = "saved_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    event_id = Column(String, index=True)
    saved_at = Column(DateTime, default=datetime.utcnow)
