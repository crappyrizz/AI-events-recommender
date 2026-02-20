from fastapi import FastAPI
from app.core.database import Base, engine
from app.models import event_interaction  # IMPORTANT (forces model import)
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import interactions, crowd, recommendations, saved_events







app = FastAPI(title = "AI Events Recommender")
API_PREFIX = "/api/v1"

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],   # IMPORTANT (allows OPTIONS)
    allow_headers=["*"],
)

# THIS CREATES THE TABLES
Base.metadata.create_all(bind=engine)

app.include_router(interactions.router, prefix=f"{API_PREFIX}/interactions", tags=["Interactions"])
app.include_router(crowd.router, prefix=f"{API_PREFIX}/crowd", tags=["Crowd"])
app.include_router(recommendations.router, prefix=f"{API_PREFIX}/recommendations", tags=["Recommendations"])
app.include_router(saved_events.router, prefix=f"{API_PREFIX}/saved-events", tags=["Saved Events"])

