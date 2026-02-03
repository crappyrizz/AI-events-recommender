from fastapi import FastAPI

from app.core.database import Base, engine
from app.models import event_interaction  # IMPORTANT (forces model import)
from fastapi.middleware.cors import CORSMiddleware


from app.api.v1 import interactions, crowd, recommendations

app = FastAPI(title = "AI Events Recommender")

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

app.include_router(interactions.router)
app.include_router(crowd.router)
app.include_router(recommendations.router)
