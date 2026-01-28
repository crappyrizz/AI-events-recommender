"""
Calculate relevance scores for events based on user preferences.
Uses weighted scoring with budget and genre as primary factors.
"""

from app.utils.distance import haversine_distance


class ScoringEngine:
    """Simple weighted scoring for event relevance."""
    
    # Weight configuration (sum should be 1.0)
    WEIGHTS = {
        'budget': 0.35,        # Budget match is most important
        'genre': 0.30,         # Genre preference is second most important
        'distance': 0.20,      # Distance is less critical
        'food_preference': 0.15  # Food preference is least critical
    }
    
    def calculate_relevance_score(
        self,
        event: dict,
        user_preferences: dict
    ) -> tuple[float, dict]:
        """
        Calculate a weighted relevance score for an event based on user preferences.
        
        Args:
            event: Event data (must include: ticket_price, genre, latitude, longitude, food_type)
            user_preferences: User preferences (must include: budget, preferred_genres, latitude, 
                            longitude, food_preference)
        
        Returns:
            tuple: (relevance_score, score_breakdown)
                - relevance_score: float between 0.0 and 1.0
                - score_breakdown: dict with individual component scores and explanations
        """
        score_breakdown = {}
        
        # Budget score (higher is better, penalize if exceeds budget)
        budget_score = self._score_budget(
            event['ticket_price'],
            user_preferences['budget']
        )
        score_breakdown['budget'] = {
            'value': budget_score,
            'description': f"Budget match: Event ticket ${event['ticket_price']:.2f} vs budget ${user_preferences['budget']:.2f}"
        }
        
        # Genre score
        genre_score = self._score_genre(
            event['genre'],
            user_preferences['preferred_genres']
        )
        score_breakdown['genre'] = {
            'value': genre_score,
            'description': f"Genre match: Event genre '{event['genre']}' vs preferences {user_preferences['preferred_genres']}"
        }
        
        # Distance score
        distance = haversine_distance(
            user_preferences['latitude'],
            user_preferences['longitude'],
            event['latitude'],
            event['longitude']
        )
        distance_score = self._score_distance(distance)
        score_breakdown['distance'] = {
            'value': distance_score,
            'description': f"Location proximity: {distance:.1f} km away"
        }
        
        # Food preference score
        food_score = self._score_food_preference(
            event['food_type'],
            user_preferences['food_preference']
        )
        score_breakdown['food_preference'] = {
            'value': food_score,
            'description': f"Food preference match: Event food '{event['food_type']}' vs preference '{user_preferences['food_preference']}'"
        }
        
        # Calculate weighted relevance score
        relevance_score = (
            budget_score * self.WEIGHTS['budget'] +
            genre_score * self.WEIGHTS['genre'] +
            distance_score * self.WEIGHTS['distance'] +
            food_score * self.WEIGHTS['food_preference']
        )
        
        return relevance_score, score_breakdown
    
    @staticmethod
    def _score_budget(ticket_price: float, user_budget: float) -> float:
        """
        Score based on budget match.
        - Perfect score (1.0) if price is within budget
        - Penalize if price exceeds budget
        """
        if ticket_price <= user_budget:
            # Within budget: normalize to 0.6-1.0 range (cheaper is better, but not hugely)
            if user_budget == 0:
                return 0.0
            return 0.6 + (1 - ticket_price / user_budget) * 0.4
        else:
            # Exceeds budget: penalize proportionally
            excess = ticket_price - user_budget
            penalty = min(excess / user_budget, 1.0)  # Cap penalty at 1.0
            return max(0.0, 0.3 - penalty * 0.3)  # Range 0.0 to 0.3
    
    @staticmethod
    def _score_genre(event_genre: str, preferred_genres: list) -> float:
        """
        Score based on genre match.
        Perfect match = 1.0, no match = 0.0
        """
        if event_genre.lower() in [g.lower() for g in preferred_genres]:
            return 1.0
        return 0.0
    
    @staticmethod
    def _score_distance(distance_km: float) -> float:
        """
        Score based on distance.
        - Close (0-5 km): high score
        - Medium (5-20 km): medium score
        - Far (20+ km): low score
        """
        if distance_km <= 5:
            return 1.0
        elif distance_km <= 20:
            return max(0.4, 1.0 - (distance_km - 5) / 15 * 0.6)
        else:
            return max(0.0, 0.4 - (distance_km - 20) / 100 * 0.4)
    
    @staticmethod
    def _score_food_preference(event_food: str, user_food_preference: str) -> float:
        """
        Score based on food preference match.
        Perfect match = 1.0, no match = 0.2 (events can be good without matching food)
        """
        if event_food.lower() == user_food_preference.lower():
            return 1.0
        return 0.2
