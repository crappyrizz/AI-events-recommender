export interface UserPreferences {
  budget: number;
  preferred_genres: string[];
  latitude: number;
  longitude: number;
  food_preference: string;
  avoid_crowds?: boolean;
}

export interface ScoreDetail {
  value: number;
  description: string;
}

export interface Recommendation {
  event_id: number;
  relevance_score: number;
  score_breakdown: {
    budget?: ScoreDetail;
    genre?: ScoreDetail;
    distance?: ScoreDetail;
    food_preference?: ScoreDetail;
    temporal?: ScoreDetail;
    weather?: ScoreDetail;
    crowd?: ScoreDetail;
  };
}
