import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import { useAuth } from "../context/AuthContext";
import {
  UploadCloud,
  FileText,
  CheckCircle,
  AlertTriangle,
  Clock,
  Bell,
  ArrowRight,
  Sparkles,
  Calendar,
  Layers,
  Trash2,
} from "lucide-react";

export default function Dashboard() {
  const { faculty, incomingCount } = useAuth();
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    loadDashboard();
  }, [faculty?.email]);

  function loadDashboard() {
    api
      .dashboard({
        applicant_name: faculty?.name,
        faculty_email: faculty?.email,
      })
      .then(setData)
      .catch((err) => setError(err.message));
  }

  async function handleDeleteForm(id, filename) {
    if (
      !window.confirm(
        `Are you sure you want to delete form "${filename || id}"? All scanned rows and notifications will be permanently removed.`
      )
    ) {
      return;
    }
    try {
      await api.deleteForm(id);
      setData((prev) => {
        if (!prev) return prev;
        return {
          ...prev,
          form_count: Math.max(0, prev.form_count - 1),
          recent: (prev.recent || []).filter((f) => f.id !== id),
        };
      });
    } catch (err) {
      alert(`Failed to delete form: ${err.message}`);
    }
  }

  if (error) {
    return (
      <div className="page-container">
        <div className="alert-box error" style={{ margin: "2rem 0", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <div>
            <strong>Backend Connection Notice:</strong> {error}
            <div className="text-xs muted" style={{ marginTop: "0.25rem" }}>
              Ensure the FastAPI backend server is active on http://127.0.0.1:8000.
            </div>
          </div>
          <button type="button" className="btn btn-secondary btn-sm" onClick={() => { setError(""); loadDashboard(); }}>
            Retry Connection
          </button>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="page-container">
        <div className="loading-state" style={{ padding: "3rem", textAlign: "center" }}>
          <p className="muted">Loading faculty portal metrics…</p>
        </div>
      </div>
    );
  }


  const counts = data.status_counts || {};

  return (
    <div className="page-container">
      {faculty && (
        <div className="dashboard-welcome-banner panel">
          <div className="welcome-avatar-wrap">
            <img
              src={
                faculty.avatar ||
                `https://ui-avatars.com/api/?name=${encodeURIComponent(faculty.name)}&background=0284c7&color=fff`
              }
              alt={faculty.name}
              className="welcome-avatar"
            />
          </div>
          <div className="welcome-text-col">
            <h2>Welcome, {faculty.name}</h2>
            <p className="welcome-subtext">
              {faculty.designation} · {faculty.department || "Information Technology"} ·{" "}
              {faculty.email}
            </p>
          </div>

          <div className="welcome-actions">
            <Link to="/upload" className="button primary sm">
              <UploadCloud size={16} /> File New Leave Form
            </Link>
            <Link to="/notifications" className="button secondary sm incoming-sub-btn">
              <Bell size={16} />
              <span>Incoming Substitutions</span>
              <span className="incoming-count-badge">{incomingCount}</span>
            </Link>
          </div>
        </div>
      )}

      <div className="cards-metrics-grid">
        <article className="card metric-card">
          <div className="metric-header">
            <span className="metric-label">Total Leave Forms</span>
            <FileText size={18} className="metric-icon" />
          </div>
          <div className="stat">{data.form_count}</div>
          <span className="metric-footnote">Scanned arrangements</span>
        </article>

        <article className="card metric-card">
          <div className="metric-header">
            <span className="metric-label">Needs Review</span>
            <AlertTriangle size={18} className="metric-icon warn" />
          </div>
          <div className="stat">{counts.NEEDS_REVIEW || 0}</div>
          <span className="metric-footnote">Awaiting human sign-off</span>
        </article>

        <article className="card metric-card">
          <div className="metric-header">
            <span className="metric-label">Substitutes Notified</span>
            <CheckCircle size={18} className="metric-icon ok" />
          </div>
          <div className="stat">{(counts.NOTIFIED || 0) + (counts.CONFIRMED || 0)}</div>
          <span className="metric-footnote">Dispatched to faculty</span>
        </article>

        <article className="card metric-card">
          <div className="metric-header">
            <span className="metric-label">Active Semesters</span>
            <Calendar size={18} className="metric-icon" />
          </div>
          <div className="stat" style={{ fontSize: "1.4rem" }}>
            Sem {data.active_semesters?.join(", ") || "1, 3, 5, 7"}
          </div>
          <span className="metric-footnote">ODD Term 2026</span>
        </article>
      </div>

      <div className="quick-actions-row">
        <Link className="quick-action-tile" to="/upload">
          <UploadCloud size={22} className="tile-icon" />
          <div>
            <h4 className="tile-title">Upload Leave Form</h4>
            <p className="tile-desc">Scan handwritten table with TrOCR AI model</p>
          </div>
          <ArrowRight size={16} className="tile-arrow" />
        </Link>

        <Link className="quick-action-tile" to="/review">
          <CheckCircle size={22} className="tile-icon ok" />
          <div>
            <h4 className="tile-title">Scan Results & Notifications</h4>
            <p className="tile-desc">Inspect lecture slots & notify resultant faculty</p>
          </div>
          <ArrowRight size={16} className="tile-arrow" />
        </Link>

        <Link className="quick-action-tile" to="/notifications">
          <Bell size={22} className="tile-icon warn" />
          <div>
            <h4 className="tile-title">Faculty Notification Center</h4>
            <p className="tile-desc">Check substitute assignments & confirmations</p>
          </div>
          <ArrowRight size={16} className="tile-arrow" />
        </Link>
      </div>

      <div className="panel recent-forms-card">
        <div className="table-card-header">
          <h3>Recent Leave Forms & Submissions</h3>
          <span className="badge text-xs">
            {data.demo_mode ? "Fast Demo Active" : "Live TrOCR Engine"}
          </span>
        </div>

        <table className="recent-forms-table">
          <thead>
            <tr>
              <th>Applicant Faculty</th>
              <th>Form Image File</th>
              <th>Status</th>
              <th>Submitted</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {(data.recent || []).map((form) => (
              <tr key={form.id}>
                <td>
                  <strong>{form.applicant_name}</strong>
                  <div className="text-xs muted">{form.year} Academic Year</div>
                </td>
                <td>{form.original_filename}</td>
                <td>
                  <span
                    className={`badge ${
                      form.status === "CONFIRMED" || form.status === "NOTIFIED"
                        ? "ok"
                        : form.status === "REVIEWED"
                        ? "info"
                        : form.status === "NEEDS_REVIEW"
                        ? "warn"
                        : "default"
                    }`}
                  >
                    {form.status}
                  </span>
                </td>
                <td className="text-sm muted">
                  {form.created_at ? new Date(form.created_at).toLocaleDateString() : "Today"}
                </td>
                <td>
                  <div style={{ display: "flex", gap: "0.45rem", alignItems: "center" }}>
                    <Link to={`/review/${form.id}`} className="button secondary sm">
                      Review & Notify <ArrowRight size={13} />
                    </Link>
                    <button
                      type="button"
                      className="button danger-outline sm"
                      onClick={() => handleDeleteForm(form.id, form.original_filename)}
                      title="Delete this leave form"
                      style={{ padding: "0.45rem 0.6rem" }}
                    >
                      <Trash2 size={14} />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
