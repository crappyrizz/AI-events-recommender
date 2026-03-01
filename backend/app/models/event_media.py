from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.core.database import Base

class EventMedia(Base):
    __tablename__ = "event_media"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, index=True)
    user_id = Column(Integer, index=True)
    file_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)