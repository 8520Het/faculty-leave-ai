import { useEffect, useState } from "react";
import { api } from "../api";

export default function Emails() {
  const [emails, setEmails] = useState([]);
  const [forms, setForms] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([api.emails(), api.forms()])
      .then(([mail, formList]) => {
        setEmails(mail);
        setForms(formList);
      })
      .catch((err) => setError(err.message));
  }, []);

  return (
    <section>
      <h2>Grouped emails</h2>
      <p className="lede">
        One preview is produced per substitute. These are drafts only; the MVP
        does not send mail.
      </p>
      {error && <p className="error">{error}</p>}
      {emails.length === 0 && <p className="muted">No email previews yet. Review a form first.</p>}
      {emails.map((email) => (
        <article className="panel" key={email.id}>
          <h3>{email.subject}</h3>
          <p>
            To: {email.to} · {email.assignment_count} lecture(s)
          </p>
          <pre className="preview">{email.body}</pre>
        </article>
      ))}
      <div className="panel">
        <h3>Forms</h3>
        <ul>
          {forms.map((form) => (
            <li key={form.id}>
              {form.applicant_name} — {form.email_count} email(s) — {form.status}
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
