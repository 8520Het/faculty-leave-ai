import { createContext, useContext, useEffect, useState } from "react";
import { api } from "../api";

export const FACULTY_ACCOUNTS = [
  {
    id: 1,
    name: "Dr. Harshad B. Prajapati",
    shortName: "HBP",
    email: "harshad.prajapati@ddu.ac.in",
    password: "password123",
    department: "Information Technology",
    designation: "Associate Professor",
    avatar: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=120&auto=format&fit=crop&q=80",
  },
  {
    id: 2,
    name: "Dr. Anand K. Patel",
    shortName: "AKP",
    email: "anand.patel@ddu.ac.in",
    password: "password123",
    department: "Information Technology",
    designation: "Associate Professor",
    avatar: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=120&auto=format&fit=crop&q=80",
  },
  {
    id: 3,
    name: "Prof. Sandeep R. Suthar",
    shortName: "SRS",
    email: "sandeep.suthar@ddu.ac.in",
    password: "password123",
    department: "Information Technology",
    designation: "Assistant Professor",
    avatar: "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=120&auto=format&fit=crop&q=80",
  },
  {
    id: 4,
    name: "Prof. Deepak C. Vegda",
    shortName: "DCV",
    email: "deepak.vegda@ddu.ac.in",
    password: "password123",
    department: "Information Technology",
    designation: "Assistant Professor",
    avatar: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=120&auto=format&fit=crop&q=80",
  },
];

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [faculty, setFaculty] = useState(() => {
    try {
      const saved = localStorage.getItem("faculty_user");
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });

  const [googleClientId, setGoogleClientId] = useState(() => {
    return localStorage.getItem("google_client_id") || "";
  });

  const [incomingCount, setIncomingCount] = useState(0);

  useEffect(() => {
    if (faculty) {
      localStorage.setItem("faculty_user", JSON.stringify(faculty));
      refreshNotifications();

      // Poll every 2.5 seconds so incoming notifications appear live across browsers
      const timer = setInterval(() => {
        refreshNotifications();
      }, 2500);

      return () => clearInterval(timer);
    } else {
      localStorage.removeItem("faculty_user");
      setIncomingCount(0);
    }
  }, [faculty?.email]);

  const refreshNotifications = async () => {
    if (!faculty?.email) return;
    try {
      const res = await api.facultyNotifications(faculty.email);
      setIncomingCount(res?.count || 0);
    } catch {
      // ignore
    }
  };

  const loginWithCredentials = (inputEmail, inputPassword) => {
    const cleanEmail = (inputEmail || "").trim().toLowerCase();
    const cleanPass = (inputPassword || "").trim();

    if (!cleanEmail || !cleanPass) {
      return { success: false, error: "Please enter both email and password." };
    }

    const matched = FACULTY_ACCOUNTS.find(
      (f) => f.email.toLowerCase() === cleanEmail
    );

    if (!matched) {
      return {
        success: false,
        error: "Unrecognized institutional email. Only authorized faculty can log in.",
      };
    }

    if (matched.password !== cleanPass) {
      return {
        success: false,
        error: "Incorrect password. Please verify your credentials.",
      };
    }

    setFaculty(matched);
    return { success: true, faculty: matched };
  };

  const loginWithGoogle = (googleUserData) => {
    const matched = FACULTY_ACCOUNTS.find(
      (f) => f.email.toLowerCase() === googleUserData.email?.toLowerCase()
    );

    if (matched) {
      setFaculty(matched);
      return { success: true };
    }

    // If signed in with valid Google account from another faculty
    const newProfile = {
      id: Date.now(),
      name: googleUserData.name || "Faculty Member",
      email: googleUserData.email,
      department: "Information Technology",
      designation: "Faculty Member",
      avatar: googleUserData.picture,
      isGoogleAuth: true,
    };
    setFaculty(newProfile);
    return { success: true };
  };

  const logout = () => {
    localStorage.removeItem("faculty_user");
    setFaculty(null);
  };

  const updateGoogleClientId = (id) => {
    setGoogleClientId(id);
    localStorage.setItem("google_client_id", id);
  };

  return (
    <AuthContext.Provider
      value={{
        faculty,
        FACULTY_ACCOUNTS,
        loginWithCredentials,
        loginWithGoogle,
        logout,
        googleClientId,
        updateGoogleClientId,
        incomingCount,
        refreshNotifications,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
