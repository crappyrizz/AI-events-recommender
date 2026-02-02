class WeatherContextService:
    """
    Provides weather-based contextual relevance.
    This is a mocked service (no external API yet).
    """

    @staticmethod
    def score(event_type: str) -> float:
        """
        Return a weather suitability score.
        Outdoor events are penalized by default.
        """
        outdoor_types = ["outdoor", "festival", "open-air"]

        if event_type.lower() in outdoor_types:
            return 0.6  # weather risk
        return 1.0  # indoor events unaffected
