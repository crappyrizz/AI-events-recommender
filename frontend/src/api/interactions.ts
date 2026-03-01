import { API_BASE_URL, authHeaders } from "./config";

export async function sendInteraction(
  eventId: string,
  interactionType: "INTERESTED" | "NOT_INTERESTED"
) {
  const resp = await fetch(`${API_BASE_URL}/interactions/`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({
      event_id: eventId,
      interaction_type: interactionType,
    }),
  });

  if (!resp.ok) {
    throw new Error("interaction_failed");
  }

  return resp.json();
}