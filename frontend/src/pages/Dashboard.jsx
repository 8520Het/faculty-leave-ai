import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .dashboard()
      .then(setData)
      .catch((err) => setError(err.message));
  }, []);

  if (error) return <p className="error">{error}</p>;
  if (!data) return <p>Loading desk summary…</p>;

  const counts = data.status_counts || {};

  return (
    <section>
      <h2>Arrangement desk</h2>
      <p className="lede">
        New forms are never auto-mailed. Extracted rows stay in review until a
        person confirms the substitute, subject, room, and time.
      </p>
      <div className="cards">
        <article className="card">
          <p className="muted">Forms</p>
          <div className="stat">{data.form_count}</div>
        </article>
        <article className="card">
          <p className="muted">Needs review</p>
          <div className="stat">{counts.NEEDS_REVIEW || 0}</div>
        </article>
        <article className="card">
          <p className="muted">Processing</p>
          <div className="stat">{(counts.PROCESSING || 0) + (counts.QUEUED || 0)}</div>
        </article>
        <article className="card">
          <p className="muted">Failed</p>
          <div className="stat">{counts.FAILED || 0}</div>
        </article>
      </div>
      <div className="row" style={{ margin: "1.2rem 0" }}>
        <Link className="button" to="/upload">
          Upload a leave form
        </Link>
        <span className="badge">{data.demo_mode ? "Demo mode on" : "Live OCR"}</span>
        <span className="muted">Active semesters: {data.active_semesters?.join(", ")}</span>
      </div>
      <div className="panel">
        <h3>Recent forms</h3>
        <table>
          <thead>
            <tr>
              <th>Applicant</th>
              <th>File</th>
              <th>Status</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {(data.recent || []).map((form) => (
              <tr key={form.id}>
                <td>{form.applicant_name}</td>
                <td>{form.original_filename}</td>
                <td>
                  <span className="badge">{form.status}</span>
                </td>
                <td>
                  <Link to={`/review/${form.id}`}>Open</Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
