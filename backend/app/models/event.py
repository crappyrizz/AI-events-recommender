"""
Event data model.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Event:
    """Represents an event with relevant attributes."""
    id: str
    name: str
    genre: str
    ticket_price: float
    latitude: float
    longitude: float
    food_type: str
    date: str
    description: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert event to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'genre': self.genre,
            'ticket_price': self.ticket_price,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'food_type': self.food_type,
            'date': self.date,
            'description': self.description
        }
