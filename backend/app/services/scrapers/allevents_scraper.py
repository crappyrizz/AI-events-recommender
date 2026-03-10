"""
Allevents Kenya scraper using Playwright.

Scrapes events from multiple Kenyan cities on allevents.in.
Each city has its own page: allevents.in/{city}

Why Playwright?
    Allevents is JS-rendered (Vue.js). requests + BeautifulSoup would
    get empty placeholders. Playwright runs a real headless browser,
    waits for JS to populate the cards, then reads the HTML.

Usage:
    from app.services.scrapers.allevents_scraper import AlleventsScraper
    scraper = AlleventsScraper()
    events = scraper.scrape()
"""

from os import name
import re
import logging
from datetime import datetime, timezone
from typing import Optional
import requests
from bs4 import BeautifulSoup

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------
# Kenyan cities to scrape
# Each entry is (url_slug, city_name, latitude, longitude)
# Coordinates are city centers — used for distance scoring
# ------------------------------------------------------------------

KENYA_CITIES = [
    ("nairobi",   "Nairobi",   -1.2921,  36.8219),
    ("mombasa",   "Mombasa",   -4.0435,  39.6682),
    ("kisumu",    "Kisumu",    -0.0917,  34.7679),
    ("nakuru",    "Nakuru",    -0.3031,  36.0800),
    ("eldoret",   "Eldoret",    0.5143,  35.2698),
    ("thika",     "Thika",     -1.0332,  37.0693),
    ("naivasha",  "Naivasha",  -0.7167,  36.4333),
    ("nyeri",     "Nyeri",     -0.4167,  36.9500),
    ("kisii",     "Kisii",     -0.6817,  34.7667),
    ("kakamega",  "Kakamega",   0.2827,  34.7519),
]

SCROLL_PAUSES  = 4       # scrolls per city page to load more cards
SCROLL_WAIT_MS = 1500    # ms to wait after each scroll
PAGE_TIMEOUT   = 30000   # 30 seconds max page load


# ------------------------------------------------------------------
# Scraper
# ------------------------------------------------------------------

class AlleventsScraper:
    """
    Scrapes event listings from allevents.in for multiple Kenyan cities.

    We launch ONE browser instance and reuse it across all city pages.
    This is much more efficient than launching a new browser per city.

    Flow:
        1. Launch headless Firefox once
        2. For each city:
            a. Navigate to allevents.in/{city}
            b. Wait for event cards to render
            c. Scroll to load more cards
            d. Extract data from each card
        3. Close browser
        4. Return all events combined
    """

    def scrape(self) -> list[dict]:
        """
        Scrape all Kenyan cities and return combined event list.

        Returns:
            List of raw event dicts ready for upsert into DB.
        """
        logger.info(f"[Allevents] Starting scrape for {len(KENYA_CITIES)} cities...")
        all_events = []

        with sync_playwright() as p:

            # Launch Firefox headless — lighter than Chromium on RAM
            browser = p.firefox.launch(headless=True, slow_mo=50)
            page = browser.new_page(viewport={"width": 1280, "height": 800})

            # Block images/fonts/stylesheets — we only need text data
            # This makes scraping significantly faster and lighter
            def block_resources(route, request):
                if request.resource_type in ["image", "media", "font", "stylesheet"]:
                    route.abort()
                else:
                    route.continue_()

            page.route("**/*", block_resources)

            for slug, city_name, city_lat, city_lng in KENYA_CITIES:
                url = f"https://allevents.in/{slug}"
                logger.info(f"[Allevents] Scraping {city_name} — {url}")

                city_events = self._scrape_city(
                    page, url, city_name, city_lat, city_lng
                )
                all_events.extend(city_events)
                logger.info(
                    f"[Allevents] {city_name} done — "
                    f"{len(city_events)} events found. "
                    f"Total so far: {len(all_events)}"
                )

            browser.close()

        logger.info(f"[Allevents] Full scrape complete — {len(all_events)} total events")
        return all_events

    # ------------------------------------------------------------------
    # Per-city scrape
    # ------------------------------------------------------------------

    def _scrape_city(
        self,
        page,
        url: str,
        city_name: str,
        city_lat: float,
        city_lng: float,
    ) -> list[dict]:
        """
        Scrape a single city page and return its events.

        Args:
            page: Playwright page (reused across cities)
            url: Full allevents.in city URL
            city_name: Human readable city name e.g. "Nairobi"
            city_lat: City center latitude for distance scoring
            city_lng: City center longitude for distance scoring
        """
        events = []

        try:
            page.goto(url, wait_until="domcontentloaded", timeout=PAGE_TIMEOUT)

            # Wait for at least one event card to appear
            # If no cards appear within timeout, this city has no events
            page.wait_for_selector("li.event-card", timeout=PAGE_TIMEOUT)

            # Scroll down to trigger lazy loading of more cards
            for i in range(SCROLL_PAUSES):
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(SCROLL_WAIT_MS)
                
                # Wait for lazy-loaded images to inject into the DOM
            try:
                page.wait_for_selector("li.event-card div.banner-cont img", timeout=8000)
            except:
                pass  # Some pages may have no images — continue anyway
            
            # Scroll back to top so all cards are in view, triggering any
            # remaining lazy loaders that only fire when elements are visible
            page.evaluate("window.scrollTo(0, 0)")
            page.wait_for_timeout(1500)


            # Read all rendered event cards
            cards = page.query_selector_all("li.event-card")
            logger.info(f"[Allevents] {city_name}: {len(cards)} cards found")

            for card in cards:
                try:
                    event = self._parse_card(card, page, city_name, city_lat, city_lng)
                    if event:
                        events.append(event)
                except Exception as e:
                    logger.warning(f"[Allevents] Card parse error in {city_name}: {e}")
                    continue

        except PlaywrightTimeout:
            # City page exists but no events loaded — not an error
            logger.info(f"[Allevents] {city_name}: no events found or page timed out")
        except Exception as e:
            logger.error(f"[Allevents] {city_name} scrape failed: {e}")

        return events

    # ------------------------------------------------------------------
    # Card parser — same HTML structure across all city pages
    # ------------------------------------------------------------------

    def _parse_card(
        self,
        card,
        page,
        city_name: str,
        city_lat: float,
        city_lng: float,
    ) -> Optional[dict]:
        """
        Extract event data from a single <li class="event-card"> element.

        Args:
            card: Playwright element handle for the event card
            page: Playwright page instance for JS evaluation
            city_name: Human readable city name e.g. "Nairobi"
            city_lat: City center latitude for distance scoring
            city_lng: City center longitude for distance scoring

        HTML structure (mapped by inspecting allevents.in/nairobi):

        <li class="event-card event-card-link"
            data-link="https://allevents.in/nairobi/event-name/ID"
            data-eid="ID">
            <div class="banner-cont">
                <img class="banner-img" data-src="poster-url">
            </div>
            <div class="meta">
                <div class="meta-top">
                    <div class="meta-top-info">
                        <div class="date">Sun, 28 Jun • 09:00 AM</div>
                    </div>
                </div>
                <div class="meta-middle">
                    <div class="title"><a><h3>Event Name</h3></a></div>
                    <div class="location">Venue Name</div>
                </div>
                <div class="meta-bottom">
                    <div class="price-container">
                        <span class="price">Free</span>
                    </div>
                </div>
            </div>
        </li>
        """

        # --- Source URL (required for deduplication) ---
        source_url = card.get_attribute("data-link")
        if not source_url:
            return None

        # --- Poster image ---
        # Allevents uses data-src for lazy loading
        
        # Try multiple selectors in order of specificity
        poster_url = None
        img = (
            card.query_selector("div.banner-cont img.banner-img") or
            card.query_selector("div.banner-cont img") or
            card.query_selector("img.banner-img") or
            card.query_selector("div.event-img img") or
            card.query_selector("img[data-src]") or
            card.query_selector("img")
        )
        if img:
            poster_url = (
                img.get_attribute("data-src") or
                img.get_attribute("data-lazy-src") or
                img.get_attribute("data-original") or
                img.get_attribute("src")
            )

        # Clean up — reject base64 placeholders and empty strings
        if poster_url and (poster_url.startswith("data:") or poster_url.strip() == ""):
            poster_url = None
            
        


        # Fallback — grab og:image from event detail page via HTTP (fast, no browser)
        if not poster_url and source_url:
            try:
                resp = requests.get(source_url, timeout=8, headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                })
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, "html.parser")
                    og = soup.find("meta", property="og:image")
                    if og and og.get("content"):
                        poster_url = og["content"]
            except Exception:
                pass    
        
        

        # --- Event name (required) ---
        name = None
        name_el = card.query_selector("div.meta-middle div.title h3")
        if name_el:
            name = name_el.inner_text().strip()
        if not name:
            return None
        
        if not poster_url:
            all_imgs = card.query_selector_all("img")
            print(f"[DEBUG] No image for '{name}' — found {len(all_imgs)} img tags")
            banner = card.query_selector("div.banner-cont")
            if banner:
                style = banner.get_attribute("style")
                bg_style = page.evaluate("el => window.getComputedStyle(el).backgroundImage", banner)
                print(f"  banner style attr: {style}")
                print(f"  banner computed bg: {bg_style[:100] if bg_style else None}")
            for i, debug_img in enumerate(all_imgs):
                print(f"  img[{i}] src={debug_img.get_attribute('src')[:80] if debug_img.get_attribute('src') else None}")
                print(f"  img[{i}] data-src={debug_img.get_attribute('data-src')[:80] if debug_img.get_attribute('data-src') else None}")
                print(f"  img[{i}] class={debug_img.get_attribute('class')}")

        # --- Venue ---
        venue_name = None
        location_el = card.query_selector("div.meta-middle div.location")
        if location_el:
            venue_name = location_el.inner_text().strip()

        # --- Date ---
        # Format: "Sun, 28 Jun • 09:00 AM"
        date_text = None
        date_el = card.query_selector("div.meta-top div.date")
        if date_el:
            date_text = date_el.inner_text().strip()
        parsed_date = self._parse_date(date_text)

        # --- Price ---
        price_text = None
        price_el = card.query_selector("div.meta-bottom span.price")
        if price_el:
            price_text = price_el.inner_text().strip()
        price_min, price_max, is_free = self._parse_price(price_text)
        if price_min == 0.0:
            is_free = True

        # --- Guess event_type from name/venue keywords ---
        # This is a simple heuristic — outdoor keywords → outdoor type
        outdoor_keywords = ["trail", "run", "marathon", "park", "garden",
                            "outdoor", "open air", "beach", "safari", "hike"]
        name_lower = name.lower()
        venue_lower = (venue_name or "").lower()
        is_outdoor = any(
            kw in name_lower or kw in venue_lower
            for kw in outdoor_keywords
        )

        return {
            "name":             name,
            "source":           "allevents",
            "source_url":       source_url,
            "poster_url":       poster_url,
            "venue_name":       venue_name,
            "city":             city_name,
            "latitude":         city_lat,    # city center coords as fallback
            "longitude":        city_lng,
            "date":             parsed_date,
            "ticket_price":     price_min,
            "ticket_price_min": price_min,
            "ticket_price_max": price_max,
            "ticket_url":       source_url,
            "is_free":          is_free,
            "currency":         "KES",
            "event_type":       "outdoor" if is_outdoor else "indoor",
            "crowd_level":      "MEDIUM",
            "scraped_at":       datetime.now(timezone.utc),
            "last_refreshed_at": datetime.now(timezone.utc),
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _parse_date(self, date_text: str) -> Optional[str]:
        """
        Convert Allevents date string to YYYY-MM-DD.

        Input:  "Sun, 28 Jun • 09:00 AM"
        Output: "2026-06-28"

        Logic:
            - Strip the time part after •
            - Try current year first, then next year
            - Only return dates in the future (past events are useless)
        """
        if not date_text:
            return None

        try:
            date_part = date_text.split("•")[0].strip()
            current_year = datetime.utcnow().year

            for year in [current_year, current_year + 1]:
                try:
                    dt = datetime.strptime(f"{date_part} {year}", "%a, %d %b %Y")
                    if dt.date() >= datetime.utcnow().date():
                        return dt.strftime("%Y-%m-%d")
                except ValueError:
                    continue

            return None

        except Exception:
            return None

    def _parse_price(self, price_text: str) -> tuple[float, float, bool]:
        """
        Parse price string into (min, max, is_free).

        Examples:
            "Free"         → (0.0, 0.0, True)
            "KES 500"      → (500.0, 500.0, False)
            "KES 500-2000" → (500.0, 2000.0, False)
        """
        if not price_text:
            return 0.0, 0.0, False

        clean = price_text.lower().replace(",", "").strip()

        if "free" in clean:
            return 0.0, 0.0, True

        clean = re.sub(r"(kes|ksh|usd|\$)", "", clean).strip()

        # Range
        range_match = re.search(r"(\d+\.?\d*)\s*[-–]\s*(\d+\.?\d*)", clean)
        if range_match:
            return float(range_match.group(1)), float(range_match.group(2)), False

        # Single price
        single_match = re.search(r"(\d+\.?\d*)", clean)
        if single_match:
            price = float(single_match.group(1))
            return price, price, price == 0.0

        return 0.0, 0.0, False
