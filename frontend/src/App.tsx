import { Routes, Route, Link } from "react-router-dom";
import HomePage from "./pages/HomePage";
import SavedPage from "./pages/SavedPage";

export default function App() {
  return (
    <div>
      <nav
        style={{
          padding: 16,
          borderBottom: "1px solid #e5e7eb",
          display: "flex",
          gap: 16,
        }}
      >
        <Link to="/">Home</Link>
        <Link to="/saved">Saved</Link>
      </nav>

      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/saved" element={<SavedPage />} />
      </Routes>
    </div>
  );
}
