import type { UserPreferences, Recommendation, RecommendationsResponse } from "../types/recommendation";
import type { ErrorType } from "../utils/errorMessages";
import { API_BASE_URL } from "./config";


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


export async function getRecommendations(
  preferences: UserPreferences,
  sortBy?: string
): Promise<Recommendation[]> {
  const query = sortBy ? `?sort_by=${sortBy}` : "";
  const url = `${API_BASE_URL}/recommendations/${query}`;

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
    throw new ApiError("network_error", (err as Error)?.message ?? "Network error");
  }

  if (!resp.ok) {
    if (resp.status === 400) throw new ApiError("validation_error", "Invalid request", 400);
    if (resp.status >= 500) throw new ApiError("server_error", "Server error", resp.status);
    throw new ApiError("unknown_error", `HTTP ${resp.status}`, resp.status);
  }

  // Backend returns { results: [...], message?: string }
  const data = (await resp.json()) as RecommendationsResponse;
  return data.results ?? [];
}