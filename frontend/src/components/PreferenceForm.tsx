import { useState } from "react";
import type { UserPreferences } from "../types/recommendation";

interface PreferenceFormProps {
  onSubmit: (preferences: UserPreferences) => void;
}

export default function PreferenceForm({ onSubmit }: PreferenceFormProps) {
  const [budget, setBudget] = useState("");
  const [genres, setGenres] = useState("");
  const [latitude, setLatitude] = useState("");
  const [longitude, setLongitude] = useState("");
  const [foodPreference, setFoodPreference] = useState("");
  const [avoidCrowds, setAvoidCrowds] = useState(false);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();

    const preferences: UserPreferences = {
      budget: Number(budget),
      preferred_genres: genres
        .split(",")
        .map((g) => g.trim())
        .filter(Boolean),
      latitude: Number(latitude),
      longitude: Number(longitude),
      food_preference: foodPreference,
      avoid_crowds: avoidCrowds,
    };

    onSubmit(preferences);
  }

  return (
    <form onSubmit={handleSubmit} style={{ marginBottom: "2rem" }}>
      <div>
        <input
          type="number"
          placeholder="Budget"
          value={budget}
          onChange={(e) => setBudget(e.target.value)}
          required
        />
      </div>

      <div>
        <input
          type="text"
          placeholder="Preferred genres (comma separated)"
          value={genres}
          onChange={(e) => setGenres(e.target.value)}
          required
        />
      </div>

      <div>
        <input
          type="number"
          placeholder="Latitude"
          value={latitude}
          onChange={(e) => setLatitude(e.target.value)}
          step="any"
          required
        />
      </div>

      <div>
        <input
          type="number"
          placeholder="Longitude"
          value={longitude}
          onChange={(e) => setLongitude(e.target.value)}
          step="any"
          required
        />
      </div>

      <div>
        <input
          type="text"
          placeholder="Food preference"
          value={foodPreference}
          onChange={(e) => setFoodPreference(e.target.value)}
        />
      </div>

      <label>
        <input
          type="checkbox"
          checked={avoidCrowds}
          onChange={(e) => setAvoidCrowds(e.target.checked)}
        />
        Avoid crowds
      </label>

      <div>
        <button type="submit">Get recommendations</button>
      </div>
    </form>
  );
}
