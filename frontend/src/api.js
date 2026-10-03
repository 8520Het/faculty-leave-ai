const API = "/api";

async function request(path, options = {}) {
  const response = await fetch(`${API}${path}`, options);
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
  dashboard: () => request("/dashboard"),
  forms: () => request("/forms"),
  form: (id) => request(`/forms/${id}`),
  review: (id) => request(`/forms/${id}/review`),
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
  emails: () => request("/emails"),
  generateEmails: (formId) =>
    request(`/forms/${formId}/emails`, { method: "POST" }),
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
