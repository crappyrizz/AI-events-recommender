from collections import Counter
from sqlalchemy.orm import Session
from app.models.event_interaction import EventInteraction
from app.api.v1 import interactions


class UserPreferenceProfile:
    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id

        self.genre_bias = Counter()
        self.crowd_bias = 0.0

        self.interest_count = 0
        self.dislike_count = 0
        
        self._build_profile()
        
        


    def _build_profile(self):
        interactions = (
            self.db.query(EventInteraction)
            .filter(EventInteraction.user_id == self.user_id)
            .all()
        )

        # Events are loaded from CSV, not database
        # So we cannot access event details here yet
        # Learning will be limited to interaction counts only

        for i in interactions:
            if i.interaction_type == "INTERESTED":
                self.interest_count += 1
            elif i.interaction_type == "NOT_INTERESTED":
                self.dislike_count += 1

