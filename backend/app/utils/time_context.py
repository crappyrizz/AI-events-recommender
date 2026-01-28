"""
Date and time context utilities for event recommendations.
"""

from datetime import datetime
from typing import Tuple


def parse_event_date(date_str: str) -> datetime:
    """
    Parse event date string (YYYY-MM-DD format).
    
    Args:
        date_str: Date string in YYYY-MM-DD format
    
    Returns:
        datetime object
    """
    return datetime.strptime(date_str, '%Y-%m-%d')


def is_event_upcoming(event_date_str: str, reference_date: datetime = None) -> bool:
    """
    Check if an event is in the future.
    
    Args:
        event_date_str: Event date string (YYYY-MM-DD format)
        reference_date: Reference date (default: today)
    
    Returns:
        True if event is in future, False otherwise
    """
    if reference_date is None:
        reference_date = datetime.now()
    
    event_date = parse_event_date(event_date_str)
    return event_date >= reference_date


def days_until_event(event_date_str: str, reference_date: datetime = None) -> int:
    """
    Calculate days until event.
    
    Args:
        event_date_str: Event date string (YYYY-MM-DD format)
        reference_date: Reference date (default: today)
    
    Returns:
        Number of days until event (negative if in past)
    """
    if reference_date is None:
        reference_date = datetime.now()
    
    event_date = parse_event_date(event_date_str)
    delta = event_date - reference_date
    return delta.days


def calculate_temporal_score(days_until: int) -> float:
    """
    Calculate temporal relevance score based on days until event.
    
    Prefer events that are soon (within 7 days) but not too far away.
    - 0-7 days: Score increases linearly to 1.0
    - 7-30 days: Score stays high (0.9)
    - 30-60 days: Score decays gradually
    - 60+ days: Low score
    
    Args:
        days_until: Number of days until event
    
    Returns:
        Temporal score (0.0 to 1.0)
    """
    if days_until < 0:
        return 0.0  # Event in past
    
    if days_until <= 7:
        return min(1.0, 0.5 + days_until / 14)  # 0.5 to 1.0
    elif days_until <= 30:
        return 0.9  # High score for near-term events
    elif days_until <= 60:
        return max(0.3, 0.9 - (days_until - 30) / 100)  # Gradual decay
    else:
        return 0.1  # Low score for distant events
