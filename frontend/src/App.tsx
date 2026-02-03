import { useState } from "react";
import PreferenceForm from "./components/PreferenceForm";
import { getRecommendations } from "./api/recommendations";
import type { Recommendation, UserPreferences } from "./types/recommendation";

function App() {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(preferences: UserPreferences) {
    try {
      setLoading(true);
      setError(null);
      const data = await getRecommendations(preferences);
      setRecommendations(data);
    } catch (err: any) {
      setError(err.message || "Failed to load recommendations");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ padding: "2rem" }}>
      <h1>AI Events Recommender</h1>
      <p>Personalized event recommendations</p>

      <PreferenceForm onSubmit={handleSubmit} />

      {loading && <p>Loading recommendations…</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}

      {recommendations.length > 0 && (
        <pre style={{ marginTop: "2rem" }}>
          {JSON.stringify(recommendations, null, 2)}
        </pre>
      )}
    </div>
  );
}

export default App;
