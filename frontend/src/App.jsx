import { NavLink, Route, Routes } from "react-router-dom";
import Dashboard from "./pages/Dashboard.jsx";
import Upload from "./pages/Upload.jsx";
import Review from "./pages/Review.jsx";
import Emails from "./pages/Emails.jsx";
import History from "./pages/History.jsx";
import MasterData from "./pages/MasterData.jsx";

export default function App() {
  return (
    <div className="shell">
      <aside className="sidebar">
        <p className="eyebrow">IT Department desk</p>
        <h1>Leave arrangements</h1>
        <p className="lede">
          Read a filled faculty leave form, check every assignment, then
          generate grouped emails for substitutes.
        </p>
        <nav>
          <NavLink to="/" end>
            Dashboard
          </NavLink>
          <NavLink to="/upload">Upload</NavLink>
          <NavLink to="/review">Review</NavLink>
          <NavLink to="/emails">Emails</NavLink>
          <NavLink to="/history">History</NavLink>
          <NavLink to="/master">Master data</NavLink>
        </nav>
        <p className="footnote">
          Works on leave-form images and similar arrangement tables. Unrelated
          photos are not supported.
        </p>
      </aside>
      <main className="content">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/upload" element={<Upload />} />
          <Route path="/review" element={<Review />} />
          <Route path="/review/:formId" element={<Review />} />
          <Route path="/emails" element={<Emails />} />
          <Route path="/history" element={<History />} />
          <Route path="/master" element={<MasterData />} />
        </Routes>
      </main>
    </div>
  );
}
