from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.core.database import Base


class SavedEvent(Base):
    __tablename__ = "saved_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    event_id = Column(String, index=True)
    event_name = Column(String)
    event_date = Column(String)
    event_genre = Column(String)
