import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { api, fileUrl } from "../api";

const emptyParsed = {
  semester: "",
  division: "",
  day: "",
  month: "",
  start_time: "",
  end_time: "",
  room: "",
  subject: "",
  staff: "",
};

export default function Review() {
  const { formId } = useParams();
  const navigate = useNavigate();
  const [forms, setForms] = useState([]);
  const [review, setReview] = useState(null);
  const [drafts, setDrafts] = useState({});
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    api.forms().then(setForms).catch((err) => setError(err.message));
  }, []);

  useEffect(() => {
    if (!formId) return;
    api
      .review(formId)
      .then((data) => {
        setReview(data);
        const next = {};
        for (const row of data.assignments || []) {
          next[row.row_number] = {
            status: row.status || "REVIEWED",
            parsed: { ...emptyParsed, ...(row.parsed || {}) },
            substitute: {
              name: row.substitute?.name || row.parsed?.staff || "",
              email: row.substitute?.email || "",
              department: row.substitute?.department || "IT",
            },
            timetable: {
              semester: row.timetable?.semester || row.parsed?.semester || "",
              division: row.timetable?.division || row.parsed?.division || "",
              start_time: row.timetable?.start_time || row.parsed?.start_time || "",
              end_time: row.timetable?.end_time || row.parsed?.end_time || "",
              room: row.timetable?.room || row.parsed?.room || "",
              subject: row.timetable?.subject || row.parsed?.subject || "",
              normal_faculty: row.timetable?.normal_faculty || data.form.applicant_name,
            },
          };
        }
        setDrafts(next);
      })
      .catch((err) => setError(err.message));
  }, [formId]);

  const selected = useMemo(
    () => forms.find((item) => item.id === formId),
    [forms, formId]
  );

  async function saveRow(rowNumber) {
    setError("");
    setMessage("");
    try {
      const draft = drafts[rowNumber];
      await api.updateAssignment(formId, rowNumber, {
        status: "REVIEWED",
        parsed: {
          ...draft.parsed,
          semester: draft.parsed.semester === "" ? null : Number(draft.parsed.semester),
          day: draft.parsed.day === "" ? null : Number(draft.parsed.day),
        },
        substitute: draft.substitute,
        timetable: {
          ...draft.timetable,
          semester: draft.timetable.semester === "" ? null : Number(draft.timetable.semester),
        },
        requires_review: false,
      });
      setMessage(`Row ${rowNumber} saved.`);
    } catch (err) {
      setError(err.message);
    }
  }

  async function generateEmails() {
    setError("");
    try {
      await api.generateEmails(formId);
      navigate("/emails");
    } catch (err) {
      setError(err.message);
    }
  }

  function updateDraft(rowNumber, section, field, value) {
    setDrafts((current) => ({
      ...current,
      [rowNumber]: {
        ...current[rowNumber],
        [section]: {
          ...current[rowNumber][section],
          [field]: value,
        },
      },
    }));
  }

  return (
    <section>
      <h2>Human review</h2>
      <p className="lede">
        Correct the structured assignment before grouped emails are generated.
        OCR suggestions are starting points, not approvals.
      </p>
      <div className="panel">
        <label htmlFor="formSelect">Form</label>
        <select
          id="formSelect"
          value={formId || ""}
          onChange={(event) => navigate(`/review/${event.target.value}`)}
        >
          <option value="">Select a processed form</option>
          {forms.map((form) => (
            <option key={form.id} value={form.id}>
              {form.applicant_name} — {form.status} — {form.original_filename}
            </option>
          ))}
        </select>
        {selected?.error_message && <p className="error">{selected.error_message}</p>}
        {review?.form && (
          <p className="muted">
            Detection: {review.form.detection_strategy || "n/a"} · {review.form.status}
          </p>
        )}
      </div>
      {(review?.assignments || []).map((row) => {
        const draft = drafts[row.row_number];
        if (!draft) return null;
        return (
          <article className="panel assignment" key={row.id || row.row_number}>
            <div>
              <h3>Row {row.row_number}</h3>
              <span className={`badge ${row.reviewed ? "ok" : "warn"}`}>{row.status}</span>
              {row.image_path && (
                <img
                  className="thumb"
                  alt={`Row ${row.row_number}`}
                  src={fileUrl(formId, "row", row.row_number)}
                />
              )}
              <p className="muted">Class OCR: {row.class_ocr?.selected || row.class_ocr?.normal}</p>
              <p className="muted">
                Subject OCR: {row.ocr?.subject} / {row.selected_subject?.value}
              </p>
            </div>
            <div>
              <div className="grid" style={{ gridTemplateColumns: "repeat(2, 1fr)" }}>
                {["semester", "division", "day", "month", "start_time", "end_time", "room", "subject"].map(
                  (field) => (
                    <div key={field}>
                      <label>{field}</label>
                      <input
                        value={draft.parsed[field] ?? ""}
                        onChange={(event) =>
                          updateDraft(row.row_number, "parsed", field, event.target.value)
                        }
                      />
                    </div>
                  )
                )}
              </div>
              <label>Substitute name</label>
              <input
                value={draft.substitute.name}
                onChange={(event) =>
                  updateDraft(row.row_number, "substitute", "name", event.target.value)
                }
              />
              <label>Substitute email</label>
              <input
                value={draft.substitute.email}
                onChange={(event) =>
                  updateDraft(row.row_number, "substitute", "email", event.target.value)
                }
              />
              <button type="button" onClick={() => saveRow(row.row_number)}>
                Save corrections
              </button>
            </div>
          </article>
        );
      })}
      {formId && (
        <div className="row">
          <button type="button" onClick={generateEmails}>
            Generate grouped emails
          </button>
          <Link to="/emails">Open email desk</Link>
        </div>
      )}
      {message && <p className="muted">{message}</p>}
      {error && <p className="error">{error}</p>}
    </section>
  );
}
