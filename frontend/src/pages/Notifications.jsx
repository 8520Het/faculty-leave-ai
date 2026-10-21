import { useEffect, useState } from "react";
import { api } from "../api";
import { useAuth } from "../context/AuthContext";
import {
  Bell,
  Mail,
  CheckCircle2,
  Clock,
  Send,
  User,
  Calendar,
  Layers,
  Inbox,
  Check,
  RefreshCw,
  ExternalLink,
} from "lucide-react";

export default function Notifications() {
  const { faculty, isAdmin, refreshNotifications } = useAuth();
  const [tab, setTab] = useState("my-inbox"); // 'my-inbox' | 'all-dispatched'
  const [inboxNotifications, setInboxNotifications] = useState([]);
  const [allEmails, setAllEmails] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionMessage, setActionMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    loadData();

    // Live background polling so substitute faculty in Browser 2 sees the notification instantly
    const timer = setInterval(() => {
      if (faculty?.email) {
        Promise.all([
          api.emails({
            faculty_email: faculty.email,
            faculty_name: faculty.name,
            is_admin: isAdmin,
          }),
          api.facultyNotifications(faculty.email),
        ])
          .then(([allList, facultyRes]) => {
            setAllEmails(allList || []);
            setInboxNotifications(facultyRes?.notifications || []);
          })
          .catch(() => {});
      }
    }, 2500);

    return () => clearInterval(timer);
  }, [faculty?.email, isAdmin]);

  async function loadData() {
    setLoading(true);
    setError("");
    try {
      const [allList, facultyRes] = await Promise.all([
        api.emails({
          faculty_email: faculty?.email,
          faculty_name: faculty?.name,
          is_admin: isAdmin,
        }),
        faculty?.email ? api.facultyNotifications(faculty.email) : Promise.resolve({ notifications: [] }),
      ]);
      setAllEmails(allList || []);
      setInboxNotifications(facultyRes?.notifications || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleAcknowledge(emailId) {
    try {
      await api.acknowledgeNotification(emailId);
      setActionMessage("Arrangement acknowledged! Status updated.");
      setTimeout(() => setActionMessage(""), 3000);
      loadData();
      refreshNotifications();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <h2>Faculty Notification Desk</h2>
        <p className="lede">
          {isAdmin
            ? "Administrative oversight of substitute arrangement notifications department-wide."
            : "Review lecture substitution requests assigned to you or dispatched for your classes."}
        </p>
      </div>

      <div className="notifications-tab-bar panel">
        <button
          type="button"
          className={`tab-btn ${tab === "my-inbox" ? "active" : ""}`}
          onClick={() => setTab("my-inbox")}
        >
          <Inbox size={16} />
          <span>My Incoming Substitution Inbox ({inboxNotifications.length})</span>
        </button>
        <button
          type="button"
          className={`tab-btn ${tab === "all-dispatched" ? "active" : ""}`}
          onClick={() => setTab("all-dispatched")}
        >
          <Mail size={16} />
          <span>
            {isAdmin
              ? `All Department Notifications (${allEmails.length})`
              : `My Dispatched Notifications (${allEmails.length})`}
          </span>
        </button>
      </div>


      {actionMessage && (
        <div className="alert-box success">
          <CheckCircle2 size={18} />
          <span>{actionMessage}</span>
        </div>
      )}
      {error && (
        <div className="alert-box error">
          <span>{error}</span>
        </div>
      )}

      {loading ? (
        <div className="loading-state">
          <RefreshCw className="spinner" size={24} />
          <p>Loading notification registry...</p>
        </div>
      ) : tab === "my-inbox" ? (
        <div className="inbox-content-section">
          {inboxNotifications.length === 0 ? (
            <div className="panel empty-state-panel">
              <Inbox size={48} className="empty-icon" />
              <h3>No Incoming Substitution Requests</h3>
              <p className="text-sm muted">
                There are currently no active lecture substitutions assigned to{" "}
                <strong>{faculty?.name || "your account"}</strong> ({faculty?.email}).
              </p>
              <p className="text-xs muted" style={{ marginTop: "1rem" }}>
                Tip: You can switch faculty profile in the top-right header to check other professors
                (e.g. Prof. Sandeep R. Suthar).
              </p>
            </div>
          ) : (
            <div className="notifications-grid">
              {inboxNotifications.map((notif) => {
                const isAck = notif.status === "ACKNOWLEDGED";
                return (
                  <article key={notif.id} className="panel notification-card-full">
                    <div className="notif-top-row">
                      <div className="notif-sender-info">
                        <div className="notif-avatar-icon">
                          <Bell size={20} />
                        </div>
                        <div>
                          <h4 className="notif-heading">{notif.subject}</h4>
                          <span className="notif-recipient-tag">
                            Sent to: {notif.to} · {notif.assignment_count} Lecture Slot(s)
                          </span>
                        </div>
                      </div>

                      <div className="notif-badge-wrap">
                        {isAck ? (
                          <span className="badge ok">
                            <CheckCircle2 size={13} style={{ marginRight: "3px" }} />
                            Acknowledged by You
                          </span>
                        ) : notif.status === "SENT" ? (
                          <span className="badge ok">
                            <Check size={13} style={{ marginRight: "3px" }} />
                            Notification Dispatched
                          </span>
                        ) : (
                          <span className="badge warn">
                            <Clock size={13} style={{ marginRight: "3px" }} />
                            Pending Dispatch
                          </span>
                        )}
                      </div>
                    </div>

                    <div className="notif-email-view">
                      <pre>{notif.body}</pre>
                    </div>

                    <div className="notif-bottom-row">
                      <div className="notif-timestamp-tag">
                        <Clock size={13} />
                        <span>
                          Generated:{" "}
                          {notif.generated_at
                            ? new Date(notif.generated_at).toLocaleString()
                            : "Recently"}
                        </span>
                      </div>

                      {!isAck && (
                        <button
                          type="button"
                          className="button primary sm"
                          onClick={() => handleAcknowledge(notif.id)}
                        >
                          <Check size={15} /> Acknowledge Substitution
                        </button>
                      )}
                    </div>
                  </article>
                );
              })}
            </div>
          )}
        </div>
      ) : (
        <div className="all-notifications-section">
          {allEmails.length === 0 ? (
            <div className="panel empty-state-panel">
              <p className="text-sm muted">No notification logs recorded yet.</p>
            </div>
          ) : (
            <div className="notifications-grid">
              {allEmails.map((email) => (
                <article key={email.id} className="panel notification-card-full">
                  <div className="notif-top-row">
                    <div>
                      <h4 className="notif-heading">{email.subject}</h4>
                      <p className="text-xs muted">
                        Recipient: <strong>{email.substitute_name}</strong> ({email.to}) ·{" "}
                        {email.assignment_count} lecture(s)
                      </p>
                    </div>

                    <span
                      className={`badge ${
                        email.status === "SENT" || email.status === "ACKNOWLEDGED" ? "ok" : "warn"
                      }`}
                    >
                      {email.status || "QUEUED"}
                    </span>
                  </div>

                  <div className="notif-email-view">
                    <pre>{email.body}</pre>
                  </div>
                </article>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
