import { Navigate } from "react-router-dom";
import type { JSX } from "react/jsx-runtime";

export default function RequireAuth({ children }: { children: JSX.Element }) {
  const token = localStorage.getItem("token");

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  return children;
}