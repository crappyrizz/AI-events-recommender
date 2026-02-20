import { API_BASE_URL } from "./config";

export async function sendInteraction(
  userId: number,
  eventId: string,
  interactionType: "INTERESTED" | "NOT_INTERESTED"
) {
  const resp = await fetch(`${API_BASE_URL}/interactions/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      user_id: userId,
      event_id: eventId,
      interaction_type: interactionType,
    }),
  });

  if (!resp.ok) {
    throw new Error("interaction_failed");
  }

  return resp.json();
}
