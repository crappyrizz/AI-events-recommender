"""
Content-based event recommendation engine.
Loads events from CSV and ranks them using weighted relevance scoring.
"""

import csv
import os
from typing import List, Dict, Tuple
from app.services.scoring import ScoringEngine


class EventRecommender:
    """Recommends events based on user preferences using content-based scoring."""
    
    def __init__(self, events_csv_path: str):
        """
        Initialize the recommender with event data.
        
        Args:
            events_csv_path: Path to the events CSV file
        """
        self.events_csv_path = events_csv_path
        self.scoring_engine = ScoringEngine()
        self.events = []
        self._load_events()
    
    def _load_events(self) -> None:
        """Load events from CSV file."""
        if not os.path.exists(self.events_csv_path):
            raise FileNotFoundError(f"Events CSV file not found: {self.events_csv_path}")
        
        self.events = []
        with open(self.events_csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Convert numeric fields
                event = {
                    'id': row['id'],
                    'name': row['name'],
                    'genre': row['genre'],
                    'ticket_price': float(row['ticket_price']),
                    'latitude': float(row['latitude']),
                    'longitude': float(row['longitude']),
                    'food_type': row['food_type'],
                    'date': row['date'],
                    'description': row.get('description', '')
                }
                self.events.append(event)
    
    def recommend(
        self,
        user_preferences: dict,
        top_n: int = 10
    ) -> List[Dict]:
        """
        Recommend events based on user preferences.
        
        Args:
            user_preferences: User preferences including:
                - budget: float (max ticket price)
                - preferred_genres: list of str
                - latitude: float
                - longitude: float
                - food_preference: str
            top_n: Number of top recommendations to return (default: 10)
        
        Returns:
            List of recommended events with:
                - event data
                - relevance_score
                - explanation (top 2-3 contributing factors)
        """
        recommendations = []
        
        for event in self.events:
            relevance_score, score_breakdown = self.scoring_engine.calculate_relevance_score(
                event,
                user_preferences
            )
            
            # Only include events with positive relevance score
            if relevance_score > 0.0:
                explanation = self._generate_explanation(score_breakdown, relevance_score)
                
                recommendation = {
                    'event': event,
                    'relevance_score': round(relevance_score, 3),
                    'explanation': explanation,
                    'score_breakdown': score_breakdown
                }
                recommendations.append(recommendation)
        
        # Sort by relevance score (descending)
        recommendations.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return recommendations[:top_n]
    
    def _generate_explanation(self, score_breakdown: dict, total_score: float) -> str:
        """
        Generate a human-readable explanation for why an event was recommended.
        Mentions only the top 2-3 contributing factors.
        
        Args:
            score_breakdown: Dict with individual component scores
            total_score: Overall relevance score
        
        Returns:
            Human-readable explanation string
        """
        # Calculate weighted contributions
        contributions = []
        weights = ScoringEngine.WEIGHTS
        
        for factor, data in score_breakdown.items():
            weighted_contribution = data['value'] * weights[factor]
            contributions.append({
                'factor': factor,
                'contribution': weighted_contribution,
                'description': data['description']
            })
        
        # Sort by contribution value and get top 2-3
        contributions.sort(key=lambda x: x['contribution'], reverse=True)
        top_factors = contributions[:3]
        
        # Build explanation
        explanation_parts = []
        for factor_data in top_factors:
            explanation_parts.append(factor_data['description'])
        
        explanation = " | ".join(explanation_parts)
        return explanation
