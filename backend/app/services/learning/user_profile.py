"""
User preference profile builder.
Derives genre and crowd preferences from past event interactions.
Now that events are in PostgreSQL, we can join interactions with events
to build a meaningful preference profile.
"""

from collections import Counter
from sqlalchemy.orm import Session

from app.models.event_interaction import EventInteraction
from app.models.event import Event


class UserPreferenceProfile:
    """
    Builds a lightweight preference profile from a user's interaction history.

    Attributes:
        genre_bias  : Counter mapping genre → bias score (+ve = liked, -ve = disliked)
        crowd_bias  : Float adjustment for crowd preference (-ve = prefers quiet events)
        interest_count  : Total INTERESTED interactions
        dislike_count   : Total NOT_INTERESTED interactions
    """

    # How much each interaction shifts the bias
    INTEREST_WEIGHT     =  0.1   # positive nudge per INTERESTED interaction
    DISLIKE_WEIGHT      = -0.15  # stronger negative nudge per NOT_INTERESTED
    CROWD_PENALTY       = -0.05  # applied per NOT_INTERESTED on a HIGH crowd event
    CROWD_BOOST         =  0.03  # applied per INTERESTED on a LOW crowd event

    def __init__(self, db: Session, user_id: int):
        self.db      = db
        self.user_id = user_id

        self.genre_bias:   Counter = Counter()
        self.crowd_bias:   float   = 0.0
        self.interest_count: int   = 0
        self.dislike_count:  int   = 0

        self._build_profile()

    def _build_profile(self):
        """
        Join interactions with events to extract genre and crowd preferences.
        """
        # Load all interactions for this user
        interactions = (
            self.db.query(EventInteraction)
            .filter(EventInteraction.user_id == self.user_id)
            .all()
        )

        if not interactions:
            return

        # Collect event IDs so we can batch-load events
        event_ids = [i.event_id for i in interactions]

        # Load matching events from DB
        events_by_id = {
            e.id: e
            for e in self.db.query(Event).filter(Event.id.in_(event_ids)).all()
        }

        for interaction in interactions:
            event = events_by_id.get(interaction.event_id)
            itype = interaction.interaction_type

            if itype == "INTERESTED":
                self.interest_count += 1
                if event and event.genre:
                    self.genre_bias[event.genre] += self.INTEREST_WEIGHT
                if event and event.crowd_level == "LOW":
                    self.crowd_bias += self.CROWD_BOOST

            elif itype == "NOT_INTERESTED":
                self.dislike_count += 1
                if event and event.genre:
                    self.genre_bias[event.genre] += self.DISLIKE_WEIGHT
                if event and event.crowd_level == "HIGH":
                    self.crowd_bias += self.CROWD_PENALTY

        # Clamp crowd_bias to a reasonable range so it
        # doesn't dominate the relevance score
        self.crowd_bias = max(-0.3, min(0.3, self.crowd_bias))

    def summary(self) -> dict:
        """Return a readable summary of the profile — useful for debugging."""
        return {
            "user_id":       self.user_id,
            "interest_count": self.interest_count,
            "dislike_count":  self.dislike_count,
            "genre_bias":     dict(self.genre_bias),
            "crowd_bias":     self.crowd_bias,
        }
