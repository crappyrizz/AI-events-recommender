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
    };

    onSubmit(preferences);
  }

  return (
    <form onSubmit={handleSubmit} className="pref-form">

      <div>
        <input
          type="number"
          placeholder="Budget (KES)"
          value={budget}
          onChange={(e) => setBudget(e.target.value)}
          required
          className="pref-input"
        />
      </div>

      <div>
        <input
          type="text"
          placeholder="Genres e.g. Music, Tech, Food"
          value={genres}
          onChange={(e) => setGenres(e.target.value)}
          required
          className="pref-input"
        />
      </div>

      <div style={{ gridColumn: "span 2" }}>
        <button
          type="button"
          onClick={detectLocation}
          disabled={locating}
          className="pref-loc-btn"
        >
          {locating ? "⏳ Detecting location..." : "📍 Use my current location"}
        </button>

        {locationError && (
          <div className="auth-error" style={{ marginTop: 8 }}>
            {locationError}
          </div>
        )}
      </div>

      <div>
        <input
          type="text"
          placeholder="Food preference"
          value={foodPreference}
          onChange={(e) => setFoodPreference(e.target.value)}
          className="pref-input"
        />
      </div>

      <label style={{ display: "flex", alignItems: "center", gap: "0.5rem", fontSize: "0.95rem", color: "var(--urban)" }}>
        <input
          type="checkbox"
          checked={avoidCrowds}
          onChange={(e) => setAvoidCrowds(e.target.checked)}
        />
        Avoid crowds
      </label>

      {latitude === null && (
        <div className="auth-error" style={{ gridColumn: "span 2" }}>
          Please detect your location before submitting.
        </div>
      )}

      <div style={{ gridColumn: "span 2" }}>
        <button
          type="submit"
          disabled={latitude === null}
          className="pref-btn"
          style={{ width: "100%" }}
        >
          Get Recommendations
        </button>
      </div>

    </form>
  );
}
