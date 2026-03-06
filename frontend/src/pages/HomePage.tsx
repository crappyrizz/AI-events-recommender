import { useState, useEffect } from "react";
import ChatBox from "../components/ChatBox";
import RecommendationCard from "../components/RecommendationCard";
import SkeletonCard from "../components/SkeletonCard";
import SortControl from "../components/SortControl";
import MapView from "../components/MapView";
import PreferenceForm from "../components/PreferenceForm";
import { getRecommendations, ApiError } from "../api/recommendations";
import type { Recommendation, ChatResponse, UserPreferences } from "../types/recommendation";
import type { SortOption } from "../types/sorting";
import type { ErrorType } from "../utils/errorMessages";
import { errorMessageFor } from "../utils/errorMessages";

export default function HomePage() {
  const [results, setResults] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(false);
  const [errorType, setErrorType] = useState<ErrorType | null>(null);
  const [sortBy, setSortBy] = useState<SortOption>("best");
  const [viewMode, setViewMode] = useState<"list" | "map">("list");
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [preferences, setPreferences] = useState<UserPreferences | null>(null);
  const [locationWarning, setLocationWarning] = useState<string | null>(null);
  const [resultCount, setResultCount] = useState<number | null>(null);

  // Restore previous session
  useEffect(() => {
    const savedResults = localStorage.getItem("recommendations");
    if (savedResults) {
      const parsed = JSON.parse(savedResults);
      setResults(parsed);
      setResultCount(parsed.length);
    }
  }, []);

  function handleChatResults(response: ChatResponse) {
    const recs = response.results ?? [];
    setResults(recs);
    setResultCount(recs.length);
    setLocationWarning(response.location_warning ?? null);
    setErrorType(null);
    localStorage.setItem("recommendations", JSON.stringify(recs));
  }

  function handleClear() {
    setResults([]);
    setResultCount(null);
    setErrorType(null);
    setLocationWarning(null);
    setPreferences(null);
    localStorage.removeItem("recommendations");
    localStorage.removeItem("user_preferences");
  }

  // Advanced form submit
  async function handleAdvancedSubmit(prefs: UserPreferences) {
    setPreferences(prefs);
    setLoading(true);
    setErrorType(null);
    try {
      const data = await getRecommendations(prefs, sortBy);
      setResults(data);
      setResultCount(data.length);
      localStorage.setItem("recommendations", JSON.stringify(data));
      localStorage.setItem("user_preferences", JSON.stringify(prefs));
      setShowAdvanced(false);
    } catch (err) {
      if (err instanceof ApiError) setErrorType(err.type);
      else setErrorType("unknown_error");
    } finally {
      setLoading(false);
    }
  }

  // Re-sort when sort changes
  useEffect(() => {
    if (preferences && results.length > 0) {
      handleAdvancedSubmit(preferences);
    }
  }, [sortBy]);

  return (
    <div className="home-page">

      {/* HERO */}
      <div className="hero">
        <div className="hero-content">
          <h1 className="hero-title">
            Discover Kenya's<br />
            <span className="hero-accent">Best Events</span>
          </h1>
          <p className="hero-subtitle">
            Tell us what you're looking for — we'll find the perfect match.
          </p>
        </div>
      </div>

      {/* CHAT SECTION */}
      <div className="chat-section">
        <ChatBox
          onResults={handleChatResults}
          onLoading={setLoading}
        />

        {/* Advanced filters toggle */}
        <button
          className="advanced-toggle"
          onClick={() => setShowAdvanced((v) => !v)}
        >
          {showAdvanced ? "▲ Hide advanced filters" : "▼ Advanced filters"}
        </button>

        {showAdvanced && (
          <div className="advanced-panel">
            <PreferenceForm
              onSubmit={handleAdvancedSubmit}
              initialValues={preferences}
            />
          </div>
        )}
      </div>

      {/* RESULTS HEADER */}
      {(results.length > 0 || loading) && (
        <div className="results-header">
          <div className="results-meta">
            {resultCount !== null && !loading && (
              <span className="results-count">
                {resultCount} event{resultCount !== 1 ? "s" : ""} found
              </span>
            )}
            {locationWarning && (
              <span className="location-warning">⚠ {locationWarning}</span>
            )}
          </div>

          <div className="results-controls">
            <SortControl value={sortBy} onChange={setSortBy} />

            <div className="view-toggle">
              <button
                className={`view-btn ${viewMode === "list" ? "active" : ""}`}
                onClick={() => setViewMode("list")}
              >
                ☰ List
              </button>
              <button
                className={`view-btn ${viewMode === "map" ? "active" : ""}`}
                onClick={() => setViewMode("map")}
              >
                🗺 Map
              </button>
            </div>

            <button className="clear-btn" onClick={handleClear}>
              ✕ Clear
            </button>
          </div>
        </div>
      )}

      {/* ERROR */}
      {errorType && (() => {
        const info = errorMessageFor(errorType);
        return (
          <div className="error-banner" role="alert">
            <strong>{info.title}</strong>
            <p>{info.message}</p>
            <button
              onClick={() => preferences
                ? handleAdvancedSubmit(preferences)
                : setErrorType(null)
              }
            >
              Try Again
            </button>
          </div>
        );
      })()}

      {/* RESULTS */}
      <div className="results-section">
        {loading && (
          <div className="results-list">
            {[...Array(3)].map((_, i) => <SkeletonCard key={i} />)}
          </div>
        )}

        {!loading && results.length === 0 && resultCount !== null && (
          <div className="empty-state">
            <div className="empty-state-content">
              <div className="empty-state-icon">🎭</div>
              <h2>No events found</h2>
              <p className="empty-state-description">
                Try different keywords, a higher budget, or a different location.
              </p>
            </div>
          </div>
        )}

        {!loading && results.length > 0 && (
          <>
            {viewMode === "map" && <MapView recommendations={results} />}
            {viewMode === "list" && (
              <div className="results-list">
                {results.map((rec) => (
                  <RecommendationCard key={rec.event.id} recommendation={rec} />
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
