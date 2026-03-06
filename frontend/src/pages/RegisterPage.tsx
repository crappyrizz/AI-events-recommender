import { useState, useEffect } from "react";
import { register } from "../api/auth";
import { useNavigate, Link } from "react-router-dom";

export default function RegisterPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    if (localStorage.getItem("token")) navigate("/");
  }, []);

  async function handleRegister() {
    if (!email || !password) {
      setError("Please fill in all fields.");
      return;
    }
    if (password !== confirm) {
      setError("Passwords do not match.");
      return;
    }
    if (password.length < 6) {
      setError("Password must be at least 6 characters.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const data = await register(email, password);
      localStorage.setItem("token", data.access_token);
      localStorage.setItem("user_id", data.user_id);
      navigate("/");
    } catch {
      setError("Registration failed. This email may already be in use.");
    } finally {
      setLoading(false);
    }
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === "Enter") handleRegister();
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-logo">Tafuta<span>Events</span></div>
        <p className="auth-tagline">Discover the best events across Kenya</p>

        <h2>Create account</h2>

        <div className="auth-form">
          {error && <div className="auth-error">{error}</div>}

          <input
            className="auth-input"
            type="email"
            placeholder="Email address"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            onKeyDown={handleKeyDown}
            autoFocus
          />

          <input
            className="auth-input"
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            onKeyDown={handleKeyDown}
          />

          <input
            className="auth-input"
            type="password"
            placeholder="Confirm password"
            value={confirm}
            onChange={(e) => setConfirm(e.target.value)}
            onKeyDown={handleKeyDown}
          />

          <button
            className="auth-btn"
            onClick={handleRegister}
            disabled={loading}
          >
            {loading ? "Creating account..." : "Create Account"}
          </button>
        </div>

        <p className="auth-switch">
          Already have an account?{" "}
          <Link to="/login">Sign in</Link>
        </p>
      </div>
    </div>
  );
}
