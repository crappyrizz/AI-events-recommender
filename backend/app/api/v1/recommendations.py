from fastapi import APIRouter
from app.services.recommender import EventRecommender
from app.schemas.recommendation import RecommendationRequest
from fastapi import Query


router = APIRouter(prefix="/recommendations", tags=["Recommendations"])

@router.post("/")
def get_recommendations(payload: RecommendationRequest, sort_by: str = Query("best")):
    """
    Return ranked events based on user preferences and contextual scoring.
    """
    recommender = EventRecommender(
        events_csv_path="app/data/events_seed.csv"
    )
    results = recommender.recommend(payload.preferences.dict())

    if sort_by == "best":
        # Already sorted by relevance_score from recommender
        results.sort(key=lambda r: r["relevance_score"], reverse=True)

    elif sort_by == "distance":
        # Lower distance is better
        results.sort(key=lambda r: r["distance_km"])

    elif sort_by == "budget":
        # Higher budget match is better
        results.sort(
            key=lambda r: r["score_breakdown"]["budget"]["value"],
            reverse=True
        )

    elif sort_by == "crowd":
        # Lower crowd is better (avoid_crowds preference)
        results.sort(
            key=lambda r: r["score_breakdown"]["crowd"]["value"]
        )

    elif sort_by == "weather":
        # Higher weather match is better
        results.sort(
            key=lambda r: r["score_breakdown"]["weather"]["value"],
            reverse=True
        )

    return results
