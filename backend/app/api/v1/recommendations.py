from fastapi import APIRouter
from app.services.recommender import EventRecommender
from app.schemas.recommendation import RecommendationRequest

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])

@router.post("/")
def get_recommendations(payload: RecommendationRequest):
    """
    Return ranked events based on user preferences and contextual scoring.
    """
    recommender = EventRecommender(
        events_csv_path="app/data/events_seed.csv"
    )
    results = recommender.recommend(payload.preferences.dict())

    return results
