from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class EventMedia(Base):
    __tablename__ = "event_media"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, index=True, nullable=False)   # matches Event.id (String)
    user_id  = Column(Integer, index=True, nullable=False)
    file_url = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
