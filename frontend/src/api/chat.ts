// import { API_BASE_URL } from "./config";

// export async function sendChat(message: string) {
//   const resp = await fetch(`${API_BASE_URL}/chat`, {
//     method: "POST",
//     headers: { "Content-Type": "application/json" },
//     body: JSON.stringify({ message }),
//   });

//   if (!resp.ok) {
//     throw new Error("chat_failed");
//   }

//   return resp.json();
// }