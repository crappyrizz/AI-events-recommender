from pydantic import BaseModel
from typing import List


class UserPreferences(BaseModel):
    budget: float
    preferred_genres: List[str]
    latitude: float
    longitude: float
    food_preference: str
    avoid_crowds: bool = False


class RecommendationRequest(BaseModel):
    user_id: int
    preferences: UserPreferences
