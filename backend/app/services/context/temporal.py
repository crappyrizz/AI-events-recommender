from datetime import datetime


class TemporalContextService:
    """
    Scores events based on temporal relevance using event date only.
    """

    @staticmethod
    def score(event_date: str) -> float:
        try:
            event_dt = datetime.strptime(event_date, "%Y-%m-%d").date()
        except ValueError:
            return 0.5  # Unknown format, neutral score

        today = datetime.utcnow().date()
        delta_days = (event_dt - today).days

        if delta_days < 0:
            return 0.0
        elif delta_days == 0:
            return 1.0
        elif delta_days <= 3:
            return 0.9
        elif delta_days <= 7:
            return 0.8
        else:
            return 0.6
