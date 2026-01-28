"""
User data model.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class User:
    """Represents a user with preferences for event recommendations."""
    id: str
    name: str
    budget: float
    preferred_genres: List[str]
    latitude: float
    longitude: float
    food_preference: str
    
    def to_preferences_dict(self) -> dict:
        """Convert user to preferences dictionary for recommendation engine."""
        return {
            'budget': self.budget,
            'preferred_genres': self.preferred_genres,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'food_preference': self.food_preference
        }
