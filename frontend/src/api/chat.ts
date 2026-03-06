import { API_BASE_URL } from "./config";
import type { ChatResponse } from "../types/recommendation";
import { ApiError } from "./recommendations";


export async function sendChat(
  message: string,
  latitude?: number | null,
  longitude?: number | null
): Promise<ChatResponse> {

  if (typeof navigator !== "undefined" && !navigator.onLine) {
    throw new ApiError("network_error", "Offline");
  }

  let resp: Response;
  try {
    resp = await fetch(`${API_BASE_URL}/chat/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message,
        latitude:  latitude  ?? null,
        longitude: longitude ?? null,
      }),
    });
  } catch (err) {
    throw new ApiError("network_error", (err as Error)?.message ?? "Network error");
  }

  if (!resp.ok) {
    if (resp.status >= 500) throw new ApiError("server_error", "Server error", resp.status);
    throw new ApiError("unknown_error", `HTTP ${resp.status}`, resp.status);
  }

  return resp.json() as Promise<ChatResponse>;
}