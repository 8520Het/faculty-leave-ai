import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import { useAuth } from "../context/AuthContext";

export default function History() {
  const { faculty } = useAuth();
  const [forms, setForms] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .forms({
        applicant_name: faculty?.name,
        faculty_email: faculty?.email,
      })
      .then(setForms)
      .catch((err) => setError(err.message));
  }, [faculty?.email]);

  return (
    <section>
      <h2>Processing history</h2>
      {error && <p className="error">{error}</p>}
      <div className="panel">
        <table>
          <thead>
            <tr>
              <th>When</th>
              <th>Applicant</th>
              <th>File</th>
              <th>Status</th>
              <th>Rows</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {forms.map((form) => (
              <tr key={form.id}>
                <td>{form.created_at?.replace("T", " ").slice(0, 19)}</td>
                <td>{form.applicant_name}</td>
                <td>{form.original_filename}</td>
                <td>
                  <span className="badge">{form.status}</span>
                  {form.demo ? " demo" : ""}
                </td>
                <td>{form.assignment_count}</td>
                <td>
                  <Link to={`/review/${form.id}`}>Review</Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
