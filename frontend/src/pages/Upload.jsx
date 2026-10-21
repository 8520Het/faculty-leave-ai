import { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { api, poll } from "../api";
import { useAuth } from "../context/AuthContext";
import {
  UploadCloud,
  FileCheck,
  Image as ImageIcon,
  CheckCircle,
  AlertCircle,
  Loader2,
  Sparkles,
  Layers,
  Cpu,
  Mail,
  User,
  Calendar,
} from "lucide-react";

const PIPELINE_STEPS = [
  { id: 1, title: "Image Upload & Normalization", desc: "Preprocessing and deskewing image", icon: Layers },
  { id: 2, title: "Table Detection & Cell Segmentation", desc: "Finding grid boundaries and extracting rows", icon: ImageIcon },
  { id: 3, title: "TrOCR Handwriting Recognition", desc: "Transformer vision model decoding cursive handwriting", icon: Cpu },
  { id: 4, title: "Academic Master & Timetable Validation", desc: "Verifying subject codes, active slots, and rooms", icon: Calendar },
  { id: 5, title: "Substitute Matching & Notification Generation", desc: "Fuzzy matching faculty and drafting notification emails", icon: Mail },
];

export default function Upload() {
  const navigate = useNavigate();
  const { faculty } = useAuth();

  const [file, setFile] = useState(null);
  const [filePreview, setFilePreview] = useState(null);
  const [applicantName, setApplicantName] = useState(faculty?.name || "");
  const [year, setYear] = useState(2026);
  const [demo, setDemo] = useState(false);
  const [busy, setBusy] = useState(false);
  const [activeStep, setActiveStep] = useState(0);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef(null);

  function handleFileChange(selectedFile) {
    if (!selectedFile) return;
    setFile(selectedFile);
    setError("");
    const reader = new FileReader();
    reader.onload = (e) => setFilePreview(e.target.result);
    reader.readAsDataURL(selectedFile);
  }

  function handleDrag(e) {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }

  function handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileChange(e.dataTransfer.files[0]);
    }
  }

  async function waitForForm(id) {
    let stepInterval = setInterval(() => {
      setActiveStep((prev) => (prev < 4 ? prev + 1 : prev));
    }, 2500);

    try {
      const form = await poll(() => api.form(id), {
        until: (value) =>
          ["NEEDS_REVIEW", "NOTIFIED", "FAILED"].includes(value.status) ||
          (value.assignment_count > 0 &&
            value.status !== "PROCESSING" &&
            value.status !== "QUEUED"),
      });
      clearInterval(stepInterval);
      setActiveStep(5);
      return form;
    } catch (err) {
      clearInterval(stepInterval);
      throw err;
    }
  }

  async function onSubmit(event) {
    event.preventDefault();
    setError("");
    setBusy(true);
    setActiveStep(1);
    setMessage("Uploading form and initializing AI pipeline...");

    try {
      if (!file && !demo) {
        throw new Error("Please select or drop a JPG/PNG leave arrangement image.");
      }

      let uploaded;
      if (demo && !file) {
        setMessage("Starting Demo pipeline simulation...");
        uploaded = await api.demo(applicantName, year);
      } else {
        uploaded = await api.upload({
          file,
          applicantName,
          year,
          processNow: true,
          demo,
        });
      }

      setMessage("AI OCR processing and timetable cross-referencing in progress...");
      const finished = await waitForForm(uploaded.id);

      if (finished.status === "FAILED") {
        throw new Error(finished.error_message || "Form processing failed");
      }

      setMessage("Scan successful! Opening results and notification center...");
      setTimeout(() => {
        navigate(`/review/${finished.id}`);
      }, 800);
    } catch (err) {
      setError(err.message);
      setBusy(false);
      setActiveStep(0);
    }
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <h2>Submit Faculty Leave Form</h2>
        <p className="lede">
          Upload your signed leave arrangement sheet. The AI will extract your handwritten
          lecture slots, match substitute faculty, and prepare automated notifications.
        </p>
      </div>

      {faculty && (
        <div className="faculty-identity-banner">
          <div className="identity-avatar-wrap">
            <img
              src={
                faculty.avatar ||
                `https://ui-avatars.com/api/?name=${encodeURIComponent(faculty.name)}&background=0284c7&color=fff`
              }
              alt={faculty.name}
              className="identity-avatar"
            />
          </div>
          <div className="identity-text">
            <span className="identity-tag">Filing as Registered Faculty</span>
            <h4 className="identity-name">{faculty.name}</h4>
            <p className="identity-email">{faculty.email} · {faculty.department || "IT Dept"}</p>
          </div>
          <button
            type="button"
            className="button secondary sm identity-change-btn"
            onClick={() => setApplicantName(faculty.name)}
          >
            Apply My Identity
          </button>
        </div>
      )}

      <div className="upload-layout-grid">
        <form className="panel upload-form-card" onSubmit={onSubmit}>
          <div
            className={`dropzone-card ${dragActive ? "drag-active" : ""} ${
              filePreview ? "has-preview" : ""
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              ref={fileInputRef}
              id="file"
              type="file"
              accept="image/png,image/jpeg,image/jpg"
              style={{ display: "none" }}
              onChange={(e) => handleFileChange(e.target.files[0])}
            />

            {filePreview ? (
              <div className="preview-container">
                <img src={filePreview} alt="Form preview" className="uploaded-preview-img" />
                <div className="preview-overlay">
                  <p className="preview-name">{file.name}</p>
                  <span className="badge ok">Ready to Scan</span>
                  <p className="preview-change-hint">Click or drag a new image to change</p>
                </div>
              </div>
            ) : (
              <div className="dropzone-empty">
                <div className="upload-icon-circle">
                  <UploadCloud size={32} />
                </div>
                <h4 className="dropzone-title">Drag & drop your leave form image</h4>
                <p className="dropzone-subtitle">Supports JPG, JPEG, and PNG document scans</p>
                <button type="button" className="button secondary sm">
                  Browse Device Files
                </button>
              </div>
            )}
          </div>

          <div className="form-controls-grid">
            <div>
              <label htmlFor="applicantName">
                <User size={14} style={{ display: "inline", marginRight: "4px" }} />
                Applicant Faculty (Authenticated Account)
              </label>
              <input
                id="applicantName"
                value={faculty?.name || applicantName}
                readOnly
                style={{ backgroundColor: "var(--panel-bg)", cursor: "not-allowed" }}
                placeholder="Logged in faculty name"
                required
              />
              <span className="text-xs muted" style={{ display: "block", marginTop: "4px" }}>
                🔒 Locked to your session ({faculty?.email}). Form's "Name in Full" will be validated against this.
              </span>
            </div>

            <div>
              <label htmlFor="year">
                <Calendar size={14} style={{ display: "inline", marginRight: "4px" }} />
                Academic Year
              </label>
              <input
                id="year"
                type="number"
                value={year}
                onChange={(e) => setYear(Number(e.target.value))}
                min="2020"
                max="2035"
                required
              />
            </div>
          </div>

          <div className="demo-toggle-card">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={demo}
                onChange={(e) => setDemo(e.target.checked)}
                className="checkbox-input"
              />
              <div>
                <span className="checkbox-title">
                  <Sparkles size={14} className="sparkle-icon" /> Fast Demo Mode (Instant Simulation)
                </span>
                <p className="checkbox-desc">
                  Simulates TrOCR extraction with pre-validated handwritten rows (useful for fast testing without GPU delays).
                </p>
              </div>
            </label>
          </div>

          <div className="upload-action-row">
            <button
              type="submit"
              className="button primary lg full-width"
              disabled={busy || (!file && !demo)}
            >
              {busy ? (
                <>
                  <Loader2 size={18} className="spinner" />
                  Processing Form with AI...
                </>
              ) : (
                <>
                  <FileCheck size={18} />
                  Upload & Run OCR Scan
                </>
              )}
            </button>
          </div>

          {error && (
            <div className="alert-box error">
              <AlertCircle size={18} />
              <span>{error}</span>
            </div>
          )}
          {message && (
            <div className="alert-box info">
              <Loader2 size={16} className="spinner" />
              <span>{message}</span>
            </div>
          )}
        </form>

        <div className="panel pipeline-progress-card">
          <h3>AI Processing Pipeline</h3>
          <p className="text-sm muted" style={{ marginBottom: "1.2rem" }}>
            The arrangement table undergoes a 5-stage computer vision & language pipeline:
          </p>

          <div className="pipeline-steps-list">
            {PIPELINE_STEPS.map((st) => {
              const Icon = st.icon;
              const isDone = activeStep > st.id;
              const isCurrent = activeStep === st.id;

              return (
                <div
                  key={st.id}
                  className={`pipeline-step-item ${isDone ? "done" : ""} ${
                    isCurrent ? "active" : ""
                  }`}
                >
                  <div className="step-indicator">
                    {isDone ? (
                      <CheckCircle size={18} className="step-done-icon" />
                    ) : isCurrent ? (
                      <Loader2 size={18} className="spinner step-current-icon" />
                    ) : (
                      <Icon size={16} />
                    )}
                  </div>
                  <div className="step-info">
                    <h5 className="step-title">{st.title}</h5>
                    <p className="step-desc">{st.desc}</p>
                  </div>
                </div>
              );
            })}
          </div>

          <div className="pipeline-tip-box">
            <span className="tip-badge">Resultant Notification</span>
            <p className="text-xs muted" style={{ margin: 0 }}>
              Once scanned, substitute faculty members will receive lecture takeover summaries
              ready for instant notification dispatch.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
