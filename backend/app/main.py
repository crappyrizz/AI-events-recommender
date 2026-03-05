from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import requests as http_requests

from app.core.database import Base, engine, SessionLocal, get_db
from app.models import event_interaction
from app.models.user import User
from app.models.event import Event
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import interactions, crowd, recommendations, saved_events, event_media, chat
from app.api.v1.auth import router as auth_router
from fastapi.staticfiles import StaticFiles
from app.services.scrapers.scheduler import start_scheduler, stop_scheduler, trigger_manual_scrape
from app.services.genre_classifier import GenreClassifier

app = FastAPI(title="AI Events Recommender")
API_PREFIX = "/api/v1"
app.mount("/media", StaticFiles(directory="media"), name="media")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

# ------------------------------------------------------------------
# Startup / shutdown — controls the scraper scheduler
# ------------------------------------------------------------------

@app.on_event("startup")
def startup():
    """Start the weekly scraper scheduler when the API starts."""
    start_scheduler(SessionLocal)


@app.on_event("shutdown")
def shutdown():
    """Stop the scheduler cleanly when the API shuts down."""
    stop_scheduler()


# ------------------------------------------------------------------
# Admin endpoint — manually trigger a scrape without waiting for schedule
# ------------------------------------------------------------------

@app.post("/api/v1/admin/scrape", tags=["Admin"])
def manual_scrape():
    """
    Manually trigger a full scrape of all sources.
    Use this to populate the database on first run or to force a refresh.
    """
    summary = trigger_manual_scrape(SessionLocal)
    return {"status": "complete", "summary": summary}


@app.post("/api/v1/admin/reclassify-genres", tags=["Admin"])
def reclassify_genres(db: Session = Depends(get_db)):
    """
    Retroactively classify genres for all events in the DB that have
    genre=null. Run this once after the first scrape.
    """
    summary = GenreClassifier.reclassify_db(db)
    return {"status": "complete", "summary": summary}


@app.on_event("startup")
def startup():
    start_scheduler(SessionLocal)
    _warmup_llm()

def _warmup_llm():
    """Pre-load the LLM into RAM so the first user request is fast."""
    try:
        print("[LLM] Warming up model...")
        http_requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "qwen2.5:1.5b",
                "prompt": "hi",
                "stream": False,
                "options": {"temperature": 0}
            },
            timeout=120
        )
        print("[LLM] Model warmed up and ready.")
    except Exception as e:
        print(f"[LLM] Warmup failed (Ollama may not be running): {e}")

# ------------------------------------------------------------------
# Routers
# ------------------------------------------------------------------

app.include_router(interactions.router,    prefix=f"{API_PREFIX}/interactions",    tags=["Interactions"])
app.include_router(crowd.router,           prefix=f"{API_PREFIX}/crowd",            tags=["Crowd"])
app.include_router(recommendations.router, prefix=f"{API_PREFIX}/recommendations",  tags=["Recommendations"])
app.include_router(saved_events.router,    prefix=f"{API_PREFIX}/saved-events",     tags=["Saved Events"])
app.include_router(auth_router,            prefix="/api/v1")
app.include_router(event_media.router,     prefix=f"{API_PREFIX}/media",            tags=["Event Media"])
app.include_router(chat.router,            prefix=f"{API_PREFIX}/chat",             tags=["Chat"])
