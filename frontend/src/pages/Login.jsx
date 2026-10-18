import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import GoogleSignInButton from "../components/GoogleSignInButton";
import {
  GraduationCap,
  Building2,
  Lock,
  Mail,
  ShieldCheck,
  ArrowRight,
} from "lucide-react";

export default function Login() {
  const { loginWithCredentials } = useAuth();
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [tab, setTab] = useState("credentials"); // 'credentials' | 'google'

  function handleLogin(e) {
    e.preventDefault();
    setError("");

    if (!email.trim() || !password.trim()) {
      setError("Please enter both your Faculty Email and Password.");
      return;
    }

    const result = loginWithCredentials(email, password);
    if (!result.success) {
      setError(result.error || "Invalid ID or Password. Access denied.");
      return;
    }

    // Success! Redirect to Portal
    navigate("/", { replace: true });
  }

  return (
    <div className="login-container">
      <div className="login-card panel">
        <div className="login-header">
          <div className="login-badge-icon">
            <GraduationCap size={32} />
          </div>
          <h2>Faculty Portal Authentication</h2>
          <p className="lede">
            Dharmsinh Desai University · Department of Information Technology
          </p>
          <p className="text-xs muted" style={{ marginTop: "4px" }}>
            Faculty Leave Arrangement & Smart Notification System
          </p>
        </div>

        <div className="login-tabs">
          <button
            type="button"
            className={`tab-btn ${tab === "credentials" ? "active" : ""}`}
            onClick={() => setTab("credentials")}
          >
            Faculty Credentials Login
          </button>
          <button
            type="button"
            className={`tab-btn ${tab === "google" ? "active" : ""}`}
            onClick={() => setTab("google")}
          >
            Google Workspace Login
          </button>
        </div>

        {tab === "credentials" && (
          <div className="login-tab-content">
            <form onSubmit={handleLogin} className="credentials-form">
              {error && (
                <div className="alert-box error" style={{ padding: "0.65rem 0.85rem", fontSize: "0.84rem" }}>
                  <span>{error}</span>
                </div>
              )}

              <div>
                <label htmlFor="facultyEmail">
                  <Mail size={14} style={{ display: "inline", marginRight: "5px" }} />
                  Faculty Institutional Email (ID)
                </label>
                <input
                  id="facultyEmail"
                  type="email"
                  placeholder="e.g. harshad.prajapati@ddu.ac.in"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  autoComplete="username"
                  required
                />
              </div>

              <div>
                <label htmlFor="facultyPassword">
                  <Lock size={14} style={{ display: "inline", marginRight: "5px" }} />
                  Password
                </label>
                <input
                  id="facultyPassword"
                  type="password"
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  autoComplete="current-password"
                  required
                />
              </div>

              <button
                type="submit"
                className="button primary full-width lg"
                style={{ marginTop: "0.4rem" }}
              >
                Sign In to Faculty Desk <ArrowRight size={16} />
              </button>
            </form>
          </div>
        )}

        {tab === "google" && (
          <div className="login-tab-content">
            <p className="login-tab-description">
              Sign in with your verified university Google account (e.g. <code>@ddu.ac.in</code>) to
              authenticate your faculty session.
            </p>
            <div className="google-login-center">
              <GoogleSignInButton onAuthSuccess={() => navigate("/")} />
            </div>
            <div className="security-notice">
              <ShieldCheck size={16} />
              <span>Institutional Single Sign-On (SSO)</span>
            </div>
          </div>
        )}

        <div className="login-footer">
          <Building2 size={15} />
          <span>Faculty of Technology · Dharmsinh Desai University, Nadiad</span>
        </div>
      </div>
    </div>
  );
}
