from datetime import datetime


class TemporalContextService:
    """
    Scores events based on how soon they are from today.
    Uses a decay curve that favours events happening within 30 days.
    """

    @staticmethod
    def score(event_date: str) -> float:
        """
        Score an event based on days until it occurs.

        Scoring curve:
            past        → 0.0
            today       → 1.0
            1–7 days    → 0.5–1.0  (ramps up as event approaches)
            8–30 days   → 0.9      (high relevance, coming soon)
            31–60 days  → 0.3–0.9  (gradual decay)
            60+ days    → 0.1      (low relevance, too far away)

        Args:
            event_date: Date string in YYYY-MM-DD format.

        Returns:
            Float score between 0.0 and 1.0.
        """
        try:
            event_dt = datetime.strptime(event_date, "%Y-%m-%d")
        except (ValueError, TypeError):
            return 0.5  # unknown format → neutral score

        days_until = (event_dt.date() - datetime.utcnow().date()).days

        if days_until < 0:
            return 0.0
        if days_until == 0:
            return 1.0
        if days_until <= 7:
            return min(1.0, 0.5 + days_until / 14)
        if days_until <= 30:
            return 0.9
        if days_until <= 60:
            return max(0.3, 0.9 - (days_until - 30) / 100)
        return 0.1
