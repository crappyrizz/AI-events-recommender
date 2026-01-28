"""
Test the recommendation engine using sample user and preferences.
Prints ranked events and their scores for manual verification.
"""

import sys
import os
from pathlib import Path

# Add backend to path for imports
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from app.services.recommender import EventRecommender


def test_recommendation_engine():
    """Test the recommendation engine with sample data."""
    
    # Path to events CSV
    events_csv = Path(__file__).parent.parent / 'app' / 'data' / 'events_seed.csv'
    
    # Initialize recommender
    recommender = EventRecommender(str(events_csv))
    
    # Sample user preferences
    test_cases = [
        {
            'name': 'Alice - Music and Tech Lover (NYC)',
            'preferences': {
                'budget': 100.00,
                'preferred_genres': ['Music', 'Technology'],
                'latitude': 40.7128,
                'longitude': -74.0060,
                'food_preference': 'Vegan'
            }
        },
        {
            'name': 'Bob - Food and Sports Enthusiast (NYC)',
            'preferences': {
                'budget': 50.00,
                'preferred_genres': ['Food', 'Sports'],
                'latitude': 40.7580,
                'longitude': -73.9855,
                'food_preference': 'BBQ'
            }
        },
        {
            'name': 'Carol - Budget-Conscious Movie Lover (LA)',
            'preferences': {
                'budget': 30.00,
                'preferred_genres': ['Movies'],
                'latitude': 34.0522,
                'longitude': -118.2437,
                'food_preference': 'Italian'
            }
        },
    ]
    
    # Test each case
    for test_case in test_cases:
        print("\n" + "=" * 80)
        print(f"TEST CASE: {test_case['name']}")
        print("=" * 80)
        
        preferences = test_case['preferences']
        print(f"\nUser Preferences:")
        print(f"  Budget: ${preferences['budget']:.2f}")
        print(f"  Preferred Genres: {', '.join(preferences['preferred_genres'])}")
        print(f"  Location: ({preferences['latitude']}, {preferences['longitude']})")
        print(f"  Food Preference: {preferences['food_preference']}")
        
        # Get recommendations
        recommendations = recommender.recommend(preferences, top_n=5)
        
        print(f"\n\nTop {len(recommendations)} Recommendations:")
        print("-" * 80)
        
        if not recommendations:
            print("No recommendations found matching user preferences.")
        else:
            for rank, rec in enumerate(recommendations, 1):
                event = rec['event']
                score = rec['relevance_score']
                explanation = rec['explanation']
                
                print(f"\n{rank}. {event['name']}")
                print(f"   Relevance Score: {score:.3f}")
                print(f"   Event Details: {event['genre']} | ${event['ticket_price']:.2f} | {event['food_type']}")
                print(f"   Date: {event['date']}")
                print(f"   Why Recommended: {explanation}")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)


if __name__ == '__main__':
    test_recommendation_engine()
