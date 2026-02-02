class CrowdContextService:
    """
    Translates crowd interest levels into a relevance score.
    Lower crowd = higher score (generally preferred).
    """

    @staticmethod
    def score(level: str) -> float:
        """
        Convert crowd level to a normalized score.
        """
        mapping = {
            "LOW": 1.0,
            "MEDIUM": 0.7,
            "HIGH": 0.4
        }

        return mapping.get(level.upper(), 0.7)
