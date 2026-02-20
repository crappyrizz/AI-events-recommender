import { API_BASE_URL } from "./config";

export const saveEvent = async (
  userId: number,
  eventId: string,
  eventName: string,
  eventDate: string,
  eventGenre: string
) => {
  const resp = await fetch(`${API_BASE_URL}/saved-events/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      user_id: userId,
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


export const unsaveEvent = async (
  userId: number,
  eventId: string
) => {
  const resp = await fetch(
    `${API_BASE_URL}/saved-events/${userId}/${eventId}`,
    { method: "DELETE" }
  );

  if (!resp.ok) {
    throw new Error("unsave_failed");
  }

  return resp.json();
};



export const getSavedEvents = async (userId: number) => {
  const resp = await fetch(
    `${API_BASE_URL}/saved-events/${userId}`
  );

  if (!resp.ok) {
    throw new Error("fetch_saved_failed");
  }

  return resp.json();
};