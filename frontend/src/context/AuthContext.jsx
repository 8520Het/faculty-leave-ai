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
    designation: "Professor",
    avatar: "/faculty/2-HBP.jpg",
    role: "FACULTY",
  },
  {
    id: 2,
    name: "Dr. Anand K. Patel",
    shortName: "AKP",
    email: "anand.patel@ddu.ac.in",
    password: "password123",
    department: "Information Technology",
    designation: "Associate Professor",
    avatar: "/faculty/17-akp.jpg",
    role: "FACULTY",
  },
  {
    id: 3,
    name: "Prof. Sandeep R. Suthar",
    shortName: "SRS",
    email: "sandeep.suthar@ddu.ac.in",
    password: "password123",
    department: "Information Technology",
    designation: "Assistant Professor",
    avatar: "/faculty/10-SRS.jpg",
    role: "FACULTY",
  },
  {
    id: 4,
    name: "Prof. Deepak C. Vegda",
    shortName: "DCV",
    email: "deepak.vegda@ddu.ac.in",
    password: "password123",
    department: "Information Technology",
    designation: "Assistant Professor",
    avatar: "/faculty/13-DCV.jpg",
    role: "FACULTY",
  },
  {
    id: 5,
    name: "Dr. Vipul K. Dabhi",
    shortName: "VKD",
    email: "vipul.dabhi@ddu.ac.in",
    password: "password123",
    department: "Information Technology",
    designation: "Professor & Head",
    avatar: "/faculty/1-VKD.jpg",
    role: "ADMIN",
  },
  {
    id: 6,
    name: "Prof. Nikita Desai",
    shortName: "NKD",
    email: "nikita.desai@ddu.ac.in",
    password: "password123",
    department: "Information Technology",
    designation: "Associate Professor",
    avatar: "/faculty/3-NKD1.jpg",
    role: "FACULTY",
  },
  {
    id: 7,
    name: "Prof. Archana N. Vyas",
    shortName: "ANV",
    email: "archana.vyas@ddu.ac.in",
    password: "password123",
    department: "Information Technology",
    designation: "Assistant Professor",
    avatar: "/faculty/12-ANV.jpg",
    role: "FACULTY",
  },
  {
    id: 8,
    name: "Prof. Sunil K. Vithlani",
    shortName: "SKV",
    email: "sunil.vithlani@ddu.ac.in",
    password: "password123",
    department: "Information Technology",
    designation: "Assistant Professor",
    avatar: "/faculty/14-SKV.jpg",
    role: "FACULTY",
  },
];


const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [faculty, setFaculty] = useState(() => {
    try {
      // Clear legacy localStorage so the portal always requests credentials on fresh start
      localStorage.removeItem("faculty_user");
      const saved = sessionStorage.getItem("faculty_user");
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
      sessionStorage.setItem("faculty_user", JSON.stringify(faculty));
      refreshNotifications();

      // Poll every 2.5 seconds so incoming notifications appear live across browsers
      const timer = setInterval(() => {
        refreshNotifications();
      }, 2500);

      return () => clearInterval(timer);
    } else {
      sessionStorage.removeItem("faculty_user");
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
    sessionStorage.removeItem("faculty_user");
    localStorage.removeItem("faculty_user");
    setFaculty(null);
  };

  const updateGoogleClientId = (id) => {
    setGoogleClientId(id);
    localStorage.setItem("google_client_id", id);
  };

  const isAdmin =
    faculty?.role === "ADMIN" ||
    faculty?.email?.toLowerCase() === "vipul.dabhi@ddu.ac.in";

  return (
    <AuthContext.Provider
      value={{
        faculty,
        isAdmin,
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
