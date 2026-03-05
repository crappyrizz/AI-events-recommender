"""
Content-based event recommendation engine.
Loads events from PostgreSQL and ranks them using weighted relevance scoring.
"""

from typing import List, Dict

from app.services.scoring import ScoringEngine
from app.services.learning.user_profile import UserPreferenceProfile


class EventRecommender:
    """Recommends events based on user preferences using content-based scoring."""

    def __init__(self, db=None):
        """
        Args:
            db: SQLAlchemy session. Required for loading events and user profiles.
        """
        self.db = db
        self.scoring_engine = ScoringEngine()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def recommend(
        self,
        user_preferences: dict,
        user_id: int | None = None,
        sort_by: str = "best",
        top_n: int = 10,
        max_distance_km: float | None = None,
        weights: dict | None = None,
    ) -> List[Dict]:
        """
        Recommend events based on user preferences.

        Args:
            user_preferences: Must include budget, preferred_genres,
                              latitude, longitude, food_preference.
            user_id: Optional — loads personalisation profile when provided.
            sort_by: "best" | "distance" | "budget" | "crowd"
            top_n: Maximum number of results to return.
            max_distance_km: Hard distance cap in km (None = no cap).
            weights: Override scoring weights.

        Returns:
            List of recommendation dicts with event, relevance_score,
            distance_km, explanation, and score_breakdown.
        """
        from app.utils.distance import haversine_distance
        from app.models.event import Event

        # --- Load events from DB ---
        events = self.db.query(Event).all()

        if not events:
            return []

        # --- Optionally load user profile ---
        profile = None
        if user_id and self.db:
            try:
                profile = UserPreferenceProfile(self.db, user_id)
            except Exception as e:
                print(f"[Recommender] Could not load user profile: {e}")

        recommendations = []

        for event in events:
            # Skip events with missing location
            if event.latitude is None or event.longitude is None:
                continue

            distance = haversine_distance(
                user_preferences["latitude"],
                user_preferences["longitude"],
                event.latitude,
                event.longitude,
            )

            # Hard distance cap
            if max_distance_km is not None and distance > max_distance_km:
                continue

            # Convert Event model to dict for scoring engine
            event_dict = {
                "id":           event.id,
                "name":         event.name,
                "genre":        event.genre or "",
                "ticket_price": event.ticket_price or 0.0,
                "latitude":     event.latitude,
                "longitude":    event.longitude,
                "food_type":    event.food_type or "",
                "date":         event.date or "",
                "event_type":   event.event_type or "indoor",
                "crowd_level":  event.crowd_level or "MEDIUM",
                "description":  event.description or "",
            }

            relevance_score, score_breakdown = self.scoring_engine.calculate_relevance_score(
                event_dict, user_preferences, weights=weights
            )

            # --- Personalisation adjustments ---
            if profile:
                genre_bias = profile.genre_bias.get(event.genre, 0)
                relevance_score += genre_bias * 0.05

                if "crowd" in score_breakdown:
                    relevance_score += profile.crowd_bias

            if relevance_score > 0.0:
                explanation = self._generate_explanation(score_breakdown, relevance_score)
                recommendations.append({
                    "event": {
                        "id":        event.id,
                        "name":      event.name,
                        "date":      event.date,
                        "genre":     event.genre,
                        "latitude":  event.latitude,
                        "longitude": event.longitude,
                        "media": {
                            "poster_url":    event.poster_url,
                            "thumbnail_url": event.thumbnail_url,
                        },
                        "ticketing": {
                            "price":      event.ticket_price,
                            "is_free":    event.is_free,
                            "ticket_url": event.ticket_url,
                            "currency":   event.currency,
                        },
                        "location": {
                            "venue_name": event.venue_name,
                            "address":    event.address,
                            "city":       event.city,
                        },
                        "is_verified": event.is_verified,
                    },
                    "relevance_score": round(relevance_score, 3),
                    "distance_km":     round(distance, 1),
                    "explanation":     explanation,
                    "score_breakdown": score_breakdown,
                })

        # --- Minimum score filter ---
        MIN_SCORE = 0.4
        recommendations = [r for r in recommendations if r["relevance_score"] >= MIN_SCORE]

        if not recommendations:
            return []

        # --- Sort ---
        recommendations = self._sort(recommendations, sort_by)

        return recommendations[:top_n]

    # ------------------------------------------------------------------
    # Sorting
    # ------------------------------------------------------------------

    @staticmethod
    def _sort(recommendations: List[Dict], sort_by: str) -> List[Dict]:
        if sort_by == "distance":
            return sorted(recommendations, key=lambda x: x["distance_km"])

        if sort_by == "budget":
            return sorted(
                recommendations,
                key=lambda x: x["score_breakdown"].get("budget", {}).get("value", 0),
                reverse=True,
            )

        if sort_by == "crowd" and "crowd" in recommendations[0]["score_breakdown"]:
            return sorted(
                recommendations,
                key=lambda x: x["score_breakdown"].get("crowd", {}).get("value", 0),
                reverse=True,
            )

        # Default: "best" — tiered by distance band then score
        def distance_tier(distance: float) -> int:
            if distance <= 50:
                return 0
            if distance <= 200:
                return 1
            return 2

        return sorted(
            recommendations,
            key=lambda x: (
                distance_tier(x["distance_km"]),
                -x["relevance_score"],
                x["distance_km"],
            ),
        )

    # ------------------------------------------------------------------
    # Explanation
    # ------------------------------------------------------------------

    def _generate_explanation(self, score_breakdown: dict, total_score: float) -> str:
        weights = ScoringEngine.WEIGHTS

        contributions = [
            {
                "factor":       factor,
                "contribution": data["value"] * weights.get(factor, 0),
                "description":  data["description"],
            }
            for factor, data in score_breakdown.items()
        ]

        contributions.sort(key=lambda x: x["contribution"], reverse=True)
        return " | ".join(f["description"] for f in contributions[:3])

    # ------------------------------------------------------------------
    # Static helpers
    # ------------------------------------------------------------------

    @staticmethod
    def apply_crowd_modifier(score: float, crowd_level: str, avoid_crowds: bool) -> float:
        if not avoid_crowds:
            return score
        if crowd_level == "HIGH":
            return score * 0.6
        if crowd_level == "MEDIUM":
            return score * 0.85
        return score * 1.05
