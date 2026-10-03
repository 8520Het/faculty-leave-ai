import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, poll } from "../api";

export default function Upload() {
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [applicantName, setApplicantName] = useState("Anand K. Patel");
  const [year, setYear] = useState(2026);
  const [demo, setDemo] = useState(false);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  async function waitForForm(id) {
    const form = await poll(() => api.form(id), {
      until: (value) =>
        ["NEEDS_REVIEW", "FAILED"].includes(value.status) ||
        (value.assignment_count > 0 && value.status !== "PROCESSING" && value.status !== "QUEUED"),
    });
    return form;
  }

  async function onSubmit(event) {
    event.preventDefault();
    setError("");
    setMessage("Uploading and queuing processing…");
    setBusy(true);
    try {
      if (!file) {
        throw new Error("Choose a JPG or PNG leave-form image.");
      }
      const uploaded = await api.upload({
        file,
        applicantName,
        year,
        processNow: true,
        demo,
      });
      setMessage("Processing the arrangement table. This can take several minutes if TrOCR is enabled.");
      const finished = await waitForForm(uploaded.id);
      if (finished.status === "FAILED") {
        throw new Error(finished.error_message || "Processing failed");
      }
      navigate(`/review/${finished.id}`);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  async function runDemo() {
    setError("");
    setBusy(true);
    setMessage("Loading demo assignments…");
    try {
      const created = await api.demo(applicantName, year);
      const finished = await waitForForm(created.id);
      navigate(`/review/${finished.id}`);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <section>
      <h2>Upload a leave form</h2>
      <p className="lede">
        Use a photo or scan of the faculty leave arrangement sheet. The desk
        looks for the handwritten assignment table, not arbitrary documents.
      </p>
      <form className="panel" onSubmit={onSubmit}>
        <label htmlFor="file">Form image</label>
        <input
          id="file"
          type="file"
          accept="image/png,image/jpeg"
          onChange={(event) => setFile(event.target.files[0])}
        />
        <label htmlFor="name">Applicant name</label>
        <input
          id="name"
          value={applicantName}
          onChange={(event) => setApplicantName(event.target.value)}
        />
        <label htmlFor="year">Academic year used for dates</label>
        <input
          id="year"
          type="number"
          value={year}
          onChange={(event) => setYear(event.target.value)}
        />
        <label>
          <input
            type="checkbox"
            checked={demo}
            onChange={(event) => setDemo(event.target.checked)}
            style={{ width: "auto", marginRight: "0.5rem" }}
          />
          Skip OCR and attach demo rows (useful without TrOCR)
        </label>
        <div className="row">
          <button type="submit" disabled={busy}>
            {busy ? "Working…" : "Upload and process"}
          </button>
          <button type="button" className="secondary" onClick={runDemo} disabled={busy}>
            Run demo without an image
          </button>
        </div>
        {message && <p className="muted">{message}</p>}
        {error && <p className="error">{error}</p>}
      </form>
    </section>
  );
}
