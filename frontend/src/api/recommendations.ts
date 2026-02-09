import type { UserPreferences, Recommendation } from "../types/recommendation";
import type { ErrorType } from "../utils/errorMessages";

export class ApiError extends Error {
  public type: ErrorType;
  public status?: number;
  constructor(type: ErrorType, message?: string, status?: number) {
    super(message ?? type);
    this.type = type;
    this.status = status;
    Object.setPrototypeOf(this, ApiError.prototype);
  }
}

const BASE_URL = "http://127.0.0.1:8000";

export async function getRecommendations(
  preferences: UserPreferences,
  sortBy?: string
): Promise<Recommendation[]> {
  const query = sortBy ? `?sort_by=${sortBy}` : "";
  const url = `${BASE_URL}/recommendations/${query}`;

  if (preferences.max_distance_km) {
    `&max_distance_km=${preferences.max_distance_km}`;
  }

  if (typeof navigator !== "undefined" && !navigator.onLine) {
    throw new ApiError("network_error", "Offline");
  }

  let resp: Response;
  try {
    resp = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: 1, preferences }),
    });
  } catch (err) {
    // Network-level failures
    throw new ApiError("network_error", (err as Error)?.message ?? "Network error");
  }

  if (!resp.ok) {
    if (resp.status === 400) {
      throw new ApiError("validation_error", "Invalid request", 400);
    }

    if (resp.status >= 500) {
      throw new ApiError("server_error", "Server error", resp.status);
    }

    throw new ApiError("unknown_error", `HTTP ${resp.status}`, resp.status);
  }

  const data = (await resp.json()) as Recommendation[];
  return data;
}
