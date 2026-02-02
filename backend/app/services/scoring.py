"""
Calculate relevance scores for events based on user preferences.
Uses weighted scoring with budget and genre as primary factors.
"""

from app.utils.distance import haversine_distance
from app.services.context.temporal import TemporalContextService
from app.services.context.weather import WeatherContextService
from app.services.context.crowd import CrowdContextService



class ScoringEngine:
    """Simple weighted scoring for event relevance."""

    # Weight configuration (sum = 1.0)
    WEIGHTS = {
        "budget": 0.30,
        "genre": 0.25,
        "distance": 0.20,
        "food_preference": 0.15,
        "temporal": 0.10,
        "weather": 0.08,  
        "crowd": 0.06,
    }

    def calculate_relevance_score(self, event: dict, user_preferences: dict) -> tuple[float, dict]:
        score_breakdown = {}

        # Budget score
        budget_score = self._score_budget(
            event["ticket_price"],
            user_preferences["budget"],
        )
        score_breakdown["budget"] = {
            "value": budget_score,
            "description": f"Budget match: Event ticket ${event['ticket_price']:.2f} vs budget ${user_preferences['budget']:.2f}",
        }

        # Genre score
        genre_score = self._score_genre(
            event["genre"],
            user_preferences["preferred_genres"],
        )
        score_breakdown["genre"] = {
            "value": genre_score,
            "description": f"Genre match: Event genre '{event['genre']}' vs preferences {user_preferences['preferred_genres']}",
        }

        # Distance score
        distance_km = haversine_distance(
            user_preferences["latitude"],
            user_preferences["longitude"],
            event["latitude"],
            event["longitude"],
        )
        distance_score = self._score_distance(distance_km)
        score_breakdown["distance"] = {
            "value": distance_score,
            "description": f"Location proximity: {distance_km:.1f} km away",
        }

        # Food preference score
        food_score = self._score_food_preference(
            event["food_type"],
            user_preferences["food_preference"],
        )
        score_breakdown["food_preference"] = {
            "value": food_score,
            "description": f"Food preference match: Event food '{event['food_type']}' vs preference '{user_preferences['food_preference']}'",
        }

        # Temporal score (context - aware)
        temporal_score = TemporalContextService.score(event["date"])
        
        score_breakdown["temporal"] = {
            "value": temporal_score,
            "description": f"Event timing relevance based on date ({event['date']})",
        }
        
        # weather score
        weather_score = WeatherContextService.score(
            event.get("event_type", "indoor")
        )
        score_breakdown["weather"] = {
            "value": weather_score,
            "description": f"Weather suitability for event type '{event.get('event_type', 'indoor')}'"
        }
        
        #crowdaware score
        crowd_level = event.get("crowd_level", "MEDIUM")
        base_crowd_score = CrowdContextService.score(crowd_level)

        if user_preferences.get("avoid_crowds"):
            crowd_score = base_crowd_score * 0.7  # stronger penalty
        else:
            crowd_score = base_crowd_score

        score_breakdown["crowd"] = {
            "value": crowd_score,
            "description": (
                f"Crowd level impact: {crowd_level} "
                f"(avoid crowds: {user_preferences.get('avoid_crowds', False)})"
            )
        }


        relevance_score = (
            budget_score * self.WEIGHTS["budget"]
            + genre_score * self.WEIGHTS["genre"]
            + distance_score * self.WEIGHTS["distance"]
            + food_score * self.WEIGHTS["food_preference"]
            + temporal_score * self.WEIGHTS["temporal"]
            + weather_score * self.WEIGHTS["weather"]
            + crowd_score * self.WEIGHTS["crowd"]
        )

        return relevance_score, score_breakdown

    @staticmethod
    def _score_budget(ticket_price: float, user_budget: float) -> float:
        """Score based on budget match."""
        if user_budget <= 0:
            return 0.0

        if ticket_price <= user_budget:
            return 0.6 + (1 - ticket_price / user_budget) * 0.4
        else:
            excess_ratio = min((ticket_price - user_budget) / user_budget, 1.0)
            return max(0.0, 0.3 * (1 - excess_ratio))

    @staticmethod
    def _score_genre(event_genre: str, preferred_genres: list) -> float:
        """Score based on genre match."""
        if not preferred_genres:
            return 0.0

        return 1.0 if event_genre.lower() in [g.lower() for g in preferred_genres] else 0.0

    @staticmethod
    def _score_distance(distance_km: float) -> float:
        """
        Score based on distance.
        - 0–5 km: excellent
        - 5–20 km: good
        - 20–100 km: weak
        - >100 km: very weak
        """
        if distance_km < 0:
            return 0.0

        if distance_km <= 5:
            return 1.0
        elif distance_km <= 20:
            return max(0.4, 1.0 - (distance_km - 5) / 15 * 0.6)
        elif distance_km <= 100:
            return max(0.1, 0.4 - (distance_km - 20) / 80 * 0.3)
        else:
            return max(0.0, 0.1 - (distance_km - 100) / 1000 * 0.1)

    @staticmethod
    def _score_food_preference(event_food: str, user_food_preference: str) -> float:
        """Score based on food preference match."""
        if event_food.lower() == user_food_preference.lower():
            return 1.0
        return 0.2
