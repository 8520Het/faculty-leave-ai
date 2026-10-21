import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
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
  Layers,
  Sparkles,
  RefreshCw,
  Eye,
  Trash2,
  FileText,
  UploadCloud,
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
  const [rowConflicts, setRowConflicts] = useState({});
  const [validatingConflicts, setValidatingConflicts] = useState(false);
  const [sendingAll, setSendingAll] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [expandedImage, setExpandedImage] = useState(null);

  useEffect(() => {
    loadForms();
  }, [faculty?.email]);

  async function loadForms() {
    try {
      const data = await api.forms({
        applicant_name: faculty?.name,
        faculty_email: faculty?.email,
      });
      setForms(data);
      if (data.length > 0) {
        const belongsToMe = data.some((f) => f.id === formId);
        if (!formId || !belongsToMe) {
          navigate(`/review/${data[0].id}`, { replace: true });
        }
      } else {
        setReview(null);
      }
    } catch (err) {
      setError(err.message);
    }
  }

  useEffect(() => {
    if (!formId) return;
    loadReviewData(formId);
  }, [formId]);

  async function checkRowConflict(rowNum, draftData, applicantName, formYear) {
    if (!draftData) return null;
    try {
      const p = draftData.parsed || {};
      const t = draftData.timetable || {};
      const sub = draftData.substitute || {};

      const sem = p.semester !== undefined && p.semester !== null ? p.semester : t.semester || "";
      const div = p.division || t.division || "";
      const dayVal = p.day_of_week || t.day || "";
      const dDay = p.day;
      const dMonth = p.month;
      const roomVal = p.room || t.room || "";
      const subName = sub.name || "";
      const subCode = sub.code || "";
      const timeSlot = p.start_time
        ? `${p.start_time} TO ${p.end_time || ""}`
        : p.time || (t.start_time ? `${t.start_time} TO ${t.end_time || ""}` : "");

      const res = await api.checkConflict({
        day: dayVal,
        date_day: dDay,
        date_month: dMonth,
        date_year: formYear || review?.form?.year || 2026,
        time_slot: timeSlot,
        substitute_name: subName,
        substitute_code: subCode,
        applicant_name: applicantName || review?.form?.applicant_name || "",
        room: roomVal,
        semester: String(sem),
        division: String(div),
        subject: p.subject || t.subject || "",
      });

      return res;
    } catch (e) {
      console.warn("Conflict check error for row", rowNum, e);
      return null;
    }
  }

  async function runAllConflictChecks(draftsObj, appName, formYear) {
    setValidatingConflicts(true);
    const conflictMap = {};
    const entries = Object.entries(draftsObj);
    await Promise.all(
      entries.map(async ([rowNum, draftData]) => {
        const res = await checkRowConflict(rowNum, draftData, appName, formYear);
        if (res && (res.has_conflict || res.has_warning)) {
          conflictMap[rowNum] = res;
        }
      })
    );
    setRowConflicts(conflictMap);
    setValidatingConflicts(false);
  }

  async function loadReviewData(id) {
    try {
      setError("");
      const data = await api.review(id, {
        applicant_name: faculty?.name,
        faculty_email: faculty?.email,
      });
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
      runAllConflictChecks(next, data.form?.applicant_name, data.form?.year);
    } catch (err) {
      setError(err.message);
    }
  }

  const selectedForm = useMemo(
    () => forms.find((item) => item.id === formId),
    [forms, formId]
  );

  async function handleSaveAllAndNotifyAll() {
    if (!formId) return;
    setSendingAll(true);
    setError("");
    setMessage("");
    try {
      // 1. Conflict verification against Department Timetable
      const conflictList = [];
      for (const [rNum, rConf] of Object.entries(rowConflicts)) {
        if (rConf.conflicts?.length > 0) {
          conflictList.push(
            `Row #${rNum} Substitute Conflict:\n` + rConf.conflicts.map((c) => `  • ${c}`).join("\n")
          );
        }
        if (rConf.warnings?.length > 0) {
          conflictList.push(
            `Row #${rNum} Timetable Discrepancy:\n` + rConf.warnings.map((w) => `  • ${w}`).join("\n")
          );
        }
      }

      if (conflictList.length > 0) {
        const confirmMsg =
          "⚠️ TIMETABLE CONFLICTS / DISCREPANCIES DETECTED:\n\n" +
          conflictList.join("\n\n") +
          "\n\nAre you sure you want to continue and dispatch notifications?";
        if (!window.confirm(confirmMsg)) {
          setSendingAll(false);
          return;
        }
      }

      // 2. Save all row drafts as REVIEWED
      for (const row of review?.assignments || []) {
        const draft = drafts[row.row_number];
        if (draft) {
          await api.updateAssignment(formId, row.row_number, {
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
        }
      }
      await api.generateEmails(formId);

      const result = await api.sendAllEmails(formId);
      setMessage(
        `All changes saved successfully! Dispatched notifications to all ${result.sent_count} substitute faculty.`
      );
      await loadReviewData(formId);
      loadForms();
      refreshNotifications();
    } catch (err) {
      setError(err.message);
    } finally {
      setSendingAll(false);
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
    setDrafts((current) => {
      const updatedRow = {
        ...current[rowNumber],
        [section]: {
          ...current[rowNumber][section],
          [field]: value,
        },
      };

      // Trigger conflict re-check dynamically for this updated row
      checkRowConflict(rowNumber, updatedRow, review?.form?.applicant_name, review?.form?.year).then((res) => {
        setRowConflicts((prev) => {
          if (res && (res.has_conflict || res.has_warning)) {
            return { ...prev, [rowNumber]: res };
          } else {
            const nextMap = { ...prev };
            delete nextMap[rowNumber];
            return nextMap;
          }
        });
      });

      return {
        ...current,
        [rowNumber]: updatedRow,
      };
    });
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
            <option value="">
              {forms.length > 0 ? "Choose a leave form" : "No leave forms submitted yet"}
            </option>
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

      {forms.length === 0 && (
        <div className="panel" style={{ padding: "3.5rem 1.5rem", textAlign: "center", marginTop: "1.25rem" }}>
          <FileText size={48} className="muted" style={{ marginBottom: "0.75rem", opacity: 0.5 }} />
          <h3 style={{ marginBottom: "0.5rem" }}>No Leave Forms Uploaded Yet</h3>
          <p className="muted" style={{ maxWidth: "480px", margin: "0 auto 1.5rem auto", fontSize: "0.92rem" }}>
            You ({faculty?.name}) have not submitted any leave application forms yet. Upload a leave sheet to extract arrangement rows and notify substitute faculty.
          </p>
          <button
            type="button"
            className="button primary"
            onClick={() => navigate("/upload")}
            style={{ display: "inline-flex", alignItems: "center", gap: "8px" }}
          >
            <UploadCloud size={16} /> Upload Leave Form
          </button>
        </div>
      )}

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
      <div className="section-title-wrap" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "1rem" }}>
        <div>
          <h3>Extracted Arrangement Rows & OCR Evidence</h3>
          <p className="text-sm muted">
            Inspect each cell's handwritten image crop next to the decoded AI fields.
          </p>
        </div>
        <button
          type="button"
          className="button primary"
          onClick={handleSaveAllAndNotifyAll}
          disabled={sendingAll || !review?.assignments?.length}
          style={{ display: "inline-flex", alignItems: "center", gap: "6px" }}
        >
          {sendingAll ? (
            <>
              <RefreshCw size={14} className="spinner" />
              Saving & Notifying All...
            </>
          ) : (
            <>
              <Send size={14} />
              Save All Changes & Notify All Faculty
            </>
          )}
        </button>
      </div>

      {/* TIMETABLE CONFLICTS TOP BANNER */}
      {Object.keys(rowConflicts).length > 0 && (
        <div
          style={{
            background: "#ffebee",
            border: "2px solid #d32f2f",
            borderRadius: "8px",
            padding: "1rem 1.25rem",
            marginBottom: "1.25rem",
            display: "flex",
            alignItems: "center",
            gap: "0.85rem",
          }}
        >
          <AlertTriangle size={24} style={{ color: "#d32f2f", flexShrink: 0 }} />
          <div>
            <div style={{ color: "#b71c1c", fontWeight: 700, fontSize: "0.95rem" }}>
              TIMETABLE CONFLICT / ENTRY MISMATCH DETECTED ({Object.keys(rowConflicts).length} ROW{Object.keys(rowConflicts).length > 1 ? "S" : ""} FLAGGED)
            </div>
            <div style={{ fontSize: "0.84rem", color: "#37474f", marginTop: "0.25rem", lineHeight: 1.45 }}>
              One or more lecture rows conflict with the official department timetable (substitute faculty already teaching, division not recognized, or room mismatch). Review the highlighted red warning boxes on the flagged rows below.
            </div>
          </div>
        </div>
      )}

      <div className="rows-list">
        {(review?.assignments || []).map((row) => {
          const draft = drafts[row.row_number];
          if (!draft) return null;

          return (
            <article className="panel row-inspection-card" key={row.id || row.row_number}>
              <div className="row-crop-col">
                <div className="row-crop-header">
                  <span className="row-num-pill">Row #{row.row_number}</span>
                  <span className={`badge ${row.reviewed ? "ok" : "warn"}`}>{row.status}</span>
                  {rowConflicts[row.row_number] && (
                    <span
                      className="badge danger"
                      style={{
                        background: "#d32f2f",
                        color: "#fff",
                        fontWeight: 700,
                        display: "inline-flex",
                        alignItems: "center",
                        gap: "4px",
                      }}
                    >
                      <AlertTriangle size={12} />
                      CONFLICT
                    </span>
                  )}
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

                {/* TIMETABLE CONFLICT / ENTRY MISMATCH RED MESSAGE BOX */}
                {rowConflicts[row.row_number] &&
                  (rowConflicts[row.row_number].conflicts?.length > 0 ||
                    rowConflicts[row.row_number].warnings?.length > 0) && (
                    <div
                      className="timetable-conflict-card"
                      style={{
                        marginTop: "1rem",
                        padding: "0.9rem 1.15rem",
                        borderRadius: "8px",
                        background: "#fff5f5",
                        border: "2px solid #d32f2f",
                        color: "#b71c1c",
                        boxShadow: "0 2px 8px rgba(211, 47, 47, 0.12)",
                      }}
                    >
                      <div
                        style={{
                          display: "flex",
                          alignItems: "center",
                          gap: "0.45rem",
                          fontWeight: 700,
                          fontSize: "0.9rem",
                          color: "#c62828",
                          marginBottom: "0.45rem",
                        }}
                      >
                        <AlertTriangle size={18} style={{ color: "#d32f2f", flexShrink: 0 }} />
                        <span>TIMETABLE CONFLICT / ENTRY DISCREPANCY DETECTED</span>
                      </div>

                      <ul
                        style={{
                          margin: 0,
                          paddingLeft: "1.25rem",
                          fontSize: "0.84rem",
                          lineHeight: 1.55,
                        }}
                      >
                        {rowConflicts[row.row_number].conflicts?.map((c, i) => (
                          <li key={`c-${i}`} style={{ fontWeight: 600, color: "#b71c1c" }}>
                            {c}
                          </li>
                        ))}
                        {rowConflicts[row.row_number].warnings?.map((w, i) => (
                          <li key={`w-${i}`} style={{ color: "#c62828" }}>
                            {w}
                          </li>
                        ))}
                      </ul>

                      <div
                        style={{
                          fontSize: "0.78rem",
                          color: "#880e4f",
                          marginTop: "0.45rem",
                          fontStyle: "italic",
                        }}
                      >
                        Please review the lecture date, time slot, division, room number, or assign an available substitute faculty.
                      </div>
                    </div>
                  )}
              </div>
            </article>
          );
        })}
      </div>

      {review?.assignments?.length > 0 && (
        <div
          className="save-all-bottom-bar panel"
          style={{
            marginTop: "1.5rem",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            flexWrap: "wrap",
            gap: "1rem",
            padding: "1.25rem 1.5rem",
          }}
        >
          <div>
            <h4 style={{ margin: 0, fontSize: "1rem" }}>Finished editing arrangement rows?</h4>
            <p className="text-sm muted" style={{ margin: "2px 0 0 0" }}>
              Saves all timetable and substitute modifications and automatically notifies all substitute faculty members.
            </p>
          </div>
          <button
            type="button"
            className="button primary"
            onClick={handleSaveAllAndNotifyAll}
            disabled={sendingAll}
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: "8px",
              padding: "0.75rem 1.4rem",
              fontSize: "0.95rem",
            }}
          >
            {sendingAll ? (
              <>
                <RefreshCw size={16} className="spinner" />
                Saving & Notifying All...
              </>
            ) : (
              <>
                <Send size={16} />
                Save All Changes & Notify All Faculty
              </>
            )}
          </button>
        </div>
      )}

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
