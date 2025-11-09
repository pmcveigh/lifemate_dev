import React, { useState } from "react";
import { useAuth } from "../auth/AuthContext.jsx";

const formStyle = {
  maxWidth: "320px",
  margin: "4rem auto",
  padding: "2rem",
  borderRadius: "0.75rem",
  background: "#ffffff",
  boxShadow: "0 10px 30px rgba(15, 23, 42, 0.08)",
  border: "1px solid #e5e7eb",
};

const inputStyle = {
  width: "100%",
  padding: "0.6rem 0.75rem",
  marginBottom: "1rem",
  borderRadius: "0.5rem",
  border: "1px solid #d1d5db",
  fontSize: "0.95rem",
};

const labelStyle = {
  display: "block",
  fontWeight: 600,
  marginBottom: "0.35rem",
  color: "#111827",
};

const buttonStyle = {
  width: "100%",
  padding: "0.65rem",
  borderRadius: "0.5rem",
  border: "none",
  background: "#2563eb",
  color: "#ffffff",
  fontWeight: 600,
  cursor: "pointer",
};

const errorStyle = {
  color: "#b91c1c",
  marginBottom: "1rem",
  fontSize: "0.9rem",
};

export default function Login() {
  const { login, loginLoading } = useAuth();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    try {
      await login(username.trim(), password);
      setPassword("");
    } catch (err) {
      setError(err.message || "Login failed");
    }
  }

  return (
    <div style={{ minHeight: "100vh", background: "#f9fafb", padding: "2rem" }}>
      <form onSubmit={handleSubmit} style={formStyle}>
        <h1 style={{ fontSize: "1.5rem", marginBottom: "1.5rem", textAlign: "center" }}>
          Sign in to Lifemate
        </h1>
        {error ? <div style={errorStyle}>{error}</div> : null}
        <label style={labelStyle} htmlFor="username">
          Username
        </label>
        <input
          id="username"
          name="username"
          type="text"
          autoComplete="username"
          style={inputStyle}
          value={username}
          onChange={(event) => setUsername(event.target.value)}
          disabled={loginLoading}
          required
        />
        <label style={labelStyle} htmlFor="password">
          Password
        </label>
        <input
          id="password"
          name="password"
          type="password"
          autoComplete="current-password"
          style={inputStyle}
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          disabled={loginLoading}
          required
        />
        <button type="submit" style={buttonStyle} disabled={loginLoading}>
          {loginLoading ? "Signing in…" : "Sign in"}
        </button>
      </form>
    </div>
  );
}
