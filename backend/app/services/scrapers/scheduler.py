"""
Scraper scheduler and database upsert service.

- Runs the Allevents scraper on a weekly schedule.
- Upserts scraped events into the database (insert or update by source_url).
- Can be triggered manually via an admin endpoint.

How to start (add to main.py startup):
    from app.core.database import SessionLocal
    from app.services.scrapers.scheduler import start_scheduler

    @app.on_event("startup")
    def startup():
        start_scheduler(SessionLocal)
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Callable

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session

from app.models.event import Event
from app.services.scrapers.allevents_scraper import AlleventsScraper
from app.services.genre_classifier import GenreClassifier

logger = logging.getLogger(__name__)

SCRAPE_INTERVAL_DAYS = 7  # re-scrape every 7 days


# ------------------------------------------------------------------
# Upsert logic
# ------------------------------------------------------------------

def upsert_events(db: Session, raw_events: list[dict]) -> dict:
    """
    Insert new events or update existing ones by source_url.

    Why upsert instead of just insert?
        Events get re-scraped weekly. We don't want duplicates.
        source_url is unique per event so we use it as the identifier.
        If the event already exists we update price and date in case
        they changed. If it's new we insert it fresh.

    Args:
        db: SQLAlchemy session
        raw_events: List of raw dicts from scraper

    Returns:
        Summary dict: {inserted, updated, skipped}
    """
    inserted = 0
    updated  = 0
    skipped  = 0

    for raw in raw_events:
        source_url = raw.get("source_url")

        # Skip noise events flagged by genre classifier
        if raw.get("_noise"):
            skipped += 1
            continue

        if not source_url:
            skipped += 1
            continue

        if not raw.get("date"):
            skipped += 1
            continue

        try:
            existing = db.query(Event).filter_by(source_url=source_url).first()

            if existing:
                existing.ticket_price      = raw.get("ticket_price", existing.ticket_price)
                existing.ticket_price_min  = raw.get("ticket_price_min", existing.ticket_price_min)
                existing.ticket_price_max  = raw.get("ticket_price_max", existing.ticket_price_max)
                existing.is_free           = raw.get("is_free", existing.is_free)
                existing.poster_url        = raw.get("poster_url") or existing.poster_url
                existing.venue_name        = raw.get("venue_name") or existing.venue_name
                existing.date              = raw.get("date") or existing.date
                existing.last_refreshed_at = datetime.now(timezone.utc)
                updated += 1

            else:
                event = Event(
                    id               = str(uuid.uuid4()),  # generate unique ID
                    name             = raw.get("name", "Untitled Event"),
                    description      = raw.get("description"),
                    genre            = raw.get("genre"),
                    poster_url       = raw.get("poster_url"),
                    ticket_price     = raw.get("ticket_price", 0.0),
                    ticket_price_min = raw.get("ticket_price_min", 0.0),
                    ticket_price_max = raw.get("ticket_price_max", 0.0),
                    ticket_url       = raw.get("ticket_url"),
                    is_free          = raw.get("is_free", False),
                    currency         = raw.get("currency", "KES"),
                    venue_name       = raw.get("venue_name"),
                    city             = raw.get("city", "Nairobi"),
                    latitude         = raw.get("latitude"),
                    longitude        = raw.get("longitude"),
                    date             = raw.get("date"),
                    food_type        = raw.get("food_type"),
                    crowd_level      = raw.get("crowd_level", "MEDIUM"),
                    event_type       = raw.get("event_type", "indoor"),
                    source           = raw.get("source", "allevents"),
                    source_url       = source_url,
                    scraped_at       = raw.get("scraped_at", datetime.now(timezone.utc)),
                    last_refreshed_at = raw.get("last_refreshed_at", datetime.now(timezone.utc)),
                )
                db.add(event)
                inserted += 1

        except Exception as e:
            logger.error(f"[Upsert] Failed for {source_url}: {e}")
            db.rollback()
            skipped += 1
            continue

    db.commit()
    summary = {"inserted": inserted, "updated": updated, "skipped": skipped}
    logger.info(f"[Upsert] Complete: {summary}")
    return summary


# ------------------------------------------------------------------
# Scheduler
# ------------------------------------------------------------------

_scheduler = BackgroundScheduler()


def _scrape_and_store(db_factory: Callable[[], Session]) -> None:
    """Job: run all scrapers and upsert results into DB."""
    logger.info("[Scheduler] Starting scheduled scrape job...")
    db = db_factory()
    try:
        raw_events = AlleventsScraper().scrape()
        # Classify genres before inserting into DB
        raw_events = GenreClassifier.classify_batch(raw_events)
        summary    = upsert_events(db, raw_events)
        logger.info(f"[Scheduler] Done. Summary: {summary}")
    except Exception as e:
        logger.error(f"[Scheduler] Job failed: {e}")
    finally:
        db.close()


def start_scheduler(db_factory: Callable[[], Session]) -> None:
    """
    Start the background scraper scheduler.
    Call once during FastAPI app startup.
    """
    if _scheduler.running:
        logger.warning("[Scheduler] Already running — skipping.")
        return

    _scheduler.add_job(
        func=_scrape_and_store,
        trigger=IntervalTrigger(days=SCRAPE_INTERVAL_DAYS),
        args=[db_factory],
        id="weekly_scrape",
        name="Weekly Allevents scrape",
        replace_existing=True,
    )

    _scheduler.start()
    logger.info(f"[Scheduler] Started — scraping every {SCRAPE_INTERVAL_DAYS} days.")


def stop_scheduler() -> None:
    """Gracefully stop the scheduler on app shutdown."""
    if _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("[Scheduler] Stopped.")


def trigger_manual_scrape(db_factory: Callable[[], Session]) -> dict:
    """Manually trigger a scrape — used by admin endpoint."""
    logger.info("[Scheduler] Manual scrape triggered.")
    db = db_factory()
    try:
        raw_events = AlleventsScraper().scrape()
        raw_events = GenreClassifier.classify_batch(raw_events)  # classify before upsert
        return upsert_events(db, raw_events)
    finally:
        db.close()