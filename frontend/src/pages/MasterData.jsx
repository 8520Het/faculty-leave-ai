import { useEffect, useState } from "react";
import { api } from "../api";

export default function MasterData() {
  const [staff, setStaff] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [rooms, setRooms] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([api.staff(), api.subjects(), api.rooms()])
      .then(([staffRows, subjectRows, roomRows]) => {
        setStaff(staffRows);
        setSubjects(subjectRows);
        setRooms(roomRows);
      })
      .catch((err) => setError(err.message));
  }, []);

  return (
    <section>
      <h2>Master data</h2>
      <p className="lede">
        Seeded from the existing academic, staff, and room catalogues used by
        timetable validation.
      </p>
      {error && <p className="error">{error}</p>}
      <div className="panel">
        <h3>Staff</h3>
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Dept</th>
            </tr>
          </thead>
          <tbody>
            {staff.map((row) => (
              <tr key={row.staff_id}>
                <td>{row.name}</td>
                <td>{row.email}</td>
                <td>{row.department}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="panel">
        <h3>Rooms</h3>
        <p>{rooms.map((row) => `Sem ${row.semester}: ${row.room}`).join(" · ")}</p>
      </div>
      <div className="panel">
        <h3>Subjects</h3>
        <table>
          <thead>
            <tr>
              <th>Sem</th>
              <th>Code</th>
              <th>Name</th>
              <th>Faculty</th>
            </tr>
          </thead>
          <tbody>
            {subjects.map((row) => (
              <tr key={`${row.semester}-${row.code}`}>
                <td>{row.semester}</td>
                <td>{row.code}</td>
                <td>{row.name}</td>
                <td>{row.teacher}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
