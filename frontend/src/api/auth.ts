// const BASE = "http://127.0.0.1:8000/api/v1";

import { API_BASE_URL } from "./config";

export async function login(email: string, password: string) {
  const resp = await fetch(`${API_BASE_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  if (!resp.ok) {
    throw new Error("Login failed");
  }

  return resp.json();
}

export async function register(email: string, password: string) {
  const res = await fetch(`${API_BASE_URL}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  if (!res.ok) throw new Error("Register failed");

  return res.json();
}