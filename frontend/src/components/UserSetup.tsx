// import { useState } from "react";
// import { useUser } from "../context/UserContext";

// export default function UserSetup() {
//   const { userId, setUserEmail } = useUser();
//   const [email, setEmail] = useState("");

//   if (userId) return null;

//   return (
//     <div
//       style={{
//         background: "#f3f4f6",
//         padding: 16,
//         marginBottom: 16,
//         borderRadius: 8,
//       }}
//     >
//       <strong>Enter your email to personalize your experience</strong>

//       <div style={{ marginTop: 8 }}>
//         <input
//           type="email"
//           placeholder="you@example.com"
//           value={email}
//           onChange={(e) => setEmail(e.target.value)}
//           style={{ padding: 6, marginRight: 8 }}
//         />

//         <button
//           onClick={() => setUserEmail(email)}
//           style={{
//             padding: "6px 12px",
//             background: "#2563EB",
//             color: "white",
//             border: "none",
//             borderRadius: 6,
//           }}
//         >
//           Continue
//         </button>
//       </div>
//     </div>
//   );
// }