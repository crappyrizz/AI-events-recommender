"""
Content-based event recommendation engine.
Loads events from CSV and ranks them using weighted relevance scoring.
"""

import csv
import os
from typing import List, Dict
from pathlib import Path

from app.services.scoring import ScoringEngine
from app.services.context.temporal import TemporalContextService
from app.services.context.weather import WeatherContextService
from app.services.context.crowd import CrowdContextService
from app.services.learning.user_profile import UserPreferenceProfile


class EventRecommender:
    """Recommends events based on user preferences using content-based scoring."""

    def __init__(self, events_csv_path: str, db=None):
        """
        Initialize the recommender with event data.

        Args:
            events_csv_path: Path to the events CSV file (used as fallback label only).
            db: Optional database session for user profile loading.
        """
        self.events_csv_path = events_csv_path
        self.db = db
        self.scoring_engine = ScoringEngine()
        self.events = []
        self._load_events()

    # ------------------------------------------------------------------
    # Data loading
    # ------------------------------------------------------------------

    def _load_events(self) -> None:
        """Load and normalise events from the CSV file."""
        base_dir = Path(__file__).resolve().parent.parent
        csv_path = base_dir / "data" / "events_seed.csv"

        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"Events CSV file not found: {csv_path}")

        self.events = []
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                event = {
                    "id": row["id"],
                    "name": row["name"],
                    "genre": row["genre"],
                    "ticket_price": float(row["ticket_price"]),
                    "latitude": float(row["latitude"]),
                    "longitude": float(row["longitude"]),
                    "food_type": row.get("food_type", ""),
                    "date": row["date"],
                    "description": row.get("description", ""),
                    "event_type": row.get("event_type", "indoor"),
                    "crowd_level": row.get("crowd_level", "MEDIUM"),
                }
                self.events.append(event)

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
            max_distance_km: Hard distance cap (None = no cap).
            weights: Override scoring weights (defaults to ScoringEngine.WEIGHTS).

        Returns:
            List of recommendation dicts, each containing event, relevance_score,
            distance_km, explanation, and score_breakdown.
        """
        from app.utils.distance import haversine_distance

        # Optionally load user preference profile
        profile = None
        if user_id and self.db:
            try:
                profile = UserPreferenceProfile(self.db, user_id)
            except Exception as e:
                print(f"[Recommender] Could not load user profile: {e}")

        recommendations = []

        for event in self.events:
            distance = haversine_distance(
                user_preferences["latitude"],
                user_preferences["longitude"],
                event["latitude"],
                event["longitude"],
            )

            # Hard distance cap
            if max_distance_km is not None and distance > max_distance_km:
                continue

            relevance_score, score_breakdown = self.scoring_engine.calculate_relevance_score(
                event, user_preferences, weights=weights
            )

            # --- Personalisation adjustments ---
            if profile:
                # Genre bias
                genre_bias = profile.genre_bias.get(event["genre"], 0)
                relevance_score += genre_bias * 0.05

                # Crowd bias — only when crowd data is present
                if "crowd" in score_breakdown:
                    relevance_score += profile.crowd_bias

            if relevance_score > 0.0:
                explanation = self._generate_explanation(score_breakdown, relevance_score)
                recommendations.append({
                    "event": {
                        "id": event["id"],
                        "name": event["name"],
                        "date": event["date"],
                        "genre": event.get("genre"),
                        "latitude": event["latitude"],
                        "longitude": event["longitude"],
                    },
                    "relevance_score": round(relevance_score, 3),
                    "distance_km": round(distance, 1),
                    "explanation": explanation,
                    "score_breakdown": score_breakdown,
                })

        # --- Minimum score filter (applied once, after loop) ---
        MIN_SCORE = 0.4
        recommendations = [r for r in recommendations if r["relevance_score"] >= MIN_SCORE]

        if not recommendations:
            return []

        # --- Sorting ---
        recommendations = self._sort(recommendations, sort_by)

        return recommendations[:top_n]

    # ------------------------------------------------------------------
    # Sorting
    # ------------------------------------------------------------------

    @staticmethod
    def _sort(recommendations: List[Dict], sort_by: str) -> List[Dict]:
        """Sort recommendations according to the requested strategy."""

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

        # Default: "best" — tiered by distance band, then by score
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
    # Explanation generation
    # ------------------------------------------------------------------

    def _generate_explanation(self, score_breakdown: dict, total_score: float) -> str:
        """
        Build a human-readable explanation highlighting the top 3 scoring factors.

        Args:
            score_breakdown: Per-factor score data from the scoring engine.
            total_score: Overall weighted relevance score.

        Returns:
            Pipe-separated string of top factor descriptions.
        """
        weights = ScoringEngine.WEIGHTS

        contributions = [
            {
                "factor": factor,
                "contribution": data["value"] * weights.get(factor, 0),
                "description": data["description"],
            }
            for factor, data in score_breakdown.items()
        ]

        contributions.sort(key=lambda x: x["contribution"], reverse=True)
        top_factors = contributions[:3]

        return " | ".join(f["description"] for f in top_factors)

    # ------------------------------------------------------------------
    # Static helpers
    # ------------------------------------------------------------------

    @staticmethod
    def apply_crowd_modifier(score: float, crowd_level: str, avoid_crowds: bool) -> float:
        """Apply a crowd penalty to a score when the user prefers low-crowd events."""
        if not avoid_crowds:
            return score
        if crowd_level == "HIGH":
            return score * 0.6
        if crowd_level == "MEDIUM":
            return score * 0.85
        return score * 1.05
