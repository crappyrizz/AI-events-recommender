import { Routes, Route, Link } from "react-router-dom";
import HomePage from "./pages/HomePage";
import SavedPage from "./pages/SavedPage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import RequireAuth from "./components/RequireAuth";


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
        <Link to="/login">Login</Link>
        <Link to="/register">Register</Link>
      </nav>

      

          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />

            <Route
              path="/"
              element={
                <RequireAuth>
                <HomePage />
                </RequireAuth>
              }
            />

            <Route
              path="/saved"
              element={
                <RequireAuth>
                  <SavedPage />
                </RequireAuth>
              }
            />
            </Routes>


    </div>
  );
}
