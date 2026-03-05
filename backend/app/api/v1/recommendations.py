"""
Recommendations endpoint.
Accepts structured user preferences and returns ranked events from PostgreSQL.
"""

from fastapi import Query, Depends, APIRouter
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.recommender import EventRecommender
from app.schemas.recommendation import RecommendationRequest

router = APIRouter()


@router.post("/")
def get_recommendations(
    payload: RecommendationRequest,
    sort_by: str = Query(default="best"),
    max_distance_km: float | None = Query(None),
    db: Session = Depends(get_db),
):
    """
    Return ranked events based on user preferences and contextual scoring.

    Args:
        payload: RecommendationRequest containing user_id and preferences
        sort_by: "best" | "distance" | "budget" | "crowd" | "weather"
        max_distance_km: Optional hard distance cap in km
        db: SQLAlchemy session (injected by FastAPI)

    Returns:
        List of ranked recommendation dicts
    """
    # EventRecommender now only takes db — no CSV path
    recommender = EventRecommender(db=db)

    # recommender.recommend() handles all sorting internally
    # so we just pass sort_by through and return the result directly
    results = recommender.recommend(
        user_preferences=payload.preferences.dict(),
        user_id=payload.user_id,
        sort_by=sort_by,
        max_distance_km=max_distance_km,
        top_n=10,
    )

    if not results:
        return {
            "results": [],
            "message": "No events found matching your criteria. Try broadening your search."
        }

    return {"results": results}