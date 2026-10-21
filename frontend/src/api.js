const API = "/api";

async function request(path, options = {}) {
  let response;
  try {
    response = await fetch(`${API}${path}`, options);
  } catch (err) {
    if (err?.message && (err.message.includes("Failed to fetch") || err.message.includes("NetworkError"))) {
      throw new Error("Unable to connect to backend server. Please verify backend is running on http://127.0.0.1:8000.");
    }
    throw err;
  }
  if (!response.ok) {
    let detail = `${response.status} ${response.statusText}`;
    try {
      const body = await response.json();
      detail = body.detail || JSON.stringify(body);
    } catch {
      /* keep status text */
    }
    throw new Error(detail);
  }
  if (response.status === 204) {
    return null;
  }
  return response.json();
}


export const api = {
  health: () => request("/health"),
  dashboard: (params = {}) => {
    const query = new URLSearchParams();
    if (params.applicant_name) query.set("applicant_name", params.applicant_name);
    if (params.faculty_email) query.set("faculty_email", params.faculty_email);
    const qs = query.toString();
    return request(qs ? `/dashboard?${qs}` : "/dashboard");
  },
  forms: (params = {}) => {
    const query = new URLSearchParams();
    if (params.applicant_name) query.set("applicant_name", params.applicant_name);
    if (params.faculty_email) query.set("faculty_email", params.faculty_email);
    const qs = query.toString();
    return request(qs ? `/forms?${qs}` : "/forms");
  },
  form: (id) => request(`/forms/${id}`),
  deleteForm: (id) => request(`/forms/${id}`, { method: "DELETE" }),
  review: (id, params = {}) => {
    const query = new URLSearchParams();
    if (params.applicant_name) query.set("applicant_name", params.applicant_name);
    if (params.faculty_email) query.set("faculty_email", params.faculty_email);
    const qs = query.toString();
    return request(qs ? `/forms/${id}/review?${qs}` : `/forms/${id}/review`);
  },
  process: (id, demo = false) =>
    request(`/forms/${id}/process`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ demo }),
    }),
  updateAssignment: (formId, rowNumber, payload) =>
    request(`/forms/${formId}/assignments/${rowNumber}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }),
  emails: (params = {}) => {
    const query = new URLSearchParams();
    if (params.faculty_email) query.set("faculty_email", params.faculty_email);
    if (params.faculty_name) query.set("faculty_name", params.faculty_name);
    if (params.is_admin) query.set("is_admin", "true");
    const qs = query.toString();
    return request(qs ? `/emails?${qs}` : "/emails");
  },
  adminEmails: () => request("/admin/emails"),
  adminForms: () => request("/admin/forms"),
  uploadTimetable: async (file) => {
    const data = new FormData();
    data.append("file", file);
    return request("/admin/timetable/upload", { method: "POST", body: data });
  },
  loadSampleTimetable: (sampleKey = "VII-F") =>
    request(`/admin/timetable/load-sample?sample_key=${sampleKey}`, { method: "POST" }),
  commitTimetable: (payload) =>
    request("/admin/timetable/commit", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }),
  adminTimetableEntries: (params = {}) => {
    const query = new URLSearchParams();
    if (params.semester) query.set("semester", params.semester);
    if (params.division) query.set("division", params.division);
    const qs = query.toString();
    return request(qs ? `/admin/timetable/entries?${qs}` : "/admin/timetable/entries");
  },
  deleteTimetableEntries: (semester, division) =>
    request(`/admin/timetable/entries?semester=${encodeURIComponent(semester)}&division=${encodeURIComponent(division)}`, {
      method: "DELETE",
    }),
  clearAllTimetables: () =>
    request("/admin/timetable/entries?clear_all=true", { method: "DELETE" }),
  seedDefaultTimetables: () =>
    request("/admin/timetable/seed-defaults", { method: "POST" }),
  mySchedule: (params = {}) => {
    const query = new URLSearchParams();
    if (params.faculty_email) query.set("faculty_email", params.faculty_email);
    if (params.faculty_name) query.set("faculty_name", params.faculty_name);
    const qs = query.toString();
    return request(qs ? `/timetable/my-schedule?${qs}` : "/timetable/my-schedule");
  },
  checkConflict: (payload) =>
    request("/timetable/check-conflict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }),
  generateEmails: (formId) =>
    request(`/forms/${formId}/emails`, { method: "POST" }),
  sendEmail: (emailId) =>
    request(`/emails/${emailId}/send`, { method: "POST" }),
  sendAllEmails: (formId) =>
    request(`/forms/${formId}/emails/send-all`, { method: "POST" }),
  facultyNotifications: (email) =>
    request(`/faculty/${encodeURIComponent(email)}/notifications`),
  acknowledgeNotification: (emailId) =>
    request(`/faculty/notifications/${emailId}/acknowledge`, { method: "POST" }),
  samples: () => request("/samples"),
  staff: () => request("/master/staff"),
  subjects: () => request("/master/subjects"),
  rooms: () => request("/master/rooms"),
  timetable: (semester) =>
    request(semester ? `/master/timetable?semester=${semester}` : "/master/timetable"),
  demo: (applicantName, year) =>
    request("/demo/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        applicant_name: applicantName,
        year: Number(year),
      }),
    }),
  upload: async ({ file, applicantName, year, processNow, demo }) => {
    const data = new FormData();
    data.append("file", file);
    data.append("applicant_name", applicantName);
    data.append("year", String(year));
    data.append("process_now", processNow ? "true" : "false");
    data.append("demo", demo ? "true" : "false");
    return request("/upload", { method: "POST", body: data });
  },
};

export function fileUrl(formId, kind, row) {
  const params = new URLSearchParams();
  if (row) params.set("row", String(row));
  const query = params.toString();
  return `${API}/forms/${formId}/files/${kind}${query ? `?${query}` : ""}`;
}

export function sampleUrl(filename) {
  return `${API}/samples/${filename}`;
}

export function poll(fn, { interval = 1500, until } = {}) {
  return new Promise((resolve, reject) => {
    const tick = async () => {
      try {
        const value = await fn();
        if (!until || until(value)) {
          resolve(value);
          return;
        }
        setTimeout(tick, interval);
      } catch (error) {
        reject(error);
      }
    };
    tick();
  });
}
