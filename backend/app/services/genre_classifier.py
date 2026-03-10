"""
Genre classifier for scraped events.

Strategy:
    1. Noise filter  — skip/delete spam, betting, overseas events
    2. Keyword match — fast, Kenya-specific, covers ~60% of events
    3. LLM fallback  — Ollama/Qwen for events keywords can't classify

Usage:
    from app.services.genre_classifier import GenreClassifier
    genre = GenreClassifier.classify("Nairobi Jazz Night", "Live jazz band")
    # returns "Music"
"""

import re
import json
import logging
import requests
from typing import Optional

logger = logging.getLogger(__name__)

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL      = "qwen2.5:1.5b"

# Canonical genre list — all classifications must use these exact strings
VALID_GENRES = [
    "Music", "Tech", "Food", "Sports", "Business",
    "Education", "Culture", "Travel", "Arts", "Nightlife", "Wellness"
]

# ------------------------------------------------------------------
# LLM prompt for genre classification
# ------------------------------------------------------------------

GENRE_CLASSIFY_PROMPT = """You are a JSON-only event genre classifier.

Given an event name and description, return ONLY a JSON object with one key "genre".
Choose from ONLY these genres: Music, Tech, Food, Sports, Business, Education, Culture, Travel, Arts, Nightlife, Wellness
If none fit, use the closest match. Never return null or None.

OUTPUT FORMAT (strict JSON, no markdown, no extra text):
{"genre": "Music"}

EXAMPLES:
Event: "ISUKUTI FEST EDITION 2" | Description: ""
Output: {"genre": "Music"}

Event: "NAIROBI LITFEST 2026" | Description: ""
Output: {"genre": "Arts"}

Event: "BACK & FORTH - OLD SCHOOL PARTY!" | Description: ""
Output: {"genre": "Nightlife"}

Event: "26TH INDUSMACH KENYA 2026" | Description: ""
Output: {"genre": "Tech"}

Event: "FLORIDA EXPERIENCE" | Description: ""
Output: {"genre": "Nightlife"}

Event: "THURSDAY | NAIROBI SINGLES MIXER | JEKYLL & HYDE" | Description: ""
Output: {"genre": "Nightlife"}

Event: "MOMBASA 2DAYS 1NIGHT KES.9,800" | Description: ""
Output: {"genre": "Travel"}

Event: "STEPPING OUT - THE NAIROBI JAZZ ORCHESTRA" | Description: ""
Output: {"genre": "Music"}

Event: "DEY SAY - LIVE IN NAIROBI, KENYA" | Description: ""
Output: {"genre": "Music"}

Event: "TRAIL SESSION" | Description: ""
Output: {"genre": "Sports"}

Event: "GALLERIA FIT FEST" | Description: ""
Output: {"genre": "Sports"}

Event: "WACKEN METAL BATTLE KENYA SHOWCASE" | Description: ""
Output: {"genre": "Music"}

Event: "WORLD ORAL HEALTH DAY - WALK" | Description: ""
Output: {"genre": "Wellness"}

Event: "NAIROBI COLOUR FESTIVAL 2026" | Description: ""
Output: {"genre": "Culture"}

Event: "BREAK THE CHAIN" | Description: ""
Output: {"genre": "Culture"}

Event: "13TH POWER & ENERGY KENYA 2026" | Description: ""
Output: {"genre": "Tech"}

Event: "ARSENAL VS. MONACO" | Description: ""
Output: {"genre": "Sports"}

Event: "GREAT RIFT 10 ASIDE 2026" | Description: ""
Output: {"genre": "Sports"}

Event: "BOWLING WITH MEGA ROTARY CLUB" | Description: ""
Output: {"genre": "Sports"}

Event: "VYBZ KARTEL EVENT" | Description: ""
Output: {"genre": "Music"}

Event: "FREE HEALTH CHECKS" | Description: ""
Output: {"genre": "Wellness"}

Event: "ELANI YOUTH ELITE TRIALS 2026" | Description: ""
Output: {"genre": "Sports"}

Event: "PERFORMATIVE ARTS" | Description: ""
Output: {"genre": "Arts"}

Event: "STREET HALISI" | Description: ""
Output: {"genre": "Culture"}

Event: "{name}" | Description: "{description}"
Output:"""


# ------------------------------------------------------------------
# Kenya-specific noise filter
# ------------------------------------------------------------------

NOISE_KEYWORDS = [
    "promo code", "betting", "betwinner", "1xbet", "sportybet",
    "hay farming", "forex trading", "crypto trading", "mlm",
    "pyramid", "recruitment", "admission ongoing", "reporting day",
    "election day", "campus tour", "children's home",
    "discount on service parts",
]

NOISE_VENUES = [
    # Indian cities
    "seattle", "manchester", "ahmedabad", "hyderabad", "mumbai",
    "delhi", "chennai", "kolkata", "bangalore", "ludhiana",
    "tamilnadu", "gujarat", "punjab", "bhopal", "kanpur",
    "bandra", "hubli", "pune", "rajkot", "jaipur", "surat",
    "indore", "vadodara", "nagpur",
    # North American cities
    "tallahassee", "las vegas", "vancouver", "dallas", "regina",
    "duncan", "orono", "vernon", "new hampshire", "hampshire",
    "trinidad", "jersey city", "new jersey",
    # European/other
    "belfast", "wales", "australia", "new zealand", "canada",
    "hong kong", "dubai",
    # Generic overseas indicators
    "bc(", ", bc", ", on(", "isd", " isd",
]


# ------------------------------------------------------------------
# Genre keyword definitions
# Order matters — first match wins
# ------------------------------------------------------------------

GENRE_KEYWORDS: dict[str, list[str]] = {

    "Music": [
        # International
        "jazz", "concert", "live band", "live music", "orchestra",
        "choir", "reggae", "gospel", "afrobeats", "hip hop", "hiphop",
        "rnb", "r&b", "dj", "gig", "band night", "acoustic",
        "karaoke", "open mic", "music festival", "band", "musician",
        "sing", "song", "rap", "dancehall", "edm", "amapiano",
        "live performance", "bashment", "riddim", "metal battle",
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
        "indusmach", "buildexpo", "medexpo", "power & energy",
        "energy expo", "webfair", "gaming", "esports",
    ],

    "Food": [
        "food festival", "food fair", "brunch", "chef", "tasting",
        "barbecue", "bbq", "street food", "culinary", "wine tasting",
        "cocktail", "beer festival", "food tour", "cooking",
        "supper", "dinner", "feast", "nyama choma", "roast",
        "buffet", "food market", "pop up kitchen", "food drive",
        "masterchef", "meat fest", "herbal festival", "popup market",
        "pop up market", "farmers market", "easter popup",
        "cookie", "cookier", "baking",
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
        "paragliding", "rock climbing", "obstacle", "karate",
        "10 aside", "fit fest", "trail session", "bowling",
        "legends cup", "colour run", "esports", "gaming", "fifa", 
        "pes", "dota", "league of legends", "playstation", "xbox", "nintendo",
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
        "ragia forest", "ol pejeta", "safari park", "giraffe centre",
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
        "indusmach", "medexpo", "bridal fair", "pitch night", 
        "startup showcase","business awards",
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
        "puppet show", "short plays", "performative", "improv",
        "sip and paint", "paint", "fashion", "design", "creative", 
        "craft", "illustration", "animation","storytelling", "literary",
        "book", "writing", "author",
    ],

    "Nightlife": [
        "party", "club night", "rooftop", "lounge", "mixer",
        "social night", "dance night", "night out", "vibe",
        "after party", "sundowner", "happy hour", "ladies night",
        "themed party", "halloween", "new year", "nye",
        "valentines", "birthday bash", "pool party", "beach party",
        "rave", "block party", "florida experience", "kizomba",
        "salsa", "latin night", "afro night", "bonfire",
        "get together", "singles mixer", "strangers meetup","social",
        "rooftop party", "rooftop event",
    ],

    "Education": [
        "training", "course", "bootcamp", "class", "lecture",
        "certification", "masterclass", "webinar", "learning",
        "study", "scholarship", "career", "internship",
        "mentorship", "coaching", "skill", "professional development",
        "exam prep", "tutoring", "graduation", "orientation",
        "symposium", "academic", "university", "college", "school",
        "ielts", "pte", "conclave", "ted", "tedx", "hackathon", 
    ],

    "Wellness": [
        "wellness", "mental health", "meditation", "spa",
        "retreat", "yoga", "mindfulness", "therapy", "healing",
        "self care", "self-care", "breathwork", "sound bath",
        "pilates", "nutrition", "health talk", "detox",
        "motivational", "empowerment", "women wellness",
        "holistic", "reiki", "life coach", "world kidney day",
        "transplant", "health fair", "medical", "health check",
        "free health", "oral health", "pregnancy fair",
        "miles for mind",
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
        "zuri awards", "awards", "gala", "colour festival",
        "color festival", "sendoff", "dance"
    ],
}


# ------------------------------------------------------------------
# Classifier
# ------------------------------------------------------------------

class GenreClassifier:

    @staticmethod
    def is_noise(name: str, venue: str = "") -> bool:
        """Check if an event is irrelevant noise (betting, overseas, spam)."""
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
        Keyword-based classification — fast, no LLM.
        Returns genre string or None if no keyword match.
        """
        text = f"{name} {description}".lower()
        text = re.sub(r"[^\w\s]", " ", text)

        for genre, keywords in GENRE_KEYWORDS.items():
            for keyword in keywords:
                pattern = r"\b" + re.escape(keyword.lower()) + r"\b"
                if re.search(pattern, text):
                    logger.debug(f"[GenreClassifier] '{name}' → '{genre}' (matched: '{keyword}')")
                    return genre

        logger.debug(f"[GenreClassifier] '{name}' → no keyword match")
        return None

    @staticmethod
    def classify_with_llm(name: str, description: str = "") -> Optional[str]:
        """
        LLM-based classification fallback via Ollama.
        Used when keyword matching fails.
        Returns a genre from VALID_GENRES or None.
        """
        prompt = GENRE_CLASSIFY_PROMPT\
            .replace("{name}", name)\
            .replace("{description}", description or "")

        payload = {
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {"temperature": 0, "top_p": 0.1}
        }

        try:
            resp = requests.post(OLLAMA_URL, json=payload, timeout=20)
            resp.raise_for_status()
            text = resp.json().get("response", "").strip()
            parsed = json.loads(text)
            genre = parsed.get("genre")

            # Reject null, None string, or anything not in valid list
            if not genre or str(genre).lower() == "none":
                logger.warning(f"[GenreClassifier] LLM returned null/None for '{name}'")
                return None

            if genre in VALID_GENRES:
                logger.debug(f"[GenreClassifier] LLM classified '{name}' → '{genre}'")
                return genre

            logger.warning(f"[GenreClassifier] LLM returned invalid genre '{genre}' for '{name}'")

        except Exception as e:
            logger.warning(f"[GenreClassifier] LLM failed for '{name}': {e}")

        return None

    @staticmethod
    def classify_batch(events: list[dict]) -> list[dict]:
        """
        Classify a list of raw event dicts in place.
        Order: noise check → keyword → LLM fallback.
        Adds/overwrites the 'genre' key on each dict.
        Marks noise events with '_noise': True so upsert can skip them.
        """
        matched        = 0
        llm_classified = 0
        unmatched      = 0
        noise          = 0

        for event in events:
            if GenreClassifier.is_noise(
                event.get("name", ""),
                event.get("venue_name", "") or ""
            ):
                event["_noise"] = True
                noise += 1
                continue

            if not event.get("genre"):
                # Try keywords first
                genre = GenreClassifier.classify(
                    event.get("name", ""),
                    event.get("description", "") or ""
                )

                # LLM fallback
                if not genre:
                    genre = GenreClassifier.classify_with_llm(
                        event.get("name", ""),
                        event.get("description", "") or ""
                    )
                    if genre:
                        llm_classified += 1

                event["genre"] = genre
                if genre:
                    matched += 1
                else:
                    unmatched += 1

        logger.info(
            f"[GenreClassifier] Batch complete — "
            f"keyword: {matched}, llm: {llm_classified}, "
            f"unmatched: {unmatched}, noise: {noise}"
        )
        return events

    @staticmethod
    def reclassify_db(db) -> dict:
        """
        Retroactively classify all null-genre events in DB.
        Order: noise check → keyword → LLM fallback.
        Also normalises 'Technology' → 'Tech' for consistency.

        Args:
            db: SQLAlchemy session

        Returns:
            Summary dict with counts.
        """
        from app.models.event import Event

        events         = db.query(Event).filter(Event.genre.is_(None)).all()
        updated        = 0
        skipped        = 0
        removed        = 0
        llm_classified = 0

        for event in events:
            # Remove noise events from DB entirely
            if GenreClassifier.is_noise(event.name, event.venue_name or ""):
                db.delete(event)
                removed += 1
                continue

            # Try keyword first
            genre = GenreClassifier.classify(event.name, event.description or "")

            # LLM fallback
            if not genre:
                genre = GenreClassifier.classify_with_llm(
                    event.name, event.description or ""
                )
                if genre:
                    llm_classified += 1

            if genre:
                event.genre = genre
                updated += 1
            else:
                skipped += 1

        # Normalise Technology → Tech
        tech_events = db.query(Event).filter(Event.genre == "Technology").all()
        for e in tech_events:
            e.genre = "Tech"

        db.commit()

        logger.info(
            f"[GenreClassifier] DB reclassify complete — "
            f"updated: {updated} (llm: {llm_classified}), "
            f"skipped: {skipped}, removed: {removed}, "
            f"tech_normalized: {len(tech_events)}"
        )

        return {
            "updated":         updated,
            "llm_classified":  llm_classified,
            "skipped":         skipped,
            "removed":         removed,
            "tech_normalized": len(tech_events)
        }
        