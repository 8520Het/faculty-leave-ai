import { useState, useEffect, useMemo } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import { useAuth } from "../context/AuthContext";
import {
  ShieldCheck,
  Calendar,
  Upload,
  CheckCircle2,
  AlertTriangle,
  FileText,
  Mail,
  Edit2,
  Trash2,
  Plus,
  RefreshCw,
  Eye,
  Clock,
  Layers,
  MapPin,
  Check,
  X,
  FileCheck,
  Sparkles,
} from "lucide-react";

export default function AdminPanel() {
  const { faculty, isAdmin } = useAuth();
  const [activeTab, setActiveTab] = useState("timetable"); // 'timetable' | 'forms' | 'notifications'

  // Timetable State
  const [timetableFile, setTimetableFile] = useState(null);
  const [parsing, setParsing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [draftTimetable, setDraftTimetable] = useState(null);
  const [editingSlotId, setEditingSlotId] = useState(null);
  const [slotForm, setSlotForm] = useState({});
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  // Stored Timetables
  const [storedSlots, setStoredSlots] = useState([]);
  const [loadingStored, setLoadingStored] = useState(false);
  const [expandedTimetableKeys, setExpandedTimetableKeys] = useState({});

  function toggleTimetableExpand(key) {
    setExpandedTimetableKeys((prev) => ({
      ...prev,
      [key]: !prev[key],
    }));
  }

  // Group stored slots image-wise (per class timetable)
  const timetableGroups = useMemo(() => {
    const groups = {};
    for (const slot of (storedSlots || [])) {
      const sem = slot.semester;
      const div = slot.division;
      const key = `${sem}-${div}`;
      if (!groups[key]) {
        groups[key] = {
          key,
          semester: sem,
          division: div,
          academic_year: slot.academic_year || "2026-27",
          slots: [],
          rooms: new Set(),
          subjects: new Set(),
          faculties: new Set(),
        };
      }
      groups[key].slots.push(slot);
      if (slot.room) groups[key].rooms.add(slot.room);
      if (slot.subject) groups[key].subjects.add(slot.subject);
      if (slot.faculty_name) groups[key].faculties.add(slot.faculty_name);
    }
    return Object.values(groups);
  }, [storedSlots]);

  // Department Forms State
  const [allForms, setAllForms] = useState([]);
  const [loadingForms, setLoadingForms] = useState(false);

  // Department Notifications State
  const [allNotifications, setAllNotifications] = useState([]);
  const [loadingNotifs, setLoadingNotifs] = useState(false);

  useEffect(() => {
    if (isAdmin) {
      loadStoredTimetables();
      loadDepartmentForms();
      loadDepartmentNotifications();
    }
  }, [isAdmin]);

  async function loadStoredTimetables() {
    setLoadingStored(true);
    try {
      const res = await api.adminTimetableEntries();
      setStoredSlots(res || []);
    } catch (err) {
      console.error("Error loading stored timetables:", err);
    } finally {
      setLoadingStored(false);
    }
  }

  async function loadDepartmentForms() {
    setLoadingForms(true);
    try {
      const res = await api.adminForms();
      setAllForms(res || []);
    } catch (err) {
      console.error("Error loading department forms:", err);
    } finally {
      setLoadingForms(false);
    }
  }

  async function loadDepartmentNotifications() {
    setLoadingNotifs(true);
    try {
      const res = await api.adminEmails();
      setAllNotifications(res || []);
    } catch (err) {
      console.error("Error loading department notifications:", err);
    } finally {
      setLoadingNotifs(false);
    }
  }

  async function handleAnalyzeTimetable() {
    if (!timetableFile) {
      setError("Please select a timetable image to upload.");
      return;
    }
    setParsing(true);
    setError("");
    setMessage("");
    try {
      const result = await api.uploadTimetable(timetableFile);
      setDraftTimetable(result);
      setMessage(
        `Successfully extracted Semester ${result.semester} Division ${result.division} (${result.total_slots} slots detected). Review the grid below before saving.`
      );
    } catch (err) {
      setError(`OCR Extraction Error: ${err.message}`);
    } finally {
      setParsing(false);
    }
  }

  async function handleLoadSample(key) {
    setParsing(true);
    setError("");
    setMessage("");
    try {
      const result = await api.loadSampleTimetable(key);
      setDraftTimetable(result);
      setMessage(
        `Loaded official schedule template for Semester ${result.semester} Division ${result.division}. Review the grid below and click Commit to save.`
      );
    } catch (err) {
      setError(`Sample load error: ${err.message}`);
    } finally {
      setParsing(false);
    }
  }

  async function handleCommitTimetable() {
    if (!draftTimetable || !draftTimetable.slots?.length) {
      setError("No slots to commit.");
      return;
    }
    setSaving(true);
    setError("");
    try {
      const res = await api.commitTimetable({
        semester: draftTimetable.semester,
        division: draftTimetable.division,
        academic_year: draftTimetable.academic_year || "2026-27",
        slots: draftTimetable.slots,
      });
      setMessage(`Success: ${res.message}`);
      loadStoredTimetables();
      setDraftTimetable(null);
      setTimetableFile(null);
    } catch (err) {
      setError(`Commit error: ${err.message}`);
    } finally {
      setSaving(false);
    }
  }

  function handleStartEditSlot(slot) {
    setEditingSlotId(slot.id);
    setSlotForm({ ...slot });
  }

  function handleSaveEditSlot() {
    if (!draftTimetable) return;
    const updated = draftTimetable.slots.map((s) =>
      s.id === editingSlotId ? { ...s, ...slotForm } : s
    );
    setDraftTimetable({ ...draftTimetable, slots: updated });
    setEditingSlotId(null);
  }

  function handleDeleteSlot(id) {
    if (!draftTimetable) return;
    const updated = draftTimetable.slots.filter((s) => s.id !== id);
    setDraftTimetable({
      ...draftTimetable,
      slots: updated,
      total_slots: updated.length,
    });
  }

  function handleAddSlot() {
    if (!draftTimetable) return;
    const newId = `slot_new_${Date.now()}`;
    const newSlot = {
      id: newId,
      day: "Monday",
      time_slot: "8:30 TO 9:30",
      subject: "NEW",
      subject_name: "Subject Name",
      faculty_code: "TBD",
      faculty_name: "Faculty Name",
      room: draftTimetable.default_room || "26",
      batch: "ALL",
      is_lab: false,
      raw_text: "",
    };
    setDraftTimetable({
      ...draftTimetable,
      slots: [...draftTimetable.slots, newSlot],
      total_slots: draftTimetable.slots.length + 1,
    });
    setEditingSlotId(newId);
    setSlotForm(newSlot);
  }

  async function handleDeleteSingleTimetable(sem, div, slotCount, otherClasses) {
    const keepNotice = otherClasses
      ? `All other class timetables (${otherClasses}) will remain completely intact.`
      : "No other class timetables are affected.";

    const confirmed = window.confirm(
      `Are you sure you want to delete ONLY the timetable for Semester ${sem} Division ${div}?\n\n` +
      `• Slots to remove: ${slotCount} slots.\n` +
      `• ${keepNotice}\n\n` +
      `Click OK to proceed with deleting only Sem ${sem} Div ${div}.`
    );
    if (!confirmed) return;

    try {
      const res = await api.deleteTimetableEntries(sem, div);
      setMessage(res.message || `Deleted timetable for Semester ${sem} Division ${div}.`);
      loadStoredTimetables();
    } catch (err) {
      setError(`Failed to delete timetable: ${err.message}`);
    }
  }

  async function handleSeedDefaults() {
    try {
      const res = await api.seedDefaultTimetables();
      setMessage(res.message || "Loaded official preset schedule (Sem 7 Div F).");
      loadStoredTimetables();
    } catch (err) {
      setError(`Failed to seed defaults: ${err.message}`);
    }
  }

  function handleDiscardDraft() {
    setDraftTimetable(null);
    setTimetableFile(null);
    setEditingSlotId(null);
    setMessage("Timetable draft discarded.");
  }

  if (!isAdmin) {
    return (
      <div className="page-container">
        <div className="panel" style={{ textAlign: "center", padding: "3rem" }}>
          <ShieldCheck size={56} style={{ color: "var(--danger)", margin: "0 auto 1rem" }} />
          <h2>Administrative Privilege Required</h2>
          <p className="muted" style={{ maxWidth: "500px", margin: "0.5rem auto 1.5rem" }}>
            The Admin Panel is reserved for Department Leadership (Head of Department Dr. Vipul K. Dabhi)
            to configure university timetables and oversee department arrangements.
          </p>
          <div style={{ display: "flex", gap: "1rem", justifyContent: "center" }}>
            <Link to="/my-schedule" className="btn btn-primary">
              View My Teaching Schedule
            </Link>
            <Link to="/dashboard" className="btn btn-secondary">
              Go to Dashboard
            </Link>
          </div>
        </div>
      </div>
    );
  }


  // Group slots by Day for display
  const daysList = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];

  return (
    <div className="page-container">
      {/* Header */}
      <div className="page-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <ShieldCheck size={24} style={{ color: "var(--primary)" }} />
            <span className="badge badge-primary" style={{ fontWeight: 600 }}>
              HOD ADMINISTRATION DESK
            </span>
          </div>
          <h2 style={{ marginTop: "0.4rem" }}>Department Command & Timetable Control</h2>
          <p className="lede">
            Configure curriculum timetables via OCR ingestion, review extracted matrices, and monitor department-wide leave workflows.
          </p>
        </div>
        <div className="admin-hod-card panel" style={{ padding: "0.75rem 1rem", minWidth: "220px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
            <img
              src="/faculty/1-VKD.jpg"
              alt="HOD"
              style={{ width: "42px", height: "42px", borderRadius: "50%", objectFit: "cover", border: "2px solid var(--primary)" }}
            />
            <div>
              <div style={{ fontWeight: 600, fontSize: "0.9rem" }}>Dr. Vipul K. Dabhi</div>
              <div className="text-xs muted">Head, IT Department</div>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="notifications-tab-bar panel" style={{ marginBottom: "1.5rem" }}>
        <button
          type="button"
          className={`tab-btn ${activeTab === "timetable" ? "active" : ""}`}
          onClick={() => setActiveTab("timetable")}
        >
          <Calendar size={16} />
          <span>Timetable Ingestion & Review</span>
        </button>
        <button
          type="button"
          className={`tab-btn ${activeTab === "forms" ? "active" : ""}`}
          onClick={() => setActiveTab("forms")}
        >
          <FileText size={16} />
          <span>Department Leave Forms ({allForms.length})</span>
        </button>
        <button
          type="button"
          className={`tab-btn ${activeTab === "notifications" ? "active" : ""}`}
          onClick={() => setActiveTab("notifications")}
        >
          <Mail size={16} />
          <span>Substitute Notifications Log ({allNotifications.length})</span>
        </button>
      </div>

      {/* Alerts */}
      {message && (
        <div className="alert-box success" style={{ marginBottom: "1rem" }}>
          <CheckCircle2 size={18} />
          <span>{message}</span>
        </div>
      )}
      {error && (
        <div className="alert-box error" style={{ marginBottom: "1rem" }}>
          <AlertTriangle size={18} />
          <span>{error}</span>
        </div>
      )}

      {/* TAB 1: TIMETABLE INGESTION */}
      {activeTab === "timetable" && (
        <div>
          {/* Uploader Card */}
          <div className="panel" style={{ padding: "1.5rem", marginBottom: "1.5rem" }}>
            <h3 style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.5rem" }}>
              <Upload size={18} style={{ color: "var(--primary)" }} />
              Upload Official Timetable Image
            </h3>
            <p className="text-sm muted" style={{ marginBottom: "1rem" }}>
              Upload a printed computer timetable sheet. The AI vision model segments table cells, reads lectures/labs, and maps faculty codes.
            </p>

            <div style={{ display: "grid", gridTemplateColumns: "1fr auto", gap: "1.5rem", alignItems: "center" }}>
              <div
                style={{
                  border: "2px dashed var(--border)",
                  borderRadius: "8px",
                  padding: "1.5rem",
                  textAlign: "center",
                  background: "var(--bg-subtle, #fbfbfb)",
                }}
              >
                <input
                  type="file"
                  id="timetable-file-input"
                  accept="image/png,image/jpeg,image/jpg"
                  style={{ display: "none" }}
                  onChange={(e) => setTimetableFile(e.target.files[0] || null)}
                />
                <label htmlFor="timetable-file-input" style={{ cursor: "pointer" }}>
                  <Calendar size={32} style={{ color: "var(--primary)", margin: "0 auto 0.5rem" }} />
                  <div style={{ fontWeight: 600, fontSize: "0.95rem" }}>
                    {timetableFile ? timetableFile.name : "Click to select Timetable Image (PNG / JPG)"}
                  </div>
                  <div className="text-xs muted" style={{ marginTop: "0.25rem" }}>
                    Supports high-resolution scans and official DDU Department timetables
                  </div>
                </label>
              </div>

              <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
                <button
                  type="button"
                  className="btn btn-primary"
                  disabled={!timetableFile || parsing}
                  onClick={handleAnalyzeTimetable}
                  style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}
                >
                  {parsing ? <RefreshCw className="spinner" size={16} /> : <Sparkles size={16} />}
                  <span>{parsing ? "Running AI Vision OCR..." : "Analyze & Extract Grid"}</span>
                </button>

                <div className="text-xs muted" style={{ textAlign: "center", margin: "0.25rem 0" }}>
                  — OR QUICK PRESET —
                </div>

                <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap", justifyContent: "center" }}>
                  <button
                    type="button"
                    className="btn btn-secondary btn-sm"
                    disabled={parsing}
                    onClick={() => handleLoadSample("VII-F")}
                    style={{ display: "inline-flex", alignItems: "center", gap: "6px" }}
                  >
                    <Sparkles size={14} style={{ color: "var(--primary)" }} />
                    Load Preset: Sem 7 Div F (Official IT Timetable)
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* DRAFT REVIEW MATRIX */}
          {draftTimetable && (
            <div className="panel" style={{ padding: "1.5rem", marginBottom: "2rem", border: "2px solid var(--primary)" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
                <div>
                  <span className="badge badge-success" style={{ marginBottom: "0.25rem" }}>
                    EXTRACTED DRAFT MATRIX (HUMAN REVIEW REQUIRED)
                  </span>
                  <h3 style={{ margin: "0.25rem 0" }}>
                    B.Tech. Semester {draftTimetable.semester} — Division {draftTimetable.division} ({draftTimetable.academic_year})
                  </h3>
                  <div className="text-sm muted">
                    Default Room: <strong>{draftTimetable.default_room}</strong> | Total Extracted Slots:{" "}
                    <strong>{draftTimetable.slots?.length || 0}</strong>
                  </div>
                </div>

                <div style={{ display: "flex", gap: "0.75rem", alignItems: "center" }}>
                  <button type="button" className="btn btn-secondary btn-sm" onClick={handleAddSlot}>
                    <Plus size={14} /> Add Slot
                  </button>
                  <button
                    type="button"
                    className="btn btn-secondary btn-sm"
                    onClick={handleDiscardDraft}
                    style={{ display: "flex", alignItems: "center", gap: "0.4rem", color: "var(--danger)" }}
                  >
                    <Trash2 size={14} /> Discard Draft
                  </button>
                  <button
                    type="button"
                    className="btn btn-primary"
                    disabled={saving}
                    onClick={handleCommitTimetable}
                    style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}
                  >
                    {saving ? <RefreshCw className="spinner" size={16} /> : <FileCheck size={16} />}
                    <span>{saving ? "Saving to Database..." : "Commit & Save to Database"}</span>
                  </button>
                </div>
              </div>

              {/* Slot Edit Modal / Form */}
              {editingSlotId && (
                <div
                  className="panel"
                  style={{
                    background: "var(--bg-subtle, #f5f8ff)",
                    padding: "1rem",
                    marginBottom: "1rem",
                    border: "1px solid var(--primary)",
                  }}
                >
                  <div style={{ fontWeight: 600, marginBottom: "0.5rem" }}>Edit Timetable Slot</div>
                  <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(130px, 1fr))", gap: "0.75rem" }}>
                    <div>
                      <label className="text-xs muted">Day</label>
                      <select
                        className="form-control"
                        value={slotForm.day}
                        onChange={(e) => setSlotForm({ ...slotForm, day: e.target.value })}
                      >
                        {daysList.map((d) => (
                          <option key={d} value={d}>
                            {d}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <label className="text-xs muted">Time Slot</label>
                      <input
                        className="form-control"
                        list="slot-presets"
                        placeholder="e.g. 8:30 TO 10:30"
                        value={slotForm.time_slot}
                        onChange={(e) => setSlotForm({ ...slotForm, time_slot: e.target.value })}
                      />
                      <datalist id="slot-presets">
                        <option value="8:30 TO 9:30" />
                        <option value="09:30 TO 10:30" />
                        <option value="8:30 TO 10:30" />
                        <option value="10:45 TO 11:45" />
                        <option value="11:45 TO 12:45" />
                        <option value="10:45 TO 12:45" />
                        <option value="1:30 TO 2:30" />
                        <option value="2:30 TO 3:30" />
                        <option value="1:30 TO 3:30" />
                        <option value="3:30 TO 4:30" />
                        <option value="4:30 TO 5:30" />
                        <option value="3:30 TO 5:30" />
                      </datalist>
                    </div>

                    <div>
                      <label className="text-xs muted">Subject Code</label>
                      <input
                        className="form-control"
                        value={slotForm.subject}
                        onChange={(e) => setSlotForm({ ...slotForm, subject: e.target.value })}
                      />
                    </div>

                    <div>
                      <label className="text-xs muted">Faculty Code</label>
                      <input
                        className="form-control"
                        value={slotForm.faculty_code}
                        onChange={(e) => setSlotForm({ ...slotForm, faculty_code: e.target.value })}
                      />
                    </div>

                    <div>
                      <label className="text-xs muted">Faculty Name</label>
                      <input
                        className="form-control"
                        value={slotForm.faculty_name}
                        onChange={(e) => setSlotForm({ ...slotForm, faculty_name: e.target.value })}
                      />
                    </div>

                    <div>
                      <label className="text-xs muted">Room / Lab</label>
                      <input
                        className="form-control"
                        value={slotForm.room}
                        onChange={(e) => setSlotForm({ ...slotForm, room: e.target.value })}
                      />
                    </div>

                    <div>
                      <label className="text-xs muted">Batch</label>
                      <input
                        className="form-control"
                        value={slotForm.batch}
                        onChange={(e) => setSlotForm({ ...slotForm, batch: e.target.value })}
                      />
                    </div>

                    <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginTop: "1rem" }}>
                      <input
                        type="checkbox"
                        id="is_lab_check"
                        checked={slotForm.is_lab}
                        onChange={(e) => setSlotForm({ ...slotForm, is_lab: e.target.checked })}
                      />
                      <label htmlFor="is_lab_check" className="text-xs" style={{ cursor: "pointer" }}>
                        Is Lab Session
                      </label>
                    </div>
                  </div>

                  <div style={{ display: "flex", gap: "0.5rem", marginTop: "0.75rem" }}>
                    <button type="button" className="btn btn-primary btn-sm" onClick={handleSaveEditSlot}>
                      <Check size={14} /> Update Slot
                    </button>
                    <button
                      type="button"
                      className="btn btn-secondary btn-sm"
                      onClick={() => setEditingSlotId(null)}
                    >
                      <X size={14} /> Cancel
                    </button>
                  </div>
                </div>
              )}

              {/* Matrix Table */}
              <div className="table-responsive">
                <table className="data-table" style={{ fontSize: "0.85rem" }}>
                  <thead>
                    <tr>
                      <th>Day</th>
                      <th>Time Slot</th>
                      <th>Subject</th>
                      <th>Faculty</th>
                      <th>Room / Lab</th>
                      <th>Batch</th>
                      <th>Type</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {draftTimetable.slots.map((s) => (
                      <tr key={s.id}>
                        <td>
                          <strong>{s.day}</strong>
                        </td>
                        <td>{s.time_slot}</td>
                        <td>
                          <strong>{s.subject}</strong>
                          {s.subject_name && s.subject_name !== s.subject && (
                            <div className="text-xs muted">{s.subject_name}</div>
                          )}
                        </td>
                        <td>
                          <span className="badge badge-secondary" style={{ marginRight: "0.25rem" }}>
                            {s.faculty_code}
                          </span>
                          <span>{s.faculty_name}</span>
                        </td>
                        <td>
                          <span style={{ display: "flex", alignItems: "center", gap: "0.25rem" }}>
                            <MapPin size={12} className="muted" />
                            {s.room}
                          </span>
                        </td>
                        <td>
                          <span className="badge badge-outline">{s.batch || "ALL"}</span>
                        </td>
                        <td>
                          {s.is_lab ? (
                            <span className="badge badge-warning">Lab</span>
                          ) : (
                            <span className="badge badge-primary">Lecture</span>
                          )}
                        </td>
                        <td>
                          <div style={{ display: "flex", gap: "0.25rem" }}>
                            <button
                              type="button"
                              className="btn btn-icon btn-sm"
                              title="Edit slot"
                              onClick={() => handleStartEditSlot(s)}
                            >
                              <Edit2 size={13} />
                            </button>
                            <button
                              type="button"
                              className="btn btn-icon btn-sm"
                              title="Delete slot"
                              onClick={() => handleDeleteSlot(s.id)}
                            >
                              <Trash2 size={13} style={{ color: "var(--danger)" }} />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* STORED TIMETABLES REPOSITORY (GROUPED IMAGE-WISE / CLASS-WISE) */}
          <div className="panel" style={{ padding: "1.5rem" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.25rem", flexWrap: "wrap", gap: "1rem" }}>
              <div>
                <h3 style={{ display: "flex", alignItems: "center", gap: "0.5rem", margin: 0 }}>
                  <Layers size={20} style={{ color: "var(--primary)" }} />
                  Committed Department Timetables (Image-Wise)
                </h3>
                <p className="text-sm muted" style={{ marginTop: "0.25rem" }}>
                  Active timetables grouped image-wise by class ({timetableGroups.length} timetable{timetableGroups.length === 1 ? "" : "s"}, {storedSlots.length} total slots). You can delete any specific timetable without affecting other classes.
                </p>
              </div>

              <div style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
                <button
                  type="button"
                  className="btn btn-secondary btn-sm"
                  onClick={loadStoredTimetables}
                  title="Refresh timetables"
                >
                  <RefreshCw size={14} /> Refresh
                </button>
              </div>
            </div>

            {loadingStored ? (
              <div className="loading-state">
                <RefreshCw className="spinner" size={24} />
                <p>Loading database timetable records...</p>
              </div>
            ) : timetableGroups.length === 0 ? (
              <div className="empty-state-panel" style={{ textAlign: "center", padding: "2.5rem 1rem", border: "1px dashed var(--border-color, #ccc)", borderRadius: "8px" }}>
                <Calendar size={40} className="muted" style={{ margin: "0 auto 0.75rem", opacity: 0.6 }} />
                <h4>No Committed Timetables Found</h4>
                <p className="text-sm muted" style={{ maxWidth: "480px", margin: "0.25rem auto 1.25rem auto" }}>
                  The timetable repository is empty. Upload a timetable image above or load the single official preset (Sem 7 Div F) to activate schedules.
                </p>
                <button
                  type="button"
                  className="btn btn-primary btn-sm"
                  onClick={() => handleLoadSample("VII-F")}
                  style={{ display: "inline-flex", alignItems: "center", gap: "6px" }}
                >
                  <Sparkles size={14} /> Load Preset: Sem 7 Div F
                </button>
              </div>
            ) : (
              <div className="timetables-group-list" style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
                {timetableGroups.map((group) => {
                  const isExpanded = !!expandedTimetableKeys[group.key];
                  const otherClasses = timetableGroups
                    .filter((g) => g.key !== group.key)
                    .map((g) => `Sem ${g.semester} Div ${g.division}`)
                    .join(", ");

                  return (
                    <div
                      key={group.key}
                      className="timetable-image-group panel"
                      style={{
                        padding: "1.25rem",
                        border: "1px solid var(--border-color, #e0e0e0)",
                        borderRadius: "10px",
                        background: "#ffffff",
                        boxShadow: "0 1px 4px rgba(0,0,0,0.04)",
                      }}
                    >
                      <div
                        style={{
                          display: "flex",
                          justifyContent: "space-between",
                          alignItems: "center",
                          flexWrap: "wrap",
                          gap: "1rem",
                        }}
                      >
                        <div>
                          <div style={{ display: "flex", alignItems: "center", gap: "0.6rem", flexWrap: "wrap" }}>
                            <Calendar size={18} style={{ color: "var(--primary)" }} />
                            <h4 style={{ margin: 0, fontSize: "1.1rem", fontWeight: 700 }}>
                              Timetable: Semester {group.semester} — Division {group.division}
                            </h4>
                            <span className="badge badge-primary">{group.slots.length} Slots</span>
                            <span className="badge badge-outline">{group.academic_year}</span>
                          </div>
                          <div
                            className="text-xs muted"
                            style={{ display: "flex", gap: "1.25rem", flexWrap: "wrap", marginTop: "0.5rem" }}
                          >
                            <span>
                              <strong>Rooms / Labs:</strong> {group.rooms ? Array.from(group.rooms).join(", ") : "N/A"}
                            </span>
                            <span>
                              <strong>Subjects ({group.subjects?.size || 0}):</strong>{" "}
                              {group.subjects ? Array.from(group.subjects).slice(0, 5).join(", ") : "None"}
                              {(group.subjects?.size || 0) > 5 ? "..." : ""}
                            </span>
                            <span>
                              <strong>Faculty ({group.faculties?.size || 0}):</strong> {group.faculties?.size || 0} instructors
                            </span>
                          </div>
                        </div>

                        <div style={{ display: "flex", gap: "0.6rem", alignItems: "center", flexWrap: "wrap" }}>
                          <button
                            type="button"
                            className="btn btn-secondary btn-sm"
                            onClick={() => toggleTimetableExpand(group.key)}
                            style={{ display: "inline-flex", alignItems: "center", gap: "6px" }}
                          >
                            <Eye size={14} />
                            {isExpanded ? "Hide Slots Grid" : "View Slots Grid"}
                          </button>

                          <button
                            type="button"
                            className="btn btn-secondary btn-sm"
                            onClick={() =>
                              handleDeleteSingleTimetable(
                                group.semester,
                                group.division,
                                group.slots.length,
                                otherClasses
                              )
                            }
                            style={{
                              display: "inline-flex",
                              alignItems: "center",
                              gap: "6px",
                              color: "#d32f2f",
                              borderColor: "#ffcdd2",
                              background: "#fff5f5",
                              fontWeight: 600,
                            }}
                            title={`Delete ONLY Sem ${group.semester} Div ${group.division}`}
                          >
                            <Trash2 size={14} />
                            Delete This Timetable
                          </button>
                        </div>
                      </div>

                      {/* Expanded Slots Grid for this single timetable */}
                      {isExpanded && (
                        <div style={{ marginTop: "1.25rem", paddingTop: "1rem", borderTop: "1px solid #f0f0f0" }}>
                          <div className="table-responsive">
                            <table className="data-table" style={{ fontSize: "0.85rem" }}>
                              <thead>
                                <tr>
                                  <th>Day</th>
                                  <th>Time Slot</th>
                                  <th>Subject</th>
                                  <th>Faculty</th>
                                  <th>Room / Lab</th>
                                  <th>Batch</th>
                                  <th>Type</th>
                                </tr>
                              </thead>
                              <tbody>
                                {group.slots.map((slot) => (
                                  <tr key={slot.id}>
                                    <td>
                                      <strong>{slot.day}</strong>
                                    </td>
                                    <td>{slot.time_slot}</td>
                                    <td>
                                      <strong>{slot.subject}</strong>
                                    </td>
                                    <td>
                                      <span className="badge badge-secondary" style={{ marginRight: "0.25rem" }}>
                                        {slot.faculty_code}
                                      </span>
                                      <span>{slot.faculty_name}</span>
                                    </td>
                                    <td>
                                      <span style={{ display: "flex", alignItems: "center", gap: "0.25rem" }}>
                                        <MapPin size={12} className="muted" />
                                        {slot.room}
                                      </span>
                                    </td>
                                    <td>
                                      <span className="badge badge-outline">{slot.batch}</span>
                                    </td>
                                    <td>
                                      {slot.is_lab ? (
                                        <span className="badge badge-warning">Lab</span>
                                      ) : (
                                        <span className="badge badge-primary">Lecture</span>
                                      )}
                                    </td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      )}

      {/* TAB 2: DEPARTMENT LEAVE FORMS */}
      {activeTab === "forms" && (
        <div className="panel" style={{ padding: "1.5rem" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
            <div>
              <h3>All Department Leave Applications</h3>
              <p className="text-sm muted">Department-wide oversight of faculty leave forms and substitution workflows.</p>
            </div>
            <button type="button" className="btn btn-secondary btn-sm" onClick={loadDepartmentForms}>
              <RefreshCw size={14} /> Refresh
            </button>
          </div>

          {loadingForms ? (
            <div className="loading-state">
              <RefreshCw className="spinner" size={24} />
              <p>Loading department forms...</p>
            </div>
          ) : allForms.length === 0 ? (
            <div className="empty-state-panel" style={{ textAlign: "center", padding: "2rem" }}>
              <FileText size={40} className="muted" style={{ margin: "0 auto 0.5rem" }} />
              <h4>No Leave Applications in Department</h4>
            </div>
          ) : (
            <div className="table-responsive">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Applicant Faculty</th>
                    <th>Application Date</th>
                    <th>Status</th>
                    <th>Arrangement Rows</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {allForms.map((form) => (
                    <tr key={form.id}>
                      <td>
                        <strong>{form.applicant_name}</strong>
                        <div className="text-xs muted">{form.original_filename}</div>
                      </td>
                      <td>{form.created_at ? new Date(form.created_at).toLocaleDateString() : "—"}</td>
                      <td>
                        <span className={`badge badge-${form.status?.toLowerCase()}`}>
                          {form.status}
                        </span>
                      </td>
                      <td>
                        <span className="badge badge-outline">
                          {form.assignments?.length || 0} rows
                        </span>
                      </td>
                      <td>
                        <Link to={`/review/${form.id}`} className="btn btn-secondary btn-sm">
                          <Eye size={13} /> View & Review
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* TAB 3: SUBSTITUTE NOTIFICATIONS LOG */}
      {activeTab === "notifications" && (
        <div className="panel" style={{ padding: "1.5rem" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
            <div>
              <h3>Department Substitute Notifications Dispatch Log</h3>
              <p className="text-sm muted">Track all queued and dispatched substitute arrangement emails across all faculty.</p>
            </div>
            <button type="button" className="btn btn-secondary btn-sm" onClick={loadDepartmentNotifications}>
              <RefreshCw size={14} /> Refresh
            </button>
          </div>

          {loadingNotifs ? (
            <div className="loading-state">
              <RefreshCw className="spinner" size={24} />
              <p>Loading notification dispatch logs...</p>
            </div>
          ) : allNotifications.length === 0 ? (
            <div className="empty-state-panel" style={{ textAlign: "center", padding: "2rem" }}>
              <Mail size={40} className="muted" style={{ margin: "0 auto 0.5rem" }} />
              <h4>No Dispatched Notifications</h4>
              <p className="text-sm muted">Dispatched substitute requests will appear here with delivery timestamps.</p>
            </div>
          ) : (
            <div className="table-responsive">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Substitute Faculty</th>
                    <th>Recipient Email</th>
                    <th>Classes Covered</th>
                    <th>Status</th>
                    <th>Dispatched Timestamp</th>
                  </tr>
                </thead>
                <tbody>
                  {allNotifications.map((notif) => (
                    <tr key={notif.id}>
                      <td>
                        <strong>{notif.substitute_name || "Faculty Member"}</strong>
                      </td>
                      <td>{notif.to_email}</td>
                      <td>
                        <span className="badge badge-outline">
                          {notif.assignment_count} arrangements
                        </span>
                      </td>
                      <td>
                        <span className={`badge badge-${notif.status?.toLowerCase()}`}>
                          {notif.status}
                        </span>
                      </td>
                      <td>
                        {notif.sent_at ? (
                          <span style={{ display: "flex", alignItems: "center", gap: "0.25rem" }}>
                            <Clock size={12} className="muted" />
                            {new Date(notif.sent_at).toLocaleString()}
                          </span>
                        ) : (
                          <span className="muted text-xs">Pending dispatch</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
