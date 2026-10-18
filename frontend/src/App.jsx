import { Route, Routes, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext.jsx";
import Navbar from "./components/Navbar.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Upload from "./pages/Upload.jsx";
import Review from "./pages/Review.jsx";
import Notifications from "./pages/Notifications.jsx";
import MasterData from "./pages/MasterData.jsx";
import Login from "./pages/Login.jsx";

function ProtectedRoute({ children }) {
  const { faculty } = useAuth();
  if (!faculty) {
    return <Navigate to="/login" replace />;
  }
  return children;
}

function AppContent() {
  const { faculty } = useAuth();

  return (
    <div className="portal-app">
      {faculty && <Navbar />}
      <main className={`portal-main-content ${!faculty ? "auth-screen" : ""}`}>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/upload"
            element={
              <ProtectedRoute>
                <Upload />
              </ProtectedRoute>
            }
          />
          <Route
            path="/review"
            element={
              <ProtectedRoute>
                <Review />
              </ProtectedRoute>
            }
          />
          <Route
            path="/review/:formId"
            element={
              <ProtectedRoute>
                <Review />
              </ProtectedRoute>
            }
          />
          <Route
            path="/notifications"
            element={
              <ProtectedRoute>
                <Notifications />
              </ProtectedRoute>
            }
          />
          {/* Backwards compatibility aliases */}
          <Route path="/emails" element={<Navigate to="/notifications" replace />} />
          <Route path="/history" element={<Navigate to="/" replace />} />
          <Route
            path="/master"
            element={
              <ProtectedRoute>
                <MasterData />
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<Navigate to={faculty ? "/" : "/login"} replace />} />
        </Routes>
      </main>
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}
