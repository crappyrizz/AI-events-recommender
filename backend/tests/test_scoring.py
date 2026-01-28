"""
Unit tests for the scoring engine with edge cases.
Tests budget edge cases, genre mismatches, distance extremes, and food preferences.
"""

import sys
from pathlib import Path

# Add backend to path for imports
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from app.services.scoring import ScoringEngine
from app.utils.distance import haversine_distance


class TestScoringEngine:
    """Test cases for the ScoringEngine."""
    
    def __init__(self):
        self.engine = ScoringEngine()
    
    # ==================== BUDGET EDGE CASES ====================
    
    def test_budget_zero(self):
        """Test scoring when user has zero budget."""
        print("\n" + "="*80)
        print("TEST: Budget = 0")
        print("="*80)
        
        event = {
            'id': 'E001',
            'name': 'Concert',
            'genre': 'Music',
            'ticket_price': 50.0,
            'latitude': 40.7128,
            'longitude': -74.0060,
            'food_type': 'Pizza',
            'date': '2024-03-15',
            'description': 'Test event'
        }
        
        user_prefs = {
            'budget': 0.0,
            'preferred_genres': ['Music'],
            'latitude': 40.7128,
            'longitude': -74.0060,
            'food_preference': 'Pizza'
        }
        
        score, breakdown = self.engine.calculate_relevance_score(event, user_prefs)
        
        print(f"Event: {event['name']}")
        print(f"User Budget: ${user_prefs['budget']:.2f}")
        print(f"Event Price: ${event['ticket_price']:.2f}")
        print(f"Overall Score: {score:.3f}")
        print(f"Budget Component: {breakdown['budget']['value']:.3f}")
        print(f"Expected: Budget score should be 0.0 when budget is 0")
        
        assert breakdown['budget']['value'] == 0.0, "Budget score should be 0 when user budget is 0"
        print("✓ PASSED\n")
    
    def test_budget_within_budget(self):
        """Test scoring when event price is within budget."""
        print("="*80)
        print("TEST: Event Price Within Budget")
        print("="*80)
        
        event = {
            'id': 'E002',
            'name': 'Concert',
            'genre': 'Music',
            'ticket_price': 40.0,
            'latitude': 40.7128,
            'longitude': -74.0060,
            'food_type': 'Pizza',
            'date': '2024-03-15',
            'description': 'Test event'
        }
        
        user_prefs = {
            'budget': 100.0,
            'preferred_genres': ['Music'],
            'latitude': 40.7128,
            'longitude': -74.0060,
            'food_preference': 'Pizza'
        }
        
        score, breakdown = self.engine.calculate_relevance_score(event, user_prefs)
        
        print(f"Event: {event['name']}")
        print(f"User Budget: ${user_prefs['budget']:.2f}")
        print(f"Event Price: ${event['ticket_price']:.2f}")
        print(f"Overall Score: {score:.3f}")
        print(f"Budget Component: {breakdown['budget']['value']:.3f}")
        print(f"Expected: Budget score should be 0.6-1.0 range (event within budget)")
        
        budget_score = breakdown['budget']['value']
        assert 0.6 <= budget_score <= 1.0, "Budget score should be in 0.6-1.0 range"
        print("✓ PASSED\n")
    
    def test_budget_exceeds_budget(self):
        """Test scoring when event price exceeds budget (penalty case)."""
        print("="*80)
        print("TEST: Event Price Exceeds Budget (Penalty)")
        print("="*80)
        
        event = {
            'id': 'E003',
            'name': 'Concert',
            'genre': 'Music',
            'ticket_price': 150.0,
            'latitude': 40.7128,
            'longitude': -74.0060,
            'food_type': 'Pizza',
            'date': '2024-03-15',
            'description': 'Test event'
        }
        
        user_prefs = {
            'budget': 100.0,
            'preferred_genres': ['Music'],
            'latitude': 40.7128,
            'longitude': -74.0060,
            'food_preference': 'Pizza'
        }
        
        score, breakdown = self.engine.calculate_relevance_score(event, user_prefs)
        
        print(f"Event: {event['name']}")
        print(f"User Budget: ${user_prefs['budget']:.2f}")
        print(f"Event Price: ${event['ticket_price']:.2f}")
        print(f"Overall Score: {score:.3f}")
        print(f"Budget Component: {breakdown['budget']['value']:.3f}")
        print(f"Expected: Budget score should be 0.0-0.3 range (penalty for exceeding budget)")
        
        budget_score = breakdown['budget']['value']
        assert 0.0 <= budget_score <= 0.3, "Budget score should be penalized to 0.0-0.3 range"
        print("✓ PASSED\n")
    
    # ==================== GENRE EDGE CASES ====================
    
    def test_no_preferred_genres(self):
        """Test scoring when user has no preferred genres."""
        print("="*80)
        print("TEST: No Preferred Genres")
        print("="*80)
        
        event = {
            'id': 'E004',
            'name': 'Concert',
            'genre': 'Music',
            'ticket_price': 50.0,
            'latitude': 40.7128,
            'longitude': -74.0060,
            'food_type': 'Pizza',
            'date': '2024-03-15',
            'description': 'Test event'
        }
        
        user_prefs = {
            'budget': 100.0,
            'preferred_genres': [],  # Empty list - no preferences
            'latitude': 40.7128,
            'longitude': -74.0060,
            'food_preference': 'Pizza'
        }
        
        score, breakdown = self.engine.calculate_relevance_score(event, user_prefs)
        
        print(f"Event: {event['name']}")
        print(f"User Preferred Genres: {user_prefs['preferred_genres']}")
        print(f"Event Genre: {event['genre']}")
        print(f"Overall Score: {score:.3f}")
        print(f"Genre Component: {breakdown['genre']['value']:.3f}")
        print(f"Expected: Genre score should be 0.0 when no preferred genres specified")
        
        assert breakdown['genre']['value'] == 0.0, "Genre score should be 0 with empty preferences"
        print("✓ PASSED\n")
    
    def test_genre_mismatch(self):
        """Test scoring when event genre doesn't match preferences."""
        print("="*80)
        print("TEST: Genre Mismatch")
        print("="*80)
        
        event = {
            'id': 'E005',
            'name': 'Concert',
            'genre': 'Rock',
            'ticket_price': 50.0,
            'latitude': 40.7128,
            'longitude': -74.0060,
            'food_type': 'Pizza',
            'date': '2024-03-15',
            'description': 'Test event'
        }
        
        user_prefs = {
            'budget': 100.0,
            'preferred_genres': ['Jazz', 'Classical'],  # Rock not in list
            'latitude': 40.7128,
            'longitude': -74.0060,
            'food_preference': 'Pizza'
        }
        
        score, breakdown = self.engine.calculate_relevance_score(event, user_prefs)
        
        print(f"Event: {event['name']}")
        print(f"User Preferred Genres: {user_prefs['preferred_genres']}")
        print(f"Event Genre: {event['genre']}")
        print(f"Overall Score: {score:.3f}")
        print(f"Genre Component: {breakdown['genre']['value']:.3f}")
        print(f"Expected: Genre score should be 0.0 for non-matching genre")
        
        assert breakdown['genre']['value'] == 0.0, "Genre score should be 0 for non-match"
        print("✓ PASSED\n")
    
    def test_genre_match(self):
        """Test scoring when event genre matches preferences."""
        print("="*80)
        print("TEST: Genre Match")
        print("="*80)
        
        event = {
            'id': 'E006',
            'name': 'Concert',
            'genre': 'Jazz',
            'ticket_price': 50.0,
            'latitude': 40.7128,
            'longitude': -74.0060,
            'food_type': 'Pizza',
            'date': '2024-03-15',
            'description': 'Test event'
        }
        
        user_prefs = {
            'budget': 100.0,
            'preferred_genres': ['Jazz', 'Classical'],
            'latitude': 40.7128,
            'longitude': -74.0060,
            'food_preference': 'Pizza'
        }
        
        score, breakdown = self.engine.calculate_relevance_score(event, user_prefs)
        
        print(f"Event: {event['name']}")
        print(f"User Preferred Genres: {user_prefs['preferred_genres']}")
        print(f"Event Genre: {event['genre']}")
        print(f"Overall Score: {score:.3f}")
        print(f"Genre Component: {breakdown['genre']['value']:.3f}")
        print(f"Expected: Genre score should be 1.0 for matching genre")
        
        assert breakdown['genre']['value'] == 1.0, "Genre score should be 1.0 for match"
        print("✓ PASSED\n")
    
    # ==================== DISTANCE EDGE CASES ====================
    
    def test_very_close_distance(self):
        """Test scoring when event is very close (same location)."""
        print("="*80)
        print("TEST: Very Close Distance (Same Location)")
        print("="*80)
        
        event = {
            'id': 'E007',
            'name': 'Concert',
            'genre': 'Music',
            'ticket_price': 50.0,
            'latitude': 40.7128,
            'longitude': -74.0060,
            'food_type': 'Pizza',
            'date': '2024-03-15',
            'description': 'Test event'
        }
        
        user_prefs = {
            'budget': 100.0,
            'preferred_genres': ['Music'],
            'latitude': 40.7128,  # Same location
            'longitude': -74.0060,
            'food_preference': 'Pizza'
        }
        
        score, breakdown = self.engine.calculate_relevance_score(event, user_prefs)
        
        print(f"Event: {event['name']}")
        print(f"User Location: ({user_prefs['latitude']}, {user_prefs['longitude']})")
        print(f"Event Location: ({event['latitude']}, {event['longitude']})")
        print(f"Overall Score: {score:.3f}")
        print(f"Distance Component: {breakdown['distance']['value']:.3f}")
        print(f"Expected: Distance score should be 1.0 for same location")
        
        assert breakdown['distance']['value'] == 1.0, "Distance score should be 1.0 at same location"
        print("✓ PASSED\n")
    
    def test_very_high_distance(self):
        """Test scoring when event is very far away (500+ km)."""
        print("="*80)
        print("TEST: Very High Distance (500+ km)")
        print("="*80)
        
        # NYC to LA is approximately 3,944 km
        event = {
            'id': 'E008',
            'name': 'Concert',
            'genre': 'Music',
            'ticket_price': 50.0,
            'latitude': 34.0522,  # Los Angeles
            'longitude': -118.2437,
            'food_type': 'Pizza',
            'date': '2024-03-15',
            'description': 'Test event'
        }
        
        user_prefs = {
            'budget': 100.0,
            'preferred_genres': ['Music'],
            'latitude': 40.7128,  # New York
            'longitude': -74.0060,
            'food_preference': 'Pizza'
        }
        
        score, breakdown = self.engine.calculate_relevance_score(event, user_prefs)
        distance = haversine_distance(40.7128, -74.0060, 34.0522, -118.2437)
        
        print(f"Event: {event['name']}")
        print(f"User Location: NYC ({user_prefs['latitude']}, {user_prefs['longitude']})")
        print(f"Event Location: LA ({event['latitude']}, {event['longitude']})")
        print(f"Distance: {distance:.1f} km")
        print(f"Overall Score: {score:.3f}")
        print(f"Distance Component: {breakdown['distance']['value']:.3f}")
        print(f"Expected: Distance score should be very low (near 0.0) for very far events")
        
        assert breakdown['distance']['value'] < 0.05, "Distance score should be very low for far events"
        print("✓ PASSED\n")
    
    # ==================== FOOD PREFERENCE EDGE CASES ====================
    
    def test_food_preference_match(self):
        """Test scoring when food preference matches."""
        print("="*80)
        print("TEST: Food Preference Match")
        print("="*80)
        
        event = {
            'id': 'E009',
            'name': 'Concert',
            'genre': 'Music',
            'ticket_price': 50.0,
            'latitude': 40.7128,
            'longitude': -74.0060,
            'food_type': 'Vegan',
            'date': '2024-03-15',
            'description': 'Test event'
        }
        
        user_prefs = {
            'budget': 100.0,
            'preferred_genres': ['Music'],
            'latitude': 40.7128,
            'longitude': -74.0060,
            'food_preference': 'Vegan'
        }
        
        score, breakdown = self.engine.calculate_relevance_score(event, user_prefs)
        
        print(f"Event: {event['name']}")
        print(f"Event Food: {event['food_type']}")
        print(f"User Food Preference: {user_prefs['food_preference']}")
        print(f"Overall Score: {score:.3f}")
        print(f"Food Component: {breakdown['food_preference']['value']:.3f}")
        print(f"Expected: Food score should be 1.0 for matching preference")
        
        assert breakdown['food_preference']['value'] == 1.0, "Food score should be 1.0 for match"
        print("✓ PASSED\n")
    
    def test_food_preference_mismatch(self):
        """Test scoring when food preference doesn't match (but event still has some value)."""
        print("="*80)
        print("TEST: Food Preference Mismatch")
        print("="*80)
        
        event = {
            'id': 'E010',
            'name': 'Concert',
            'genre': 'Music',
            'ticket_price': 50.0,
            'latitude': 40.7128,
            'longitude': -74.0060,
            'food_type': 'BBQ',
            'date': '2024-03-15',
            'description': 'Test event'
        }
        
        user_prefs = {
            'budget': 100.0,
            'preferred_genres': ['Music'],
            'latitude': 40.7128,
            'longitude': -74.0060,
            'food_preference': 'Vegan'
        }
        
        score, breakdown = self.engine.calculate_relevance_score(event, user_prefs)
        
        print(f"Event: {event['name']}")
        print(f"Event Food: {event['food_type']}")
        print(f"User Food Preference: {user_prefs['food_preference']}")
        print(f"Overall Score: {score:.3f}")
        print(f"Food Component: {breakdown['food_preference']['value']:.3f}")
        print(f"Expected: Food score should be 0.2 for non-match (event still valuable)")
        
        assert breakdown['food_preference']['value'] == 0.2, "Food score should be 0.2 for mismatch"
        # Event should still have positive overall score due to other factors
        assert score > 0.0, "Event should have positive score despite food mismatch"
        print("✓ PASSED\n")
    
    # ==================== HAVERSINE DISTANCE TESTS ====================
    
    def test_haversine_same_location(self):
        """Test Haversine distance for same location."""
        print("="*80)
        print("TEST: Haversine - Same Location")
        print("="*80)
        
        distance = haversine_distance(40.7128, -74.0060, 40.7128, -74.0060)
        
        print(f"Location 1: (40.7128, -74.0060)")
        print(f"Location 2: (40.7128, -74.0060)")
        print(f"Distance: {distance:.2f} km")
        print(f"Expected: Distance should be 0.0 km")
        
        assert distance < 0.1, "Distance should be near 0 for same location"
        print("✓ PASSED\n")
    
    def test_haversine_known_distance(self):
        """Test Haversine distance against known NYC-LA distance."""
        print("="*80)
        print("TEST: Haversine - NYC to LA (Known Distance)")
        print("="*80)
        
        # NYC: 40.7128, -74.0060
        # LA: 34.0522, -118.2437
        # Expected: ~3944 km
        
        distance = haversine_distance(40.7128, -74.0060, 34.0522, -118.2437)
        
        print(f"Location 1 (NYC): (40.7128, -74.0060)")
        print(f"Location 2 (LA): (34.0522, -118.2437)")
        print(f"Distance: {distance:.2f} km")
        print(f"Expected: Approximately 3944 km")
        
        # Allow some tolerance (±10%)
        assert 3500 < distance < 4300, "Distance should be approximately 3944 km"
        print(f"✓ PASSED (Distance is {distance:.2f} km)\n")


def run_all_tests():
    """Run all test cases."""
    print("\n" + "="*80)
    print("EDGE CASE UNIT TESTS FOR SCORING ENGINE")
    print("="*80)
    
    test_suite = TestScoringEngine()
    
    try:
        # Budget tests
        test_suite.test_budget_zero()
        test_suite.test_budget_within_budget()
        test_suite.test_budget_exceeds_budget()
        
        # Genre tests
        test_suite.test_no_preferred_genres()
        test_suite.test_genre_mismatch()
        test_suite.test_genre_match()
        
        # Distance tests
        test_suite.test_very_close_distance()
        test_suite.test_very_high_distance()
        
        # Food preference tests
        test_suite.test_food_preference_match()
        test_suite.test_food_preference_mismatch()
        
        # Haversine tests
        test_suite.test_haversine_same_location()
        test_suite.test_haversine_known_distance()
        
        print("="*80)
        print("ALL TESTS PASSED ✓")
        print("="*80)
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        print("="*80)
        return False
    
    return True


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
