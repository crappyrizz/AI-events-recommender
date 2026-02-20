import { useState } from "react";
import type { UserPreferences } from "../types/recommendation";
import { useEffect } from "react";

interface PreferenceFormProps {
  onSubmit: (preferences: UserPreferences ) => void;
  initialValues?: UserPreferences | null;
}

export default function PreferenceForm({ onSubmit, initialValues }: PreferenceFormProps) {
  const [budget, setBudget] = useState(initialValues?.budget ?? "");
  const [genres, setGenres] = useState(initialValues?.preferred_genres?.join(", ") ?? "");
  const [latitude, setLatitude] = useState<number | null>(initialValues?.latitude ?? null);
  const [longitude, setLongitude] = useState<number | null>(initialValues?.longitude ?? null);
  const [foodPreference, setFoodPreference] = useState(initialValues?.food_preference ?? "");
  const [avoidCrowds, setAvoidCrowds] = useState(initialValues?.avoid_crowds ?? false);
  // UI state (these should NOT be restored)
  const [locating, setLocating] = useState(false);
  const [locationError, setLocationError] = useState<string | null>(null);

  useEffect(() => {
  if (!initialValues) {
    setBudget("");
    setGenres("");
    setLatitude(null);
    setLongitude(null);
    setFoodPreference("");
    setAvoidCrowds(false);
    return;
  }

  setBudget(initialValues.budget?.toString() ?? "");
  setGenres(initialValues.preferred_genres?.join(", ") ?? "");
  setLatitude(initialValues.latitude ?? null);
  setLongitude(initialValues.longitude ?? null);
  setFoodPreference(initialValues.food_preference ?? "");
  setAvoidCrowds(initialValues.avoid_crowds ?? false);
  }, [initialValues]);


  function detectLocation() {
    if (!navigator.geolocation) {
      setLocationError("Geolocation is not supported by your browser");
      return;
    }

    setLocating(true);
    setLocationError(null);

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setLatitude(position.coords.latitude);
        setLongitude(position.coords.longitude);
        setLocating(false);
      },
      (error) => {
        setLocationError(error.message || "Unable to retrieve your location");
        setLocating(false);
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
      }
    );
  }



  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();

    const preferences: UserPreferences = {
      budget: Number(budget),
      preferred_genres: genres
        .split(",")
        .map((g) => g.trim())
        .filter(Boolean),
      latitude: latitude ?? 0,
      longitude: longitude ?? 0,
      food_preference: foodPreference,
      avoid_crowds: avoidCrowds,
      // max_distance_km: maxDistanceKm ? parseFloat(maxDistanceKm) : undefined,
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


      <div style={{ gridColumn: "span 2" }}>
        <button
          type="button"
          onClick={detectLocation}
          disabled={locating}
          style={{
            padding: "8px 12px",
            background: "#2563EB",
            color: "white",
            border: "none",
            borderRadius: 6,
            cursor: "pointer",
            width: "100%",
          }}
        >
          {locating ? "Detecting location..." : "📍 Use my current location"}
        </button>

        {locationError && (
          <div style={{ color: "red", marginTop: 6 }}>
            {locationError}
          </div>
        )}
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




      <label style={{ gridColumn: "span 1", display: "flex", alignItems: "center", gap: "0.5rem" }}>
        <input
          type="checkbox"
          checked={avoidCrowds}
          onChange={(e) => setAvoidCrowds(e.target.checked)}
        />
        Avoid crowds
      </label>

      {latitude === null && (
        <div style={{ color: "#ef4444", fontSize: 14 }}>
          Please use your location before getting recommendations.
        </div>
      )}


      <div style={{ gridColumn: "span 1" }}>
        <button type="submit" disabled={latitude === null} style={{ width: "100%" }}>Get recommendations</button>
      </div>
    </form>
  );
}
