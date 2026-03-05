"""
Genre classifier for scraped events.

Uses keyword matching against event name and description to assign
a parent genre. Fast, lightweight, no LLM required.

Usage:
    from app.services.genre_classifier import GenreClassifier
    genre = GenreClassifier.classify("Nairobi Jazz Night", "Live jazz band")
    # returns "Music"
"""

import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------
# Kenya-specific noise filter
# Events matching these keywords are likely irrelevant (betting sites,
# farming, overseas events etc.) and should be skipped entirely
# ------------------------------------------------------------------

NOISE_KEYWORDS = [
    "promo code", "betting", "betwinner", "1xbet", "sportybet",
    "hay farming", "forex trading", "crypto trading", "mlm",
    "pyramid", "recruitment", "admission ongoing", "reporting day",
    "election day", "campus tour", "children's home",
]

# Known non-Kenya city venues that slip through
NOISE_VENUES = [
    "seattle", "manchester", "ahmedabad", "hyderabad", "mumbai",
    "delhi", "chennai", "kolkata", "bangalore", "ludhiana",
    "tallahassee", "australia", "new zealand", "dubai", "canada",
    "tamilnadu", "gujarat", "punjab", "bhopal", "kanpur",
]


# ------------------------------------------------------------------
# Genre keyword definitions
# Order matters — first match wins
# More specific genres first, broader ones last
# ------------------------------------------------------------------

GENRE_KEYWORDS: dict[str, list[str]] = {

    "Music": [
        # International
        "jazz", "concert", "live band", "live music", "orchestra",
        "choir", "reggae", "gospel", "afrobeats", "hip hop", "hiphop",
        "rnb", "r&b", "dj", "gig", "band night", "acoustic",
        "karaoke", "open mic", "music festival", "band", "musician",
        "sing", "song", "rap", "dancehall", "edm", "amapiano",
        "live performance", "bashment", "riddim",
        # Kenyan specific
        "gengetone", "benga", "taarab", "rhumba", "bongo flava",
        "ohangla", "mugithi", "isukuti", "chakacha", "zilizopendwa",
        "saxophone", "guitar session", "piano night", "bonfire music",
        "90s", "throwback", "unplugged",
    ],

    "Tech": [
        "hackathon", "tech meetup", "startup", "developer",
        "coding", "artificial intelligence", "machine learning",
        "data science", "software", "innovation", "fintech",
        "blockchain", "crypto", "web3", "programming",
        "cybersecurity", "cloud", "devops", "product launch",
        "pitch competition", "tech talk", "digital", "robotics",
        "drone", "technology", "AI", "gitex", "aieverything",
        "indusmach", "buildexpo", "medexpo",
    ],

    "Food": [
        "food festival", "food fair", "brunch", "chef", "tasting",
        "barbecue", "bbq", "street food", "culinary", "wine tasting",
        "cocktail", "beer festival", "food tour", "cooking",
        "supper", "dinner", "feast", "nyama choma", "roast",
        "buffet", "food market", "pop up kitchen", "food drive",
        "masterchef", "meat fest", "herbal festival", "popup market",
        "pop up market", "farmers market", "easter popup",
    ],

    "Sports": [
        "marathon", "trail run", "fun run", "5k", "10k",
        "football", "soccer", "rugby", "basketball", "volleyball",
        "swimming", "athletics", "tournament", "league",
        "championship", "cycling", "triathlon", "crossfit",
        "fitness", "boxing", "wrestling", "tennis", "golf",
        "cricket", "netball", "badminton", "race", "match",
        "cup final", "safari rally", "wrc", "rally", "bike",
        "bicycle", "expedition", "run ", "miles run", "fun day",
        "kids run", "annual run", "easter run", "heels on wheels",
        "paragliding", "rock climbing", "obstacle",
    ],

    "Travel": [
        "tour", "trip", "travel", "holiday", "safari", "excursion",
        "getaway", "adventure", "hike", "hiking", "camping",
        "nature walk", "forest walk", "waterfall", "mountain",
        "mount ", "lake", "beach", "coastal", "island",
        "naivasha", "diani", "zanzibar", "lamu", "mombasa trip",
        "bali", "dubai trip", "sgr experience", "day trip",
        "overnight", "2days", "3days", "4days", "5days",
        "tunnel", "resort daytrip", "suswa", "aberdare",
        "amboseli", "masai mara", "tsavo", "rift valley",
        "oloolua", "karura", "kijabe", "joska", "njabini",
    ],

    "Business": [
        "conference", "expo", "summit", "networking", "seminar",
        "workshop", "leadership", "investment", "entrepreneurship",
        "business forum", "trade fair", "agm", "annual general",
        "investor", "fundraising", "accelerator", "incubator",
        "corporate", "finance", "real estate", "property",
        "insurance", "banking", "economic forum", "ceo",
        "executive", "breakfast meeting", "salesfest",
        "professional administrators", "odoo", "buildexpo",
        "indusmach", "medexpo", "bridal fair",
    ],

    "Arts": [
        "gallery", "exhibition", "art show", "theatre", "theater",
        "play", "comedy show", "stand up", "standup", "film",
        "movie", "photography", "poetry", "spoken word", "museum",
        "sculpture", "painting", "fashion show", "design",
        "creative", "craft", "illustration", "animation",
        "storytelling", "literary", "book", "writing", "author",
        "litfest", "literary festival", "art festival", "comedy night",
        "living room laughs", "paint night", "life drawing",
        "puppet show", "short plays",
    ],

    "Nightlife": [
        "party", "club night", "rooftop", "lounge", "mixer",
        "social night", "dance night", "night out", "vibe",
        "after party", "sundowner", "happy hour", "ladies night",
        "themed party", "halloween", "new year", "nye",
        "valentines", "birthday bash", "pool party", "beach party",
        "rave", "block party", "florida experience", "kizomba",
        "salsa", "latin night", "afro night", "bonfire",
    ],

    "Education": [
        "training", "course", "bootcamp", "class", "lecture",
        "certification", "masterclass", "webinar", "learning",
        "study", "scholarship", "career", "internship",
        "mentorship", "coaching", "skill", "professional development",
        "exam prep", "tutoring", "graduation", "orientation",
        "symposium", "academic", "university", "college", "school",
        "ielts", "pte", "conclave", "ted", "tedx",
    ],

    "Wellness": [
        "wellness", "mental health", "meditation", "spa",
        "retreat", "yoga", "mindfulness", "therapy", "healing",
        "self care", "self-care", "breathwork", "sound bath",
        "pilates", "nutrition", "health talk", "detox",
        "motivational", "empowerment", "women wellness",
        "holistic", "reiki", "life coach", "world kidney day",
        "transplant", "health fair", "medical",
    ],

    "Culture": [
        "cultural", "heritage", "traditional", "community",
        "charity", "fundraiser", "religious", "ceremony",
        "church", "mosque", "temple", "prayer", "worship",
        "carnival", "parade", "national day", "independence",
        "maasai", "kikuyu", "luo", "luhya", "kalenjin",
        "swahili", "african", "diaspora", "awareness",
        "commemoration", "memorial", "civic", "women's day",
        "international women", "gender", "pads drive",
        "mission", "praise", "havan", "iftar", "anniversary",
        "zuri awards", "awards", "gala",
    ],
}


# ------------------------------------------------------------------
# Classifier
# ------------------------------------------------------------------

class GenreClassifier:
    """
    Classifies events into parent genres using keyword matching.

    Matching strategy:
        1. Check against noise filter — skip irrelevant events
        2. Combine event name + description into one text blob
        3. Normalize to lowercase, remove punctuation
        4. Check each genre's keywords against the text
        5. Return first matching genre or None
    """

    @staticmethod
    def is_noise(name: str, venue: str = "") -> bool:
        """
        Check if an event is irrelevant noise (betting, overseas, spam).

        Args:
            name: Event name
            venue: Venue name or address

        Returns:
            True if the event should be skipped
        """
        text = f"{name} {venue}".lower()

        for keyword in NOISE_KEYWORDS:
            if keyword.lower() in text:
                return True

        for city in NOISE_VENUES:
            if city.lower() in text:
                return True

        return False

    @staticmethod
    def classify(name: str, description: str = "") -> Optional[str]:
        """
        Classify an event into a parent genre.

        Args:
            name: Event name e.g. "Nairobi Jazz Night"
            description: Event description (optional)

        Returns:
            Genre string e.g. "Music", "Tech" or None if no match
        """
        text = f"{name} {description}".lower()
        text = re.sub(r"[^\w\s]", " ", text)

        for genre, keywords in GENRE_KEYWORDS.items():
            for keyword in keywords:
                pattern = r"\b" + re.escape(keyword.lower()) + r"\b"
                if re.search(pattern, text):
                    logger.debug(
                        f"[GenreClassifier] '{name}' → '{genre}' "
                        f"(matched: '{keyword}')"
                    )
                    return genre

        logger.debug(f"[GenreClassifier] '{name}' → no match")
        return None

    @staticmethod
    def classify_batch(events: list[dict]) -> list[dict]:
        """
        Classify a list of raw event dicts in place.
        Adds/overwrites the 'genre' key on each dict.
        Also marks noise events so upsert can skip them.
        """
        matched   = 0
        unmatched = 0
        noise     = 0

        for event in events:
            # Mark noise events — scheduler will skip them
            if GenreClassifier.is_noise(
                event.get("name", ""),
                event.get("venue_name", "") or ""
            ):
                event["_noise"] = True
                noise += 1
                continue

            if not event.get("genre"):
                genre = GenreClassifier.classify(
                    event.get("name", ""),
                    event.get("description", "") or ""
                )
                event["genre"] = genre
                if genre:
                    matched += 1
                else:
                    unmatched += 1

        logger.info(
            f"[GenreClassifier] Batch complete — "
            f"matched: {matched}, unmatched: {unmatched}, noise: {noise}"
        )
        return events

    @staticmethod
    def reclassify_db(db) -> dict:
        """
        Retroactively classify all events in DB with genre=null.
        Also removes noise events from the DB.
        Run this after updating the classifier keywords.

        Args:
            db: SQLAlchemy session

        Returns:
            Summary dict: {updated, skipped, removed}
        """
        from app.models.event import Event

        events  = db.query(Event).filter(Event.genre.is_(None)).all()
        updated = 0
        skipped = 0
        removed = 0

        for event in events:
            # Remove noise events from DB entirely
            if GenreClassifier.is_noise(
                event.name,
                event.venue_name or ""
            ):
                db.delete(event)
                removed += 1
                continue

            genre = GenreClassifier.classify(
                event.name,
                event.description or ""
            )
            if genre:
                event.genre = genre
                updated += 1
            else:
                skipped += 1

        db.commit()
        logger.info(
            f"[GenreClassifier] DB reclassify — "
            f"updated: {updated}, skipped: {skipped}, removed: {removed}"
        )
        return {"updated": updated, "skipped": skipped, "removed": removed}
