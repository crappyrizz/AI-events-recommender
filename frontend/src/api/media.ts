import { API_BASE_URL } from "./config";

export const uploadMedia = async (eventId: string, file: File) => {
  const formData = new FormData();
  formData.append("file", file);

  const token = localStorage.getItem("token");

  const resp = await fetch(`${API_BASE_URL}/media/${eventId}`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`, // ONLY this header
    },
    body: formData,
  });

  if (!resp.ok) throw new Error("upload_failed");
  return resp.json();
};

export const getEventMedia = async (eventId: string) => {
  const token = localStorage.getItem("token");

  const resp = await fetch(`${API_BASE_URL}/media/${eventId}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!resp.ok) throw new Error("media_fetch_failed");
  return resp.json();
};