import { API_BASE_URL, authHeaders } from "./config";


export const saveEvent = async (
  eventId: string,
  eventName: string,
  eventDate: string,
  eventGenre: string
) => {
  const resp = await fetch(`${API_BASE_URL}/saved-events/`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({
      event_id: eventId,
      event_name: eventName,
      event_date: eventDate,
      event_genre: eventGenre,
    }),
  });

  if (!resp.ok) {
    throw new Error("save_failed");
  }

  return resp.json();
};

export const unsaveEvent = async (eventId: string) => {
  const resp = await fetch(
    `${API_BASE_URL}/saved-events/${eventId}`,
    {
      method: "DELETE",
      headers: authHeaders(),
    }
  );

  if (!resp.ok) {
    throw new Error("unsave_failed");
  }

  return resp.json();
};

export const getSavedEvents = async () => {
  const resp = await fetch(`${API_BASE_URL}/saved-events/`, {
    headers: authHeaders(),
  });

  if (!resp.ok) {
    throw new Error("fetch_saved_failed");
  }

  return resp.json();
};