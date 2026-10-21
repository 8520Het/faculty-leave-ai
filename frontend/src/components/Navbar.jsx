import { useState, useRef, useEffect } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import {
  FileText,
  UploadCloud,
  CheckCircle2,
  Bell,
  Calendar,
  LogOut,
  ChevronDown,
  Building,
  ShieldCheck,
} from "lucide-react";

export default function Navbar() {
  const { faculty, isAdmin, logout, incomingCount } = useAuth();

  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    function handleClickOutside(event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setDropdownOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <header className="app-navbar">
      <div className="nav-brand-section">
        <div className="brand-logo-badge">
          <Building size={20} className="brand-icon" />
        </div>
        <div>
          <h1 className="brand-title">Faculty Leave AI</h1>
          <p className="brand-subtitle">Smart Arrangement & Notification Portal</p>
        </div>
      </div>

      <nav className="nav-links">
        <NavLink to="/" end className={({ isActive }) => (isActive ? "nav-item active" : "nav-item")}>
          <FileText size={17} />
          <span>Dashboard</span>
        </NavLink>

        <NavLink to="/upload" className={({ isActive }) => (isActive ? "nav-item active" : "nav-item")}>
          <UploadCloud size={17} />
          <span>Upload Form</span>
        </NavLink>

        <NavLink to="/review" className={({ isActive }) => (isActive ? "nav-item active" : "nav-item")}>
          <CheckCircle2 size={17} />
          <span>Scan Results & Review</span>
        </NavLink>

        <NavLink to="/notifications" className={({ isActive }) => (isActive ? "nav-item active" : "nav-item")}>
          <div className="nav-icon-badge-wrap">
            <Bell size={17} />
            {incomingCount > 0 && <span className="nav-badge-count">{incomingCount}</span>}
          </div>
          <span>Notifications</span>
        </NavLink>

        <NavLink to="/my-schedule" className={({ isActive }) => (isActive ? "nav-item active" : "nav-item")}>
          <Calendar size={17} />
          <span>My Schedule</span>
        </NavLink>

        {isAdmin && (
          <NavLink
            to="/admin"
            className={({ isActive }) =>
              isActive ? "nav-item active admin-nav-item" : "nav-item admin-nav-item"
            }
            style={{ color: "var(--primary)", fontWeight: 600 }}
          >
            <ShieldCheck size={17} />
            <span>Admin Panel</span>
          </NavLink>
        )}
      </nav>


      <div className="nav-user-section" ref={dropdownRef}>
        {faculty ? (
          <div className="faculty-profile-chip" onClick={() => setDropdownOpen(!dropdownOpen)}>
            <img
              src={
                faculty.avatar ||
                `https://ui-avatars.com/api/?name=${encodeURIComponent(faculty.name)}&background=1e293b&color=fff`
              }
              alt={faculty.name}
              className="faculty-avatar"
            />
            <div className="faculty-info-text">
              <span className="faculty-name">{faculty.name}</span>
              <span className="faculty-dept">{faculty.department || "IT Dept"}</span>
            </div>
            <ChevronDown size={14} className={`dropdown-arrow ${dropdownOpen ? "open" : ""}`} />

            {dropdownOpen && (
              <div className="faculty-dropdown-menu">
                <div className="dropdown-header">
                  <p className="dropdown-faculty-name">{faculty.name}</p>
                  <p className="dropdown-faculty-email">{faculty.email}</p>
                  <span className="badge ok text-xs">{faculty.designation || "Faculty Member"}</span>
                </div>

                <div className="dropdown-divider" />
                <button
                  type="button"
                  className="dropdown-logout-btn"
                  onClick={(e) => {
                    e.stopPropagation();
                    logout();
                    navigate("/login");
                  }}
                >
                  <LogOut size={15} />
                  <span>Sign Out</span>
                </button>
              </div>
            )}
          </div>
        ) : (
          <button className="button primary sm" onClick={() => navigate("/login")}>
            Faculty Sign In
          </button>
        )}
      </div>
    </header>
  );
}
