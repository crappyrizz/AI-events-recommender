// import { useState } from "react";
// import { sendChat } from "../api/chat";

// interface Event {
//   id: string;
//   name: string;
//   date: string;
//   genre: string;
// }

// export default function ChatBox() {
//   const [message, setMessage] = useState("");
//   const [results, setResults] = useState<Event[]>([]);
//   const [loading, setLoading] = useState(false);

//   async function handleSend() {
//     if (!message) return;

//     setLoading(true);

//     try {
//       const data = await sendChat(message);
//       setResults(data);
//     } catch (err) {
//       console.error("Chat failed", err);
//     } finally {
//       setLoading(false);
//     }
//   }

//   return (
//     <div style={{ marginTop: 20 }}>
//       <h3>Ask about events</h3>

//       <div style={{ display: "flex", gap: 8 }}>
//         <input
//           value={message}
//           onChange={(e) => setMessage(e.target.value)}
//           placeholder="e.g. free tech events in Nairobi"
//           style={{ flex: 1, padding: 8 }}
//         />
//         <button onClick={handleSend}>Send</button>
//       </div>

//       {loading && <p>Searching events...</p>}

//       <div style={{ marginTop: 10 }}>
//         {results.map((event) => (
//           <div
//             key={event.id}
//             style={{
//               border: "1px solid #e5e7eb",
//               padding: 10,
//               borderRadius: 8,
//               marginBottom: 6,
//             }}
//           >
//             <strong>{event.name}</strong>
//             <div style={{ fontSize: 14 }}>
//               {event.date} • {event.genre}
//             </div>
//           </div>
//         ))}
//       </div>
//     </div>
//   );
// }