import { useState, useEffect } from "react";
import PreferenceForm from "../components/PreferenceForm";
import { getRecommendations, ApiError } from "../api/recommendations";
import type { Recommendation, UserPreferences } from "../types/recommendation";
import RecommendationCard from "../components/RecommendationCard";
import SortControl from "../components/SortControl";
import SkeletonCard from "../components/SkeletonCard";
import type { SortOption } from "../types/sorting";
import { errorMessageFor } from "../utils/errorMessages";
import type { ErrorType } from "../utils/errorMessages";





export default function HomePage() {
  const [results, setResults] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(false);
  const [errorType, setErrorType] = useState<ErrorType | null>(null);
  const [sortBy, setSortBy] = useState<SortOption>("best");
  const [preferences, setPreferences] = useState<UserPreferences | null>(null);

  async function fetchRecommendations(
    prefs: UserPreferences,
    sort: SortOption
  ) {
    const MIN_LOADING_MS = 600; // ensure skeleton visible for at least this duration
    const start = Date.now();
    try {
      setLoading(true);
      setErrorType(null);
      const data = await getRecommendations(prefs, sort);
      const elapsed = Date.now() - start;
      const remaining = Math.max(0, MIN_LOADING_MS - elapsed);
      if (remaining > 0) {
        await new Promise((resolve) => setTimeout(resolve, remaining));
      }
      setResults(data);
    } catch (err) {
      if (err instanceof ApiError) {
        setErrorType(err.type);
      } else {
        setErrorType("unknown_error");
      }
    } finally {
      setLoading(false);
    }
  }

  async function handleSubmit(userPreferences: UserPreferences) {
    setPreferences(userPreferences);
    await fetchRecommendations(userPreferences, sortBy);
  }

  // Refetch when sort changes
  useEffect(() => {
    if (preferences && results.length > 0) {
      fetchRecommendations(preferences, sortBy);
    }
  }, [sortBy]);

  return (
    <div style={{
      padding: "clamp(1rem, 5vw, 2rem)",
      maxWidth: "900px",
      margin: "0 auto"
    }}>
      <h1 style={{ marginTop: 0 }}>AI Events Recommender</h1>

      <PreferenceForm onSubmit={handleSubmit} />

      <SortControl value={sortBy} onChange={setSortBy} />

      {loading && (
        <>
          {[...Array(3)].map((_, i) => (
            <SkeletonCard key={i} />
          ))}
        </>
      )}



      {errorType && (
        (() => {
          const info = errorMessageFor(errorType);
          return (
            <div style={{ marginTop: 20 }} role="alert" aria-live="assertive">
              <div style={{ fontWeight: 600, color: "#111827" }}>{info.title}</div>
              <div style={{ color: "#6b7280", marginTop: 6 }}>{info.message}</div>
              <div style={{ marginTop: 8 }}>
                <button
                  onClick={() => {
                    // retry last request
                    if (preferences) {
                      fetchRecommendations(preferences, sortBy);
                    } else {
                      setErrorType(null);
                    }
                  }}
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
            </div>
          );
        })()
      )}

      {!loading && results.length === 0 && !errorType && preferences && (
        <div className="empty-state">
          <div className="empty-state-content">
            <div className="empty-state-icon">🎭</div>
            <h2>No events found</h2>
            <p className="empty-state-description">
              We couldn't find any events matching your preferences. Try adjusting your criteria below to discover more events.
            </p>
            <ul className="empty-state-suggestions">
              <li>Increase your budget range</li>
              <li>Expand your genre preferences</li>
              <li>Check nearby locations</li>
              <li>Disable "Avoid crowds" filter</li>
            </ul>
            <button
              onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
              style={{
                marginTop: 16,
                padding: "10px 20px",
                background: "#2563EB",
                color: "white",
                border: "none",
                borderRadius: 6,
                cursor: "pointer",
                fontSize: "1em",
                fontWeight: 500,
              }}
            >
              ↑ Modify Preferences
            </button>
          </div>
        </div>
      )}

      <div>
        {results.map((rec) => (
            <RecommendationCard
                key={rec.event?.id ?? Math.random()}
                recommendation={rec}
            />
        ))}
      </div>


    </div>
  );
}
