const BASE = (import.meta as any).env?.VITE_API_BASE_URL ?? "";

export async function sendInteraction(
  userId: number,
  eventId: number,
  interactionType: "INTERESTED" | "NOT_INTERESTED"
) {
  const resp = await fetch(`${BASE}/interactions/`, {
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
