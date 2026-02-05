import { useState } from "react";
import PreferenceForm from "../components/PreferenceForm";
import { getRecommendations } from "../api/recommendations";
import type { Recommendation, UserPreferences } from "../types/recommendation";
import RecommendationCard from "../components/RecommendationCard";
import SortControl from "../components/SortControl";
import SkeletonCard from "../components/SkeletonCard";





export default function HomePage() {
  const [results, setResults] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sortBy, setSortBy] = useState<
  "best" | "budget" | "distance" | "crowd" | "weather"
>("best");


  async function handleSubmit(preferences: UserPreferences) {
    try {
      setLoading(true);
      setError(null);
        
      const data = await getRecommendations(preferences);
      setResults(data);
    } catch (err) {
      setError("Failed to load recommendations");
    } finally {
      setLoading(false);
    }
  }

  const sortedResults = [...results].sort((a, b) => {
    if (sortBy === "budget") {
      return (b.score_breakdown.budget?.value ?? 0) -
             (a.score_breakdown.budget?.value ?? 0);
    }

    if (sortBy === "distance") {
      return (b.score_breakdown.distance?.value ?? 0) -
             (a.score_breakdown.distance?.value ?? 0);
    }

    if (sortBy === "crowd") {
      return (b.score_breakdown.crowd?.value ?? 0) -
             (a.score_breakdown.crowd?.value ?? 0);
    }

    if (sortBy === "weather") {
      return (b.score_breakdown.weather?.value ?? 0) -
             (a.score_breakdown.weather?.value ?? 0);
    }

    // default: best match
    return b.relevance_score - a.relevance_score;
  });

  return (
    <div style={{ padding: "2rem" }}>
      <h1>AI Events Recommender</h1>

      <PreferenceForm onSubmit={handleSubmit} />

      <SortControl value={sortBy} onChange={setSortBy} />

      {loading && (
        <>
          <SkeletonCard />
          <SkeletonCard />
          <SkeletonCard />
        </>
    )}


      {error && (
        <div style={{ marginTop: 20, color: "#dc2626" }}>
          <p>{error}</p>
          <button
            onClick={() => setError(null)}
            style={{
            marginTop: 8,
            padding: "6px 12px",
            background: "#2563EB",
            color: "white",
            border: "none",
            borderRadius: 6,
            cursor: "pointer",
          }}
        >
            Try Again
          </button>
        </div>
      )}


      {!loading && results.length === 0 && !error && (
        <div style={{ marginTop: 30, textAlign: "center", color: "#6b7280" }}>
          <h3>No events found 🎭</h3>
          <p>Try adjusting your preferences.</p>
        </div>
      )}


    <div>
        {sortedResults.map((rec) => (
            <RecommendationCard
                key={rec.event?.id ?? Math.random()}
                recommendation={rec}
            />
        ))}
    </div>


    </div>
  );
}
