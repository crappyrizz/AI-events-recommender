"""
LLM-based natural language interpreter for event search queries.
Converts user messages into structured JSON preference objects.
"""

import requests
import json
import re

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:1.5b"

SYSTEM_PROMPT = """You are a JSON-only data extraction engine. You never write sentences or explanations.

Your ONLY task: read a user event search query and output a single valid JSON object.

OUTPUT FORMAT (strict JSON, no markdown, no text outside the JSON):
{
    "budget": float or null,
    "preferred_genres": [string] or [],
    "distance_preference": "near" or "far" or null,
    "food_preference": string or null,
    "weight_emphasis": "budget" or "genre" or "distance" or "food_preference" or null,
    "needs_clarification": boolean,
    "follow_up_question": string or null,
    "confidence": float
}

RULES:
- weight_emphasis must be a single string key name or null. Never an object.
- confidence must be between 0.0 and 1.0.
- If query is too vague, set needs_clarification to true and provide follow_up_question.
- NEVER output anything except the JSON object.

EXAMPLES:

User: cheap music events near me with food budget 50
Output: {"budget": 50.0, "preferred_genres": ["music"], "distance_preference": "near", "food_preference": "any", "weight_emphasis": "budget", "needs_clarification": false, "follow_up_question": null, "confidence": 0.9}

User: looking for tech events
Output: {"budget": null, "preferred_genres": ["tech"], "distance_preference": null, "food_preference": null, "weight_emphasis": "genre", "needs_clarification": false, "follow_up_question": null, "confidence": 0.7}

User: I want something far away with great food, dont care about price
Output: {"budget": null, "preferred_genres": [], "distance_preference": "far", "food_preference": "any", "weight_emphasis": "food_preference", "needs_clarification": false, "follow_up_question": null, "confidence": 0.75}

User: events this weekend
Output: {"budget": null, "preferred_genres": [], "distance_preference": null, "food_preference": null, "weight_emphasis": null, "needs_clarification": true, "follow_up_question": "What type of events interest you? Music, tech, food, or sports?", "confidence": 0.3}

User: something fun
Output: {"budget": null, "preferred_genres": [], "distance_preference": null, "food_preference": null, "weight_emphasis": null, "needs_clarification": true, "follow_up_question": "Do you have a budget in mind, and what kind of events do you enjoy?", "confidence": 0.2}

User: {user_query}
Output:"""


def interpret_with_llm(message: str) -> dict:
    """
    Extract structured event preferences from a natural language user message.

    Args:
        message: Raw user input string.

    Returns:
        Dictionary with keys: budget, preferred_genres, distance_preference,
        food_preference, weight_emphasis, needs_clarification,
        follow_up_question, confidence.
    """
    formatted_prompt = SYSTEM_PROMPT.replace("{user_query}", message)

    payload = {
        "model": MODEL,
        "prompt": formatted_prompt,
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0,
            "top_p": 0.1,
            "stop": ["\n\n", "User:", "Human:", "Assistant:"]
        }
    }

    try:
        print(f"[LLM] Sending query: {message}")
        response = requests.post(OLLAMA_URL, json=payload, timeout=30)
        response.raise_for_status()

        raw = response.json()
        print(f"[LLM] Raw response: {raw}")

        text = raw.get("response", "").strip()
        print(f"[LLM] Text response: {text}")

        if text:
            # Attempt 1: direct parse
            try:
                parsed = json.loads(text)
                return _build_result(parsed)
            except json.JSONDecodeError:
                pass

            # Attempt 2: extract JSON block from text
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                try:
                    parsed = json.loads(json_match.group())
                    return _build_result(parsed)
                except json.JSONDecodeError:
                    pass

        print("[LLM] Could not parse LLM response, falling back to manual parser.")

    except requests.exceptions.Timeout:
        print("[LLM] Request timed out.")
    except requests.exceptions.ConnectionError:
        print("[LLM] Could not connect to Ollama. Is it running?")
    except Exception as e:
        print(f"[LLM] Unexpected error: {e}")

    return manual_fallback_parse(message)


def _build_result(parsed: dict) -> dict:
    """
    Normalize and validate a parsed LLM JSON response.
    Ensures all required keys exist with correct types.
    """
    valid_emphasis = {"budget", "genre", "distance", "food_preference"}

    weight_emphasis = parsed.get("weight_emphasis")
    if weight_emphasis not in valid_emphasis:
        weight_emphasis = None

    confidence = parsed.get("confidence", 0.5)
    if not isinstance(confidence, (int, float)):
        confidence = 0.5
    confidence = max(0.0, min(1.0, float(confidence)))

    budget = parsed.get("budget")
    if budget is not None:
        try:
            budget = float(budget)
        except (ValueError, TypeError):
            budget = None

    preferred_genres = parsed.get("preferred_genres", [])
    if not isinstance(preferred_genres, list):
        preferred_genres = []

    result = {
        "budget": budget,
        "preferred_genres": preferred_genres,
        "distance_preference": parsed.get("distance_preference"),
        "food_preference": parsed.get("food_preference"),
        "weight_emphasis": weight_emphasis,
        "needs_clarification": bool(parsed.get("needs_clarification", False)),
        "follow_up_question": parsed.get("follow_up_question"),
        "confidence": confidence
    }

    print(f"[LLM] Parsed result: {result}")
    return result


def manual_fallback_parse(message: str) -> dict:
    """
    Rule-based fallback parser used when the LLM fails to return valid JSON.
    Covers common patterns: budget keywords, genre keywords, distance, food types.
    """
    message_lower = message.lower()

    result = {
        "budget": None,
        "preferred_genres": [],
        "distance_preference": None,
        "food_preference": None,
        "weight_emphasis": None,
        "needs_clarification": True,
        "follow_up_question": "Could you clarify what you're looking for? (e.g., type of event, budget, location)",
        "confidence": 0.2
    }

    # --- Budget ---
    budget_match = re.search(r'budget\s*(?:of\s*)?\$?(\d+)', message_lower)
    dollar_match = re.search(r'\$(\d+)', message_lower)
    under_match = re.search(r'under\s*\$?(\d+)', message_lower)

    if budget_match:
        result["budget"] = float(budget_match.group(1))
    elif dollar_match:
        result["budget"] = float(dollar_match.group(1))
    elif under_match:
        result["budget"] = float(under_match.group(1))
    elif "cheap" in message_lower:
        result["budget"] = 30.0
    elif "free" in message_lower:
        result["budget"] = 0.0

    if result["budget"] is not None or "cheap" in message_lower or "free" in message_lower:
        result["weight_emphasis"] = "budget"

    # --- Genres ---
    genre_map = {
        "music": ["music", "concert", "gig", "band", "live music"],
        "tech": ["tech", "technology", "coding", "startup", "hackathon", "developer"],
        "food": ["food festival", "food fair", "food event"],
        "sports": ["sports", "run", "marathon", "football", "basketball", "fitness"],
        "business": ["business", "expo", "networking", "conference", "summit"],
        "art": ["art", "gallery", "exhibition", "museum"],
        "comedy": ["comedy", "stand-up", "standup"],
    }

    genres = []
    for genre, keywords in genre_map.items():
        if any(kw in message_lower for kw in keywords):
            genres.append(genre)

    result["preferred_genres"] = genres
    if genres and result["weight_emphasis"] is None:
        result["weight_emphasis"] = "genre"

    # --- Distance ---
    if any(w in message_lower for w in ["near", "nearby", "around", "close", "local"]):
        result["distance_preference"] = "near"
    elif any(w in message_lower for w in ["far", "away", "outside", "travel"]):
        result["distance_preference"] = "far"

    # --- Food preference ---
    food_types = ["bbq", "pizza", "snacks", "healthy", "cocktails", "buffet",
                  "international", "vegan", "vegetarian", "seafood", "street food"]
    for food in food_types:
        if food in message_lower:
            result["food_preference"] = food
            break

    if "food" in message_lower and not result["food_preference"]:
        result["food_preference"] = "any"

    # --- Determine if clarification still needed ---
    has_enough_info = (
        result["budget"] is not None
        or result["preferred_genres"]
        or result["food_preference"]
        or result["distance_preference"]
    )

    if has_enough_info:
        result["needs_clarification"] = False
        result["follow_up_question"] = None
        result["confidence"] = 0.55

    return result


def extract_json(text: str) -> str | None:
    """Legacy helper: extract first JSON object from a text string."""
    match = re.search(r'\{.*\}', text, re.DOTALL)
    return match.group(0) if match else None
