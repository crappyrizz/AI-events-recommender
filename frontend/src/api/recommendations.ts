import type { UserPreferences, Recommendation } from "../types/recommendation";

const BASE_URL = "http://127.0.0.1:8000";

export async function getRecommendations(
  preferences: UserPreferences
): Promise<Recommendation[]> {
  const response = await fetch(`${BASE_URL}/recommendations/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ preferences }),
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(
      `Failed to fetch recommendations: ${response.status} ${text}`
    );
  }

  return response.json();
}
