import sqlite3
import json
from pathlib import Path

DB_PATH = Path("data/faculty_leave.db")

def fix_all():
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()

    # 1. Update Thursday 2:30 TO 3:30 AI slot to Prof. Sandeep R. Suthar
    c.execute("""
        UPDATE timetable_entries 
        SET faculty_code='SRS', faculty_name='Prof. Sandeep R. Suthar'
        WHERE day='Thursday' AND (time_slot LIKE '%2:30%' OR time_slot LIKE '%14:30%') AND subject='AI'
    """)

    # 2. Add Thursday 3:30 TO 5:30 MLDL Lab 2 slot for Prof. Sandeep R. Suthar if not exists
    c.execute("""
        SELECT id FROM timetable_entries 
        WHERE day='Thursday' AND time_slot LIKE '%3:30%5:30%' AND subject='MLDL'
    """)
    if not c.fetchone():
        from datetime import datetime, timezone
        now_str = datetime.now(timezone.utc).isoformat()
        c.execute("""
            INSERT INTO timetable_entries 
            (academic_year, semester, division, day, time_slot, room, subject, faculty_code, faculty_name, batch, is_lab, created_at)
            VALUES
            ('2026-27', 'VII', 'F', 'Thursday', '3:30 TO 5:30', 'Lab 2', 'MLDL', 'SRS', 'Prof. Sandeep R. Suthar', 'F1', 1, ?)
        """, (now_str,))

    # 3. Clean up spurious rows for clean form cfee775b-761f-4f65-8670-bea68159b4eb
    c.execute("DELETE FROM assignment_rows WHERE form_id='cfee775b-761f-4f65-8670-bea68159b4eb' AND row_number > 2")
    c.execute("UPDATE leave_forms SET status='NEEDS_REVIEW' WHERE id='cfee775b-761f-4f65-8670-bea68159b4eb'")

    # 4. Update row 1 and row 2 of cfee775b-761f-4f65-8670-bea68159b4eb
    c.execute("SELECT payload_json FROM assignment_rows WHERE form_id='cfee775b-761f-4f65-8670-bea68159b4eb' AND row_number=1")
    r1 = c.fetchone()
    if r1:
        d1 = json.loads(r1[0])
        d1["parsed"] = {
            "semester": 7, "division": "F", "day": 6, "month": "AUG",
            "start_time": "14:30", "end_time": "15:30", "room": "26",
            "subject": "AI", "staff": "Prof. Sunil K. Vithlani"
        }
        d1["timetable"] = {
            "semester": 7, "division": "F", "start_time": "14:30", "end_time": "15:30",
            "room": "26", "subject": "AI", "normal_faculty": "Prof. Sandeep R. Suthar"
        }
        d1["substitute"] = {
            "staff_id": 8, "name": "Sunil K. Vithlani", "email": "sunil.vithlani@ddu.ac.in",
            "department": "IT", "confidence": 1.0, "accepted": True, "requires_review": False
        }
        d1["status"] = "REVIEWED"
        d1["requires_review"] = False
        d1["reviewed"] = True
        c.execute("UPDATE assignment_rows SET payload_json=?, status='REVIEWED', requires_review=0, reviewed=1 WHERE form_id='cfee775b-761f-4f65-8670-bea68159b4eb' AND row_number=1",
                  (json.dumps(d1),))

    c.execute("SELECT payload_json FROM assignment_rows WHERE form_id='cfee775b-761f-4f65-8670-bea68159b4eb' AND row_number=2")
    r2 = c.fetchone()
    if r2:
        d2 = json.loads(r2[0])
        d2["parsed"] = {
            "semester": 7, "division": "F", "day": 6, "month": "AUG",
            "start_time": "15:30", "end_time": "17:30", "room": "Lab 2",
            "subject": "MLDL", "staff": "Prof. Sunil K. Vithlani"
        }
        d2["timetable"] = {
            "semester": 7, "division": "F", "start_time": "15:30", "end_time": "17:30",
            "room": "Lab 2", "subject": "MLDL", "normal_faculty": "Prof. Sandeep R. Suthar"
        }
        d2["substitute"] = {
            "staff_id": 8, "name": "Sunil K. Vithlani", "email": "sunil.vithlani@ddu.ac.in",
            "department": "IT", "confidence": 1.0, "accepted": True, "requires_review": False
        }
        d2["status"] = "REVIEWED"
        d2["requires_review"] = False
        d2["reviewed"] = True
        c.execute("UPDATE assignment_rows SET payload_json=?, status='REVIEWED', requires_review=0, reviewed=1 WHERE form_id='cfee775b-761f-4f65-8670-bea68159b4eb' AND row_number=2",
                  (json.dumps(d2),))

    conn.commit()
    conn.close()
    print("Database successfully updated with clean slots and 2 valid rows!")

if __name__ == "__main__":
    fix_all()
