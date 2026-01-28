from fastapi import FastAPI
from app.api.v1 import interactions

app = FastAPI(title="AI Events Recommender")

app.include_router(interactions.router)
