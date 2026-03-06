export interface UserPreferences {
  budget: number;
  preferred_genres: string[];
  latitude: number;
  longitude: number;
  food_preference: string;
  avoid_crowds?: boolean;
  max_distance_km?: number;
}

export interface ScoreDetail {
  value: number;
  description: string;
}

// Matches exact backend Event response shape
export interface EventSummary {
  id: string;
  name: string;
  date: string;
  genre?: string;
  latitude?: number;
  longitude?: number;
  is_verified?: boolean;

  media: {
    poster_url?: string | null;
    thumbnail_url?: string | null;
  };

  ticketing: {
    price: number;
    is_free: boolean;
    ticket_url?: string | null;
    currency: string;
  };

  location: {
    venue_name?: string | null;
    address?: string | null;
    city?: string | null;
  };
}

export interface Recommendation {
  event: EventSummary;
  relevance_score: number;
  distance_km?: number;
  explanation?: string;
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

// Shape of the full chat endpoint response
export interface ChatResponse {
  needs_clarification: boolean;
  question?: string;
  interpretation?: {
    budget: number;
    genres: string[];
    food_preference: string;
    distance_preference: string | null;
    priority: string | null;
    confidence: number;
    location: {
      latitude: number;
      longitude: number;
      using_default_location: boolean;
    };
  };
  results: Recommendation[];
  message?: string;
  location_warning?: string;
}

// Shape of the recommendations endpoint response
export interface RecommendationsResponse {
  results: Recommendation[];
  message?: string;
}