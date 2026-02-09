import { useState } from "react";
import type { UserPreferences } from "../types/recommendation";

interface PreferenceFormProps {
  onSubmit: (preferences: UserPreferences ) => void;
}

export default function PreferenceForm({ onSubmit }: PreferenceFormProps) {
  const [budget, setBudget] = useState("");
  const [genres, setGenres] = useState("");
  const [latitude, setLatitude] = useState("");
  const [longitude, setLongitude] = useState("");
  const [foodPreference, setFoodPreference] = useState("");
  const [avoidCrowds, setAvoidCrowds] = useState(false);
  const [maxDistanceKm, setMaxDistanceKm] = useState("");


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
      max_distance_km: maxDistanceKm ? parseFloat(maxDistanceKm) : undefined,
    };

    onSubmit(preferences);
  }

  return (
    <form onSubmit={handleSubmit} style={{ marginBottom: "2rem", display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "1rem" }}>
      <div style={{ gridColumn: "span 1" }}>
        <input
          type="number"
          placeholder="Budget"
          value={budget}
          onChange={(e) => setBudget(e.target.value)}
          required
          style={{ width: "100%" }}
        />
      </div>

      <div style={{ gridColumn: "span 1" }}>
        <input
          type="text"
          placeholder="Preferred genres (comma separated)"
          value={genres}
          onChange={(e) => setGenres(e.target.value)}
          required
          style={{ width: "100%" }}
        />
      </div>

      <div style={{ gridColumn: "span 1" }}>
        <input
          type="number"
          placeholder="Latitude"
          value={latitude}
          onChange={(e) => setLatitude(e.target.value)}
          step="any"
          required
          style={{ width: "100%" }}
        />
      </div>

      <div style={{ gridColumn: "span 1" }}>
        <input
          type="number"
          placeholder="Longitude"
          value={longitude}
          onChange={(e) => setLongitude(e.target.value)}
          step="any"
          required
          style={{ width: "100%" }}
        />
      </div>

      <div style={{ gridColumn: "span 1" }}>
        <input
          type="text"
          placeholder="Food preference"
          value={foodPreference}
          onChange={(e) => setFoodPreference(e.target.value)}
          style={{ width: "100%" }}
        />
      </div>

      <div style={{ marginTop: 12 }}>
        <label>Distance</label>
        <select
          value={maxDistanceKm}
          onChange={(e) => setMaxDistanceKm(e.target.value)}
          style={{ display: "block", marginTop: 4 }}
        >
          <option value="">Any distance</option>
          <option value="5">Within 5 km</option>
          <option value="20">Within 20 km</option>
          <option value="50">Within 50 km</option>
        </select>
      </div>


      <label style={{ gridColumn: "span 1", display: "flex", alignItems: "center", gap: "0.5rem" }}>
        <input
          type="checkbox"
          checked={avoidCrowds}
          onChange={(e) => setAvoidCrowds(e.target.checked)}
        />
        Avoid crowds
      </label>

      <div style={{ gridColumn: "span 1" }}>
        <button type="submit" style={{ width: "100%" }}>Get recommendations</button>
      </div>
    </form>
  );
}
