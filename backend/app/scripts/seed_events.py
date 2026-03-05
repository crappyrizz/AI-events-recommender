"""
Seed script — loads events_seed.csv into the PostgreSQL events table.

Run from your project root:
    python -m app.scripts.seed_events

Safe to run multiple times — uses upsert (insert or update by id).
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Load .env BEFORE importing anything from app
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

import csv
from datetime import datetime, timezone

from app.core.database import SessionLocal
from app.models.event import Event


# ------------------------------------------------------------------
# Map CSV rows to Event model fields
# ------------------------------------------------------------------

def row_to_event(row: dict) -> Event:
    """Convert a CSV row dict into an Event model instance."""

    ticket_price = float(row.get("ticket_price", 0) or 0)

    return Event(
        id               = row["id"],
        name             = row["name"],
        genre            = row["genre"],
        description      = row.get("description"),

        # Ticketing
        ticket_price     = ticket_price,
        ticket_price_min = ticket_price,
        ticket_price_max = ticket_price,
        is_free          = ticket_price == 0.0,
        currency         = "KES",

        # Location
        latitude         = float(row["latitude"]),
        longitude        = float(row["longitude"]),
        city             = "Nairobi",

        # Food & recommender fields
        food_type        = row.get("food_type"),
        crowd_level      = row.get("crowd_level", "MEDIUM"),
        event_type       = row.get("event_type", "indoor"),
        popularity_score = 0.0,

        # Timing
        date             = row.get("date"),

        # Metadata
        source           = "manual",
        is_verified      = True,
        scraped_at       = datetime.now(timezone.utc),
        last_refreshed_at = datetime.now(timezone.utc),
    )


# ------------------------------------------------------------------
# Main seed function
# ------------------------------------------------------------------

def seed_events():
    base_dir = Path(__file__).resolve().parent.parent
    csv_path = base_dir / "data" / "events_seed.csv"

    if not csv_path.exists():
        print(f"[Seed] ERROR: CSV not found at {csv_path}")
        sys.exit(1)

    db = SessionLocal()
    inserted = 0
    updated  = 0
    skipped  = 0

    try:
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                event_id = row.get("id", "").strip()
                if not event_id:
                    skipped += 1
                    continue

                try:
                    existing = db.query(Event).filter_by(id=event_id).first()

                    if existing:
                        existing.name              = row["name"]
                        existing.genre             = row["genre"]
                        existing.description       = row.get("description")
                        existing.ticket_price      = float(row.get("ticket_price", 0) or 0)
                        existing.ticket_price_min  = existing.ticket_price
                        existing.ticket_price_max  = existing.ticket_price
                        existing.is_free           = existing.ticket_price == 0.0
                        existing.latitude          = float(row["latitude"])
                        existing.longitude         = float(row["longitude"])
                        existing.food_type         = row.get("food_type")
                        existing.date              = row.get("date")
                        existing.last_refreshed_at = datetime.now(timezone.utc)
                        updated += 1
                    else:
                        db.add(row_to_event(row))
                        inserted += 1

                except Exception as e:
                    print(f"[Seed] Failed on row {row}: {e}")
                    db.rollback()
                    skipped += 1
                    continue

        db.commit()
        print(f"[Seed] Done — inserted: {inserted}, updated: {updated}, skipped: {skipped}")

    except Exception as e:
        db.rollback()
        print(f"[Seed] Fatal error: {e}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    seed_events()
