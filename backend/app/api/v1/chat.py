"""
Chat endpoint for natural language event search.
Interprets user queries via LLM and returns ranked event recommendations.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from app.services.llm_interpreter import interpret_with_llm
from app.services.recommender import EventRecommender

router = APIRouter()


class ChatRequest(BaseModel):
    message: str


recommender = EventRecommender("app/data/events_seed.csv")

DEFAULT_WEIGHTS = {
    "budget": 0.25,
    "genre": 0.30,
    "distance": 0.20,
    "food_preference": 0.15,
    "temporal": 0.10,
    "weather": 0.08,
    "crowd": 0.06,
}

# How much to boost the priority factor
# PRIORITY_BOOST = 0.50


def generate_weights(priority: str | None) -> dict:
    """
    Boosts the priority factor to 0.5 and distributes the remaining
    0.5 equally across all other keys.

    Original dynamic weight logic:
    - priority key  → 0.5
    - all other keys → 0.5 / (n - 1) each
    - total always sums to 1.0
    """
    if not priority or priority not in DEFAULT_WEIGHTS:
        return DEFAULT_WEIGHTS.copy()

    weights = DEFAULT_WEIGHTS.copy()
    weights[priority] = 0.5

    remaining = 0.5 / (len(weights) - 1)
    for key in weights:
        if key != priority:
            weights[key] = remaining

    return weights


@router.post("/")
def chat_query(data: ChatRequest):
    """
    Main chat endpoint. Accepts a natural language message,
    extracts preferences via LLM, and returns event recommendations.
    """
    print(f"[Chat] Received message: {data.message}")

    # --- Parse user message ---
    parsed = interpret_with_llm(data.message)
    print(f"[Chat] Parsed preferences: {parsed}")

    # --- Clarification needed ---
    if parsed.get("needs_clarification", False):
        return {
            "needs_clarification": True,
            "question": parsed.get(
                "follow_up_question",
                "Could you clarify what you're looking for? (e.g., budget, type of event, location preference)"
            )
        }

    # --- Build weights ---
    priority = parsed.get("weight_emphasis")
    weights = generate_weights(priority)

    # --- Build preferences ---
    preferences = {
        "budget": parsed.get("budget") or 1000.0,
        "preferred_genres": parsed.get("preferred_genres") or [],
        "latitude": -1.286389,   # Default: Nairobi
        "longitude": 36.817223,
        "food_preference": parsed.get("food_preference") or "any",
        "avoid_crowds": parsed.get("avoid_crowds", False)
    }
    
    

    # --- Distance filter ---
    distance_pref = parsed.get("distance_preference")
    max_distance_km = None
    if distance_pref == "near":
        max_distance_km = 10
    elif distance_pref == "far":
        max_distance_km = 200

    # --- Get recommendations ---
    recommendations = recommender.recommend(
        user_preferences=preferences,
        weights=weights,
        max_distance_km=max_distance_km,
        top_n=10
    )
    
    # After getting recommendations, if user specified genres, 
    # prioritize genre matches at the top
    if preferences["preferred_genres"]:
        genre_matches = [r for r in recommendations if r["event"]["genre"].lower() 
                    in [g.lower() for g in preferences["preferred_genres"]]]
        non_matches = [r for r in recommendations if r not in genre_matches]
        recommendations = genre_matches + non_matches

    # --- Build response ---
    response = {
        "needs_clarification": False,
        "interpretation": {
            "budget": preferences["budget"],
            "genres": preferences["preferred_genres"],
            "food_preference": preferences["food_preference"],
            "distance_preference": distance_pref,
            "priority": priority,
            "confidence": parsed.get("confidence", 0.5)
        },
        "results": recommendations
    }

    if not recommendations:
        response["message"] = "No events found matching your criteria. Try broadening your search."

    return response
