"""
Event SQLAlchemy model.
Replaces the old dataclass — events are now stored in PostgreSQL.
"""

from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Float, Boolean,
    DateTime, Text, JSON, Integer
)
from app.core.database import Base


class Event(Base):
    __tablename__ = "events"

    # ------------------------------------------------------------------
    # Core identity
    # ------------------------------------------------------------------
    id          = Column(String, primary_key=True, index=True)  # e.g. "E001" or UUID string
    name        = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    genre       = Column(String(100), nullable=True, index=True)
    tags        = Column(JSON, nullable=True)           # e.g. ["live music", "outdoor"]

    # ------------------------------------------------------------------
    # Media
    # ------------------------------------------------------------------
    poster_url    = Column(String(2000), nullable=True)  # main event poster
    thumbnail_url = Column(String(2000), nullable=True)  # smaller card image
    gallery_urls  = Column(JSON, nullable=True)         # list of extra image URLs

    # ------------------------------------------------------------------
    # Ticketing
    # ------------------------------------------------------------------
    ticket_price_min = Column(Float, nullable=True)
    ticket_price_max = Column(Float, nullable=True)
    ticket_price     = Column(Float, nullable=True)     # kept for recommender compatibility
    ticket_url       = Column(String(2000), nullable=True)
    is_free          = Column(Boolean, default=False, nullable=False)
    currency         = Column(String(10), default="KES", nullable=False)

    # ------------------------------------------------------------------
    # Location
    # ------------------------------------------------------------------
    venue_name = Column(String(255), nullable=True)
    address    = Column(String(500), nullable=True)
    city       = Column(String(100), default="Nairobi", nullable=False)
    latitude   = Column(Float, nullable=True)
    longitude  = Column(Float, nullable=True)

    # ------------------------------------------------------------------
    # Timing
    # ------------------------------------------------------------------
    start_datetime = Column(DateTime(timezone=True), nullable=True, index=True)
    end_datetime   = Column(DateTime(timezone=True), nullable=True)
    date           = Column(String(20), nullable=True)  # kept for recommender compatibility e.g "2026-03-10"
    timezone       = Column(String(50), default="Africa/Nairobi", nullable=False)

    # ------------------------------------------------------------------
    # Organizer
    # ------------------------------------------------------------------
    organizer_name     = Column(String(255), nullable=True)
    organizer_url      = Column(String(500), nullable=True)
    organizer_logo_url = Column(String(500), nullable=True)

    # ------------------------------------------------------------------
    # Scraper metadata
    # ------------------------------------------------------------------
    source            = Column(String(50),  nullable=False, default="manual")
    source_url        = Column(String(2000), nullable=True, unique=True)
    scraped_at        = Column(DateTime(timezone=True), nullable=True)
    last_refreshed_at = Column(DateTime(timezone=True), nullable=True)
    is_verified       = Column(Boolean, default=False)

    # ------------------------------------------------------------------
    # Recommender fields
    # ------------------------------------------------------------------
    food_type        = Column(String(100), nullable=True)
    crowd_level      = Column(String(20),  default="MEDIUM", nullable=False)  # LOW|MEDIUM|HIGH
    event_type       = Column(String(20),  default="indoor", nullable=False)  # indoor|outdoor
    popularity_score = Column(Float, default=0.0, nullable=False)

    # ------------------------------------------------------------------
    # Timestamps
    # ------------------------------------------------------------------
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    def __repr__(self):
        return f"<Event id={self.id!r} name={self.name!r} source={self.source!r}>"

    def to_dict(self) -> dict:
        """Serialize event to dictionary for API responses."""
        return {
            "id":          self.id,
            "name":        self.name,
            "description": self.description,
            "genre":       self.genre,
            "tags":        self.tags or [],
            "media": {
                "poster_url":    self.poster_url,
                "thumbnail_url": self.thumbnail_url,
                "gallery_urls":  self.gallery_urls or [],
            },
            "ticketing": {
                "price_min":  self.ticket_price_min,
                "price_max":  self.ticket_price_max,
                "price":      self.ticket_price,
                "ticket_url": self.ticket_url,
                "is_free":    self.is_free,
                "currency":   self.currency,
            },
            "location": {
                "venue_name": self.venue_name,
                "address":    self.address,
                "city":       self.city,
                "latitude":   self.latitude,
                "longitude":  self.longitude,
            },
            "timing": {
                "start":    self.start_datetime.isoformat() if self.start_datetime else None,
                "end":      self.end_datetime.isoformat()   if self.end_datetime   else None,
                "date":     self.date,
                "timezone": self.timezone,
            },
            "organizer": {
                "name":     self.organizer_name,
                "url":      self.organizer_url,
                "logo_url": self.organizer_logo_url,
            },
            "meta": {
                "source":      self.source,
                "source_url":  self.source_url,
                "is_verified": self.is_verified,
                "scraped_at":  self.scraped_at.isoformat() if self.scraped_at else None,
            },
            "recommender": {
                "food_type":        self.food_type,
                "crowd_level":      self.crowd_level,
                "event_type":       self.event_type,
                "popularity_score": self.popularity_score,
            },
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
