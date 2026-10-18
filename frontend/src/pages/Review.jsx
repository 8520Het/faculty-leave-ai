import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { api, fileUrl } from "../api";
import { useAuth } from "../context/AuthContext";
import {
  Send,
  Mail,
  CheckCircle2,
  AlertTriangle,
  Clock,
  User,
  BookOpen,
  Calendar,
  Save,
  Check,
  ChevronRight,
  ExternalLink,
  Layers,
  Sparkles,
  RefreshCw,
  Eye,
  Trash2,
} from "lucide-react";

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
  const { faculty, refreshNotifications } = useAuth();

  const [forms, setForms] = useState([]);
  const [review, setReview] = useState(null);
  const [drafts, setDrafts] = useState({});
  const [sendingEmailId, setSendingEmailId] = useState(null);
  const [sendingAll, setSendingAll] = useState(false);
  const [savedRowId, setSavedRowId] = useState(null);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [expandedImage, setExpandedImage] = useState(null);

  useEffect(() => {
    loadForms();
  }, []);

  async function loadForms() {
    try {
      const data = await api.forms();
      setForms(data);
      if (!formId && data.length > 0) {
        navigate(`/review/${data[0].id}`, { replace: true });
      }
    } catch (err) {
      setError(err.message);
    }
  }

  useEffect(() => {
    if (!formId) return;
    loadReviewData(formId);
  }, [formId]);

  async function loadReviewData(id) {
    try {
      const data = await api.review(id);
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
    } catch (err) {
      setError(err.message);
    }
  }

  const selectedForm = useMemo(
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
      setSavedRowId(rowNumber);
      setTimeout(() => setSavedRowId(null), 3000);
      setMessage(`Row ${rowNumber} corrections successfully saved.`);
      // Refresh emails previews after update
      await api.generateEmails(formId);
      await loadReviewData(formId);
      loadForms();
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleSendNotification(emailId) {
    setSendingEmailId(emailId);
    setError("");
    setMessage("");
    try {
      const updated = await api.sendEmail(emailId);
      setMessage(`Notification dispatched successfully to ${updated.to}!`);
      await loadReviewData(formId);
      loadForms();
      refreshNotifications();
    } catch (err) {
      setError(err.message);
    } finally {
      setSendingEmailId(null);
    }
  }

  async function handleSendAllNotifications() {
    setSendingAll(true);
    setError("");
    setMessage("");
    try {
      const result = await api.sendAllEmails(formId);
      setMessage(`All ${result.sent_count} substitute faculty notifications have been dispatched!`);
      await loadReviewData(formId);
      loadForms();
      refreshNotifications();
    } catch (err) {
      setError(err.message);
    } finally {
      setSendingAll(false);
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

  async function handleDeleteCurrentForm() {
    if (!formId) return;
    const name = selectedForm
      ? `${selectedForm.applicant_name} (${selectedForm.original_filename})`
      : formId;
    if (
      !window.confirm(
        `Are you sure you want to delete form "${name}"? All scanned rows and notifications will be permanently removed.`
      )
    ) {
      return;
    }
    try {
      await api.deleteForm(formId);
      const remainingForms = forms.filter((f) => f.id !== formId);
      setForms(remainingForms);
      if (remainingForms.length > 0) {
        navigate(`/review/${remainingForms[0].id}`, { replace: true });
      } else {
        navigate("/", { replace: true });
      }
    } catch (err) {
      setError(`Failed to delete form: ${err.message}`);
    }
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <h2>Scanned Results & Substitute Dispatch</h2>
        <p className="lede">
          Examine the AI OCR results, cross-referenced timetable periods, and notify the resultant
          substitute faculty members.
        </p>
      </div>

      <div className="form-selector-bar panel">
        <div className="form-selector-left">
          <label htmlFor="formSelect">Select Form Sheet:</label>
          <select
            id="formSelect"
            value={formId || ""}
            onChange={(e) => navigate(`/review/${e.target.value}`)}
            className="form-select-dropdown"
          >
            <option value="">Choose a leave form</option>
            {forms.map((f) => (
              <option key={f.id} value={f.id}>
                {f.applicant_name} ({f.original_filename}) — {f.status}
              </option>
            ))}
          </select>
        </div>

        {selectedForm && (
          <div className="form-meta-tags" style={{ display: "flex", alignItems: "center", gap: "0.5rem", flexWrap: "wrap" }}>
            <span className="badge info">Applicant: {selectedForm.applicant_name}</span>
            {(() => {
              const currentStatus = review?.form?.status || selectedForm.status;
              const badgeClass =
                currentStatus === "CONFIRMED" || currentStatus === "NOTIFIED"
                  ? "ok"
                  : currentStatus === "REVIEWED"
                  ? "info"
                  : currentStatus === "NEEDS_REVIEW"
                  ? "warn"
                  : "default";
              return (
                <span className={`badge ${badgeClass}`}>
                  Status: {currentStatus}
                </span>
              );
            })()}
            <span className="badge text-xs">
              Strategy: {review?.form?.detection_strategy || selectedForm.detection_strategy || "Auto-grid"}
            </span>
            <button
              type="button"
              className="button danger-outline sm"
              onClick={handleDeleteCurrentForm}
              title="Delete this leave form"
              style={{ marginLeft: "auto", display: "inline-flex", alignItems: "center", gap: "5px" }}
            >
              <Trash2 size={14} /> Delete Form
            </button>
          </div>
        )}
      </div>

      {/* NOTIFICATIONS SECTION - PROMINENT & RESULTANT FACULTY FOCUSED */}
      {review?.form && (
        <div className="panel notification-dispatch-card">
          <div className="notification-card-header">
            <div className="notification-title-wrap">
              <Mail className="mail-primary-icon" size={24} />
              <div>
                <h3>Resultant Faculty Notifications</h3>
                <p className="text-sm muted">
                  Notifications drafted for the substitute faculty members based on the scanned
                  lecture arrangement rows.
                </p>
              </div>
            </div>

            {review.form.emails?.length > 0 && (
              <button
                type="button"
                className="button primary send-all-btn"
                onClick={handleSendAllNotifications}
                disabled={sendingAll}
              >
                {sendingAll ? (
                  <>
                    <RefreshCw size={16} className="spinner" />
                    Sending All...
                  </>
                ) : (
                  <>
                    <Send size={16} />
                    Notify All Resultant Faculty
                  </>
                )}
              </button>
            )}
          </div>

          {(!review.form.emails || review.form.emails.length === 0) ? (
            <div className="empty-notification-box">
              <AlertTriangle size={24} className="warn-icon" />
              <div>
                <h4>No notification drafts yet</h4>
                <p className="text-sm muted">
                  Review the extracted rows below and click "Generate / Update Email Drafts" to
                  group the arrangement by substitute faculty.
                </p>
                <button
                  type="button"
                  className="button secondary sm"
                  onClick={() => api.generateEmails(formId).then(() => loadReviewData(formId))}
                >
                  Generate Email Drafts
                </button>
              </div>
            </div>
          ) : (
            <div className="notifications-grid">
              {review.form.emails.map((email) => {
                const isSent = email.status === "SENT" || email.status === "ACKNOWLEDGED";
                const isSending = sendingEmailId === email.id;

                return (
                  <div key={email.id} className={`notification-item-card ${isSent ? "sent" : ""}`}>
                    <div className="notification-item-top">
                      <div className="substitute-identity">
                        <div className="substitute-avatar">
                          <User size={18} />
                        </div>
                        <div>
                          <h4 className="substitute-name">
                            {email.substitute_name || "Substitute Faculty"}
                          </h4>
                          <span className="substitute-email">{email.to}</span>
                        </div>
                      </div>

                      <div className="notification-status-badge">
                        {isSent ? (
                          <span className="badge ok">
                            <CheckCircle2 size={13} style={{ marginRight: "3px" }} />
                            Notification Sent
                          </span>
                        ) : (
                          <span className="badge warn">
                            <Clock size={13} style={{ marginRight: "3px" }} />
                            Ready to Send
                          </span>
                        )}
                      </div>
                    </div>

                    <div className="notification-details-summary">
                      <p className="notif-subject">
                        <strong>Subject:</strong> {email.subject}
                      </p>
                      <span className="badge info text-xs">
                        {email.assignment_count} lecture(s) to cover
                      </span>
                    </div>

                    <div className="notification-body-preview">
                      <pre>{email.body}</pre>
                    </div>

                    <div className="notification-item-actions">
                      <button
                        type="button"
                        className={`button ${isSent ? "secondary" : "primary"} sm`}
                        onClick={() => handleSendNotification(email.id)}
                        disabled={isSending}
                      >
                        {isSending ? (
                          <>
                            <RefreshCw size={14} className="spinner" />
                            Sending...
                          </>
                        ) : isSent ? (
                          <>
                            <RefreshCw size={14} />
                            Re-send Notification
                          </>
                        ) : (
                          <>
                            <Send size={14} />
                            Send Notification to Faculty
                          </>
                        )}
                      </button>

                      <Link to="/notifications" className="button secondary sm">
                        View in Inbox <ExternalLink size={14} />
                      </Link>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {message && (
        <div className="alert-box success">
          <CheckCircle2 size={18} />
          <span>{message}</span>
        </div>
      )}
      {error && (
        <div className="alert-box error">
          <AlertTriangle size={18} />
          <span>{error}</span>
        </div>
      )}

      {/* DETECTED ROWS BREAKDOWN */}
      <div className="section-title-wrap">
        <h3>Extracted Arrangement Rows & OCR Evidence</h3>
        <p className="text-sm muted">
          Inspect each cell's handwritten image crop next to the decoded AI fields. Make adjustments
          if handwriting was ambiguous.
        </p>
      </div>

      <div className="rows-list">
        {(review?.assignments || []).map((row) => {
          const draft = drafts[row.row_number];
          if (!draft) return null;
          const isRowSaved = savedRowId === row.row_number;

          return (
            <article className="panel row-inspection-card" key={row.id || row.row_number}>
              <div className="row-crop-col">
                <div className="row-crop-header">
                  <span className="row-num-pill">Row #{row.row_number}</span>
                  <span className={`badge ${row.reviewed ? "ok" : "warn"}`}>{row.status}</span>
                </div>

                {row.image_path ? (
                  <div
                    className="row-crop-image-container"
                    onClick={() => setExpandedImage(fileUrl(formId, "row", row.row_number))}
                  >
                    <img
                      className="row-crop-img"
                      alt={`Handwritten Row ${row.row_number}`}
                      src={fileUrl(formId, "row", row.row_number)}
                    />
                    <div className="image-zoom-overlay">
                      <Eye size={16} /> Click to expand
                    </div>
                  </div>
                ) : (
                  <div className="no-crop-placeholder">
                    <p className="text-xs muted">Simulated / Demo Row</p>
                  </div>
                )}

                <div className="ocr-raw-summary">
                  <p className="text-xs">
                    <strong>Class OCR:</strong> {row.class_ocr?.selected || row.class_ocr?.normal || "Sem 7-F"}
                  </p>
                  <p className="text-xs">
                    <strong>Subject OCR:</strong> {row.ocr?.subject || row.selected_subject?.value || "AJT"}
                  </p>
                  <p className="text-xs">
                    <strong>Staff OCR:</strong> {row.ocr?.staff_name || "Sandeep R. Suthar"}
                  </p>
                </div>
              </div>

              <div className="row-fields-col">
                <div className="fields-grid-two-col">
                  <div>
                    <label>Semester</label>
                    <input
                      type="number"
                      value={draft.parsed.semester ?? ""}
                      onChange={(e) => updateDraft(row.row_number, "parsed", "semester", e.target.value)}
                      placeholder="e.g. 7"
                    />
                  </div>

                  <div>
                    <label>Division</label>
                    <input
                      value={draft.parsed.division ?? ""}
                      onChange={(e) => updateDraft(row.row_number, "parsed", "division", e.target.value)}
                      placeholder="e.g. F"
                    />
                  </div>

                  <div>
                    <label>Lecture Date (Day & Month)</label>
                    <div className="row" style={{ gap: "4px" }}>
                      <input
                        style={{ width: "70px" }}
                        value={draft.parsed.day ?? ""}
                        onChange={(e) => updateDraft(row.row_number, "parsed", "day", e.target.value)}
                        placeholder="Day (3)"
                      />
                      <input
                        value={draft.parsed.month ?? ""}
                        onChange={(e) => updateDraft(row.row_number, "parsed", "month", e.target.value)}
                        placeholder="Month (AUG)"
                      />
                    </div>
                  </div>

                  <div>
                    <label>Lecture Time Slot</label>
                    <div className="row" style={{ gap: "4px" }}>
                      <input
                        value={draft.parsed.start_time ?? ""}
                        onChange={(e) => updateDraft(row.row_number, "parsed", "start_time", e.target.value)}
                        placeholder="14:30"
                      />
                      <span className="muted" style={{ alignSelf: "center" }}>to</span>
                      <input
                        value={draft.parsed.end_time ?? ""}
                        onChange={(e) => updateDraft(row.row_number, "parsed", "end_time", e.target.value)}
                        placeholder="15:30"
                      />
                    </div>
                  </div>

                  <div>
                    <label>Room Number</label>
                    <input
                      value={draft.parsed.room ?? ""}
                      onChange={(e) => updateDraft(row.row_number, "parsed", "room", e.target.value)}
                      placeholder="e.g. 26"
                    />
                  </div>

                  <div>
                    <label>Subject</label>
                    <input
                      value={draft.parsed.subject ?? ""}
                      onChange={(e) => updateDraft(row.row_number, "parsed", "subject", e.target.value)}
                      placeholder="e.g. AJT"
                    />
                  </div>
                </div>

                <div className="substitute-assigned-box">
                  <div className="substitute-inputs-grid">
                    <div>
                      <label>Assigned Substitute Faculty Name</label>
                      <input
                        value={draft.substitute.name}
                        onChange={(e) => updateDraft(row.row_number, "substitute", "name", e.target.value)}
                        placeholder="e.g. Sandeep R. Suthar"
                      />
                    </div>
                    <div>
                      <label>Substitute Official Email (Notification Target)</label>
                      <input
                        value={draft.substitute.email}
                        onChange={(e) => updateDraft(row.row_number, "substitute", "email", e.target.value)}
                        placeholder="e.g. sandeep.suthar@ddu.ac.in"
                      />
                    </div>
                  </div>
                </div>

                <div className="row-card-footer">
                  <button
                    type="button"
                    className="button secondary sm"
                    onClick={() => saveRow(row.row_number)}
                  >
                    {isRowSaved ? (
                      <>
                        <Check size={14} /> Saved!
                      </>
                    ) : (
                      <>
                        <Save size={14} /> Save Row Changes
                      </>
                    )}
                  </button>
                </div>
              </div>
            </article>
          );
        })}
      </div>

      {expandedImage && (
        <div className="modal-backdrop" onClick={() => setExpandedImage(null)}>
          <div className="image-modal-card" onClick={(e) => e.stopPropagation()}>
            <img src={expandedImage} alt="Expanded row crop" className="modal-full-img" />
            <button
              type="button"
              className="button secondary sm close-modal-btn"
              onClick={() => setExpandedImage(null)}
            >
              Close Preview
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
