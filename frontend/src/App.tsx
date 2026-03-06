import { Routes, Route, Link, useLocation, useNavigate } from "react-router-dom";
import HomePage from "./pages/HomePage";
import SavedPage from "./pages/SavedPage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import RequireAuth from "./components/RequireAuth";

function Navbar() {
  const location = useLocation();
  const navigate = useNavigate();
  const token = localStorage.getItem("token");
  const isAuth = Boolean(token);

  function handleLogout() {
    localStorage.removeItem("token");
    localStorage.removeItem("user_id");
    localStorage.removeItem("recommendations");
    localStorage.removeItem("user_preferences");
    navigate("/login");
  }

  // Don't show navbar on auth pages
  if (["/login", "/register"].includes(location.pathname)) return null;

  return (
    <nav className="navbar">
      <Link to="/" className="navbar-brand">
        Tafuta<span>Events</span>
      </Link>

      <div className="navbar-links">
        {isAuth && (
          <>
            <Link
              to="/"
              className={`nav-link ${location.pathname === "/" ? "active" : ""}`}
            >
              Discover
            </Link>
            <Link
              to="/saved"
              className={`nav-link ${location.pathname === "/saved" ? "active" : ""}`}
            >
              Saved
            </Link>
            <button className="nav-logout" onClick={handleLogout}>
              Logout
            </button>
          </>
        )}

        {!isAuth && (
          <>
            <Link to="/login" className="nav-link">Login</Link>
            <Link to="/register" className="nav-link">Register</Link>
          </>
        )}
      </div>
    </nav>
  );
}

export default function App() {
  return (
    <div>
      <Navbar />
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
