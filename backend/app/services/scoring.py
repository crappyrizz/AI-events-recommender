"""
Calculate relevance scores for events based on user preferences.
Uses weighted scoring across budget, genre, distance, food, temporal, weather, and crowd.
"""

from app.utils.distance import haversine_distance
from app.services.context.temporal import TemporalContextService
from app.services.context.weather import WeatherContextService
from app.services.context.crowd import CrowdContextService


class ScoringEngine:
    """Weighted multi-factor scoring engine for event relevance."""

    # Default weights — must roughly sum to 1.0
    WEIGHTS = {
        "budget":          0.20,
        "genre":           0.40,  # ← up from 0.30
        "distance":        0.20,
        "food_preference": 0.08,  # ← down from 0.15
        "temporal":        0.07,  # ← down from 0.10
        "weather":         0.03,  # ← down from 0.08
        "crowd":           0.02,  # ← down from 0.06
    }

    def calculate_relevance_score(
        self,
        event: dict,
        user_preferences: dict,
        weights: dict | None = None,
    ) -> tuple[float, dict]:
        """
        Compute a weighted relevance score for a single event.

        Args:
            event: Event dictionary (must include ticket_price, genre, latitude,
                   longitude, food_type, date, event_type, crowd_level).
            user_preferences: User preferences (budget, preferred_genres,
                              latitude, longitude, food_preference, avoid_crowds).
            weights: Optional weight overrides. Falls back to WEIGHTS.

        Returns:
            Tuple of (relevance_score: float, score_breakdown: dict).
        """
        weights = weights or self.WEIGHTS
        score_breakdown = {}

        # --- Budget ---
        budget_score = self._score_budget(
            event["ticket_price"],
            user_preferences.get("budget") or 0,
        )
        score_breakdown["budget"] = {
            "value": budget_score,
            "description": (
                f"Budget match: ticket ${event['ticket_price']:.2f} "
                f"vs budget ${user_preferences.get('budget', 0):.2f}"
            ),
        }

        # --- Genre ---
        genre_score = self._score_genre(
            event["genre"],
            user_preferences.get("preferred_genres") or [],
        )
        score_breakdown["genre"] = {
            "value": genre_score,
            "description": (
                f"Genre match: '{event['genre']}' "
                f"vs preferences {user_preferences.get('preferred_genres', [])}"
            ),
        }

        # --- Distance ---
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

        # --- Food preference ---
        food_score = self._score_food_preference(
            event.get("food_type", ""),
            user_preferences.get("food_preference", ""),
        )
        score_breakdown["food_preference"] = {
            "value": food_score,
            "description": (
                f"Food match: event '{event.get('food_type', 'none')}' "
                f"vs preference '{user_preferences.get('food_preference', 'none')}'"
            ),
        }

        # --- Temporal ---
        temporal_score = TemporalContextService.score(event["date"])
        score_breakdown["temporal"] = {
            "value": temporal_score,
            "description": f"Event timing relevance ({event['date']})",
        }

        # --- Weather ---
        event_type = event.get("event_type", "indoor")
        weather_score = WeatherContextService.score(event_type)
        score_breakdown["weather"] = {
            "value": weather_score,
            "description": f"Weather suitability for '{event_type}' event",
        }

        # --- Crowd ---
        crowd_level = event.get("crowd_level", "MEDIUM")
        base_crowd_score = CrowdContextService.score(crowd_level)
        avoid_crowds = user_preferences.get("avoid_crowds", False)
        crowd_score = base_crowd_score * 0.7 if avoid_crowds else base_crowd_score
        score_breakdown["crowd"] = {
            "value": crowd_score,
            "description": (
                f"Crowd level: {crowd_level} "
                f"(avoid crowds: {avoid_crowds})"
            ),
        }

        # --- Weighted total ---
        relevance_score = (
            budget_score       * weights.get("budget", 0)
            + genre_score      * weights.get("genre", 0)
            + distance_score   * weights.get("distance", 0)
            + food_score       * weights.get("food_preference", 0)
            + temporal_score   * weights.get("temporal", 0)
            + weather_score    * weights.get("weather", 0)
            + crowd_score      * weights.get("crowd", 0)
        )

        return relevance_score, score_breakdown
    

    # ------------------------------------------------------------------
    # Individual scoring methods
    # ------------------------------------------------------------------

    @staticmethod
    def _score_budget(ticket_price: float, user_budget: float) -> float:
        """
        Score budget compatibility.
        - Within budget: 0.6–1.0 (better score the cheaper the ticket relative to budget)
        - Over budget: 0.0–0.3 (penalised proportionally to how far over)
        - Zero or null budget: 0.0
        """
        if not user_budget or user_budget <= 0:
            return 0.0

        if ticket_price <= user_budget:
            return 0.6 + (1.0 - ticket_price / user_budget) * 0.4

        excess_ratio = min((ticket_price - user_budget) / user_budget, 1.0)
        return max(0.0, 0.3 * (1.0 - excess_ratio))

    @staticmethod
    def _score_genre(event_genre: str, preferred_genres: list) -> float:
        """
        Score genre match.
        - Exact match (case-insensitive): 1.0
        - No match or no preferences: 0.0
        """
        if not preferred_genres or not event_genre:
            return 0.0

        return 1.0 if event_genre.lower() in [g.lower() for g in preferred_genres] else 0.0

    @staticmethod
    def _score_distance(distance_km: float) -> float:
        """
        Score based on distance to event.
        - 0–5 km:    1.0        (excellent)
        - 5–20 km:   0.4–1.0   (good)
        - 20–100 km: 0.1–0.4   (weak)
        - >100 km:   0.0–0.1   (very weak)
        """
        if distance_km < 0:
            return 0.0
        if distance_km <= 5:
            return 1.0
        if distance_km <= 20:
            return max(0.4, 1.0 - (distance_km - 5) / 15 * 0.6)
        if distance_km <= 100:
            return max(0.1, 0.4 - (distance_km - 20) / 80 * 0.3)
        return max(0.0, 0.1 - (distance_km - 100) / 1000 * 0.1)

    @staticmethod
    def _score_food_preference(event_food: str, user_food_preference: str) -> float:
        """
        Score food preference match.
        - Exact match: 1.0
        - User wants 'any' food: 0.8
        - No match: 0.2
        - Missing data on either side: 0.2
        """
        if not event_food or not user_food_preference:
            return 0.2

        event_food_lower = event_food.lower().strip()
        user_pref_lower = user_food_preference.lower().strip()

        if user_pref_lower == "any":
            return 0.8

        if event_food_lower == user_pref_lower:
            return 1.0

        return 0.2
