import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import { useAuth } from "../context/AuthContext";
import {
  Calendar,
  Clock,
  MapPin,
  BookOpen,
  Users,
  RefreshCw,
  Printer,
  Sparkles,
  ChevronRight,
  Shield,
  Layers,
} from "lucide-react";

export default function MySchedule() {
  const { faculty, isAdmin } = useAuth();
  const [schedule, setSchedule] = useState([]);
  const [selectedDay, setSelectedDay] = useState("ALL");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const daysList = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];

  useEffect(() => {
    loadSchedule();
  }, [faculty?.email, faculty?.name]);

  async function loadSchedule() {
    if (!faculty) return;
    setLoading(true);
    setError("");
    try {
      const res = await api.mySchedule({
        faculty_email: faculty.email,
        faculty_name: faculty.name,
      });
      setSchedule(res?.schedule || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  // Filter schedule by day
  const filteredSchedule = schedule.filter((item) => {
    if (selectedDay !== "ALL" && item.day !== selectedDay) return false;
    return true;
  });

  // Group by day for organized week view
  const groupedByDay = daysList.reduce((acc, day) => {
    acc[day] = schedule.filter((item) => item.day === day);
    return acc;
  }, {});

  return (
    <div className="page-container">
      {/* Header */}
      <div className="page-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "1rem" }}>
        <div>
          <h2>My Teaching Schedule</h2>
          <p className="lede">
            Official departmental timetable for your lectures and laboratory assignments.
          </p>
        </div>

        <div style={{ display: "flex", gap: "0.5rem" }}>
          {isAdmin && (
            <Link to="/admin" className="btn btn-secondary btn-sm" style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}>
              <Shield size={14} style={{ color: "var(--primary)" }} />
              <span>Admin Timetable Desk</span>
            </Link>
          )}
          <button
            type="button"
            className="btn btn-secondary btn-sm"
            onClick={() => window.print()}
            style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}
          >
            <Printer size={14} />
            <span>Print Schedule</span>
          </button>
          <button
            type="button"
            className="btn btn-secondary btn-sm"
            onClick={loadSchedule}
            title="Refresh schedule"
          >
            <RefreshCw size={14} />
          </button>
        </div>
      </div>

      {/* Faculty Profile Strip */}
      <div className="panel" style={{ padding: "1.25rem", marginBottom: "1.5rem", background: "var(--bg-subtle, #fcfcfc)" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "1rem", flexWrap: "wrap" }}>
          <img
            src={faculty?.avatar || "/faculty/2-HBP.jpg"}
            alt={faculty?.name}
            style={{
              width: "56px",
              height: "56px",
              borderRadius: "50%",
              objectFit: "cover",
              border: "3px solid var(--primary)",
            }}
          />
          <div style={{ flex: 1, minWidth: "200px" }}>
            <h3 style={{ margin: 0, fontSize: "1.15rem" }}>{faculty?.name}</h3>
            <div className="text-sm muted" style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap", marginTop: "0.25rem" }}>
              <span>{faculty?.designation}</span>
              <span>•</span>
              <span>Department of {faculty?.department}</span>
              <span>•</span>
              <span>{faculty?.email}</span>
            </div>
          </div>
          <div style={{ textAlign: "right" }}>
            <span className="badge badge-primary" style={{ fontSize: "0.9rem", padding: "0.4rem 0.8rem" }}>
              {schedule.length} Weekly Sessions
            </span>
          </div>
        </div>
      </div>

      {/* Filter Tabs by Day */}
      <div className="notifications-tab-bar panel" style={{ marginBottom: "1.5rem" }}>
        <button
          type="button"
          className={`tab-btn ${selectedDay === "ALL" ? "active" : ""}`}
          onClick={() => setSelectedDay("ALL")}
        >
          <span>All Days ({schedule.length})</span>
        </button>
        {daysList.map((day) => {
          const count = groupedByDay[day]?.length || 0;
          return (
            <button
              key={day}
              type="button"
              className={`tab-btn ${selectedDay === day ? "active" : ""}`}
              onClick={() => setSelectedDay(day)}
            >
              <span>
                {day.slice(0, 3)} ({count})
              </span>
            </button>
          );
        })}
      </div>

      {error && (
        <div className="alert-box error" style={{ marginBottom: "1rem" }}>
          <span>{error}</span>
        </div>
      )}

      {loading ? (
        <div className="loading-state">
          <RefreshCw className="spinner" size={24} />
          <p>Loading personal schedule from department timetable...</p>
        </div>
      ) : schedule.length === 0 ? (
        <div className="panel empty-state-panel" style={{ textAlign: "center", padding: "3rem" }}>
          <Calendar size={48} className="empty-icon" />
          <h3>No Scheduled Classes Found</h3>
          <p className="text-sm muted" style={{ maxWidth: "450px", margin: "0.5rem auto 1.5rem" }}>
            No lectures or labs are currently assigned to <strong>{faculty?.name}</strong> in the committed department timetable.
          </p>
          {isAdmin && (
            <Link to="/admin" className="btn btn-primary">
              Upload Timetable in Admin Panel
            </Link>
          )}
        </div>
      ) : selectedDay === "ALL" ? (
        /* Week grouped view */
        <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
          {daysList.map((day) => {
            const daySlots = groupedByDay[day] || [];
            if (daySlots.length === 0) return null;
            return (
              <div key={day} className="panel" style={{ padding: "1.25rem" }}>
                <h4 style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "1rem", color: "var(--primary)" }}>
                  <Calendar size={18} />
                  <span>{day}</span>
                  <span className="badge badge-outline" style={{ marginLeft: "0.5rem" }}>
                    {daySlots.length} sessions
                  </span>
                </h4>

                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: "1rem" }}>
                  {daySlots.map((item) => (
                    <div
                      key={item.id}
                      style={{
                        border: "1px solid var(--border)",
                        borderRadius: "8px",
                        padding: "1rem",
                        background: item.is_lab ? "var(--bg-subtle, #fefbf3)" : "#ffffff",
                        borderLeft: `4px solid ${item.is_lab ? "#d97706" : "var(--primary)"}`,
                      }}
                    >
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "0.5rem" }}>
                        <span style={{ fontWeight: 700, fontSize: "1.1rem" }}>{item.subject}</span>
                        {item.is_lab ? (
                          <span className="badge badge-warning">Lab ({item.batch})</span>
                        ) : (
                          <span className="badge badge-primary">Lecture</span>
                        )}
                      </div>

                      <div className="text-xs muted" style={{ display: "flex", alignItems: "center", gap: "0.4rem", marginBottom: "0.4rem" }}>
                        <Clock size={13} />
                        <span>{item.time_slot}</span>
                      </div>

                      <div className="text-xs muted" style={{ display: "flex", alignItems: "center", gap: "0.4rem", marginBottom: "0.4rem" }}>
                        <MapPin size={13} />
                        <span>Room / Lab: <strong>{item.room}</strong></span>
                      </div>

                      <div className="text-xs muted" style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}>
                        <Layers size={13} />
                        <span>B.Tech Semester {item.semester} — Division {item.division}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        /* Single day view */
        <div className="panel" style={{ padding: "1.25rem" }}>
          <h4 style={{ marginBottom: "1rem" }}>{selectedDay} Sessions</h4>
          {filteredSchedule.length === 0 ? (
            <div className="muted text-sm" style={{ padding: "1rem 0" }}>
              No classes scheduled on {selectedDay}.
            </div>
          ) : (
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: "1rem" }}>
              {filteredSchedule.map((item) => (
                <div
                  key={item.id}
                  style={{
                    border: "1px solid var(--border)",
                    borderRadius: "8px",
                    padding: "1rem",
                    background: item.is_lab ? "var(--bg-subtle, #fefbf3)" : "#ffffff",
                    borderLeft: `4px solid ${item.is_lab ? "#d97706" : "var(--primary)"}`,
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "0.5rem" }}>
                    <span style={{ fontWeight: 700, fontSize: "1.1rem" }}>{item.subject}</span>
                    {item.is_lab ? (
                      <span className="badge badge-warning">Lab ({item.batch})</span>
                    ) : (
                      <span className="badge badge-primary">Lecture</span>
                    )}
                  </div>

                  <div className="text-xs muted" style={{ display: "flex", alignItems: "center", gap: "0.4rem", marginBottom: "0.4rem" }}>
                    <Clock size={13} />
                    <span>{item.time_slot}</span>
                  </div>

                  <div className="text-xs muted" style={{ display: "flex", alignItems: "center", gap: "0.4rem", marginBottom: "0.4rem" }}>
                    <MapPin size={13} />
                    <span>Room / Lab: <strong>{item.room}</strong></span>
                  </div>

                  <div className="text-xs muted" style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}>
                    <Layers size={13} />
                    <span>B.Tech Semester {item.semester} — Division {item.division}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
