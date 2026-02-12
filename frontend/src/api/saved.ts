const BASE = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

export async function getSavedEvents(): Promise<string[]> {
  const res = await fetch(`${BASE}/saved/`);
  if (!res.ok) throw new Error("Failed to load saved events");
  return res.json();
}

export async function removeSaved(eventId: string) {
  await fetch(`${BASE}/saved/${eventId}`, {
    method: "DELETE",
  });
}
