from __future__ import annotations

import json
import shutil
import traceback
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import BackgroundTasks, Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from academic_master import FACULTY, SUBJECTS
from config import DEMO_MODE
from database import (
    AssignmentRow,
    EmailPreview,
    LeaveForm,
    ProcessingLog,
    get_db,
    init_db,
)
from form_pipeline import process_uploaded_form
from grouped_email import generate_grouped_email_previews
from paths import FORMS_DIR, PROJECT_ROOT, RAW_DIR, form_paths
from staff_master import STAFF_MASTER
from timetable import SEMESTER_ROOMS, TIMETABLE, get_active_semesters


app = FastAPI(
    title="Faculty Leave AI",
    description=(
        "Upload faculty leave-form images, extract arrangement rows, "
        "support human review, and generate grouped substitute emails. "
        "Supported input: faculty leave forms or visually similar tables."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AssignmentUpdate(BaseModel):
    status: Optional[str] = None
    parsed: Optional[dict] = None
    substitute: Optional[dict] = None
    timetable: Optional[dict] = None
    requires_review: Optional[bool] = None


class ProcessRequest(BaseModel):
    demo: bool = False


class DemoRequest(BaseModel):
    applicant_name: str = "Anand K. Patel"
    year: int = Field(default=2026, ge=2000, le=2100)


def _now():
    return datetime.now(timezone.utc)


def _dumps(value) -> str:
    return json.dumps(value, default=str)


def _loads(value, default=None):
    if not value:
        return default
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return default


def _log(db: Session, form_id: Optional[str], message: str, level: str = "INFO"):
    db.add(
        ProcessingLog(
            form_id=form_id,
            level=level,
            message=message,
        )
    )


def serialize_form(form: LeaveForm, include_assignments: bool = True) -> dict:
    payload = {
        "id": form.id,
        "original_filename": form.original_filename,
        "stored_path": form.stored_path,
        "applicant_name": form.applicant_name,
        "year": form.year,
        "status": form.status,
        "detection_strategy": form.detection_strategy,
        "error_message": form.error_message,
        "summary": _loads(form.summary_json, {}),
        "demo": form.demo,
        "created_at": form.created_at.isoformat() if form.created_at else None,
        "updated_at": form.updated_at.isoformat() if form.updated_at else None,
        "email_count": len(form.emails or []),
        "assignment_count": len(form.assignments or []),
    }
    if include_assignments:
        payload["assignments"] = [
            serialize_assignment(row) for row in form.assignments
        ]
        payload["emails"] = [serialize_email(item) for item in form.emails]
    return payload


def serialize_assignment(row: AssignmentRow) -> dict:
    payload = _loads(row.payload_json, {}) or {}
    payload.update(
        {
            "id": row.id,
            "form_id": row.form_id,
            "row_number": row.row_number,
            "status": row.status,
            "image_path": row.image_path,
            "ink_ratio": row.ink_ratio,
            "requires_review": row.requires_review,
            "reviewed": row.reviewed,
        }
    )
    return payload


def serialize_email(item: EmailPreview) -> dict:
    return {
        "id": item.id,
        "form_id": item.form_id,
        "to": item.to_email,
        "substitute_name": item.substitute_name,
        "assignment_count": item.assignment_count,
        "subject": item.subject,
        "body": item.body,
        "status": getattr(item, "status", "QUEUED") or "QUEUED",
        "sent_at": item.sent_at.isoformat() if getattr(item, "sent_at", None) else None,
        "generated_at": item.generated_at.isoformat() if item.generated_at else None,
    }


def sync_form_status(form: LeaveForm) -> None:
    if not form or not form.assignments:
        return
    all_reviewed = all(r.reviewed for r in form.assignments)
    all_ack = len(form.emails) > 0 and all(e.status == "ACKNOWLEDGED" for e in form.emails)
    any_sent = any(e.status in {"SENT", "ACKNOWLEDGED"} for e in form.emails)

    if all_ack:
        form.status = "CONFIRMED"
    elif any_sent:
        form.status = "NOTIFIED"
    elif all_reviewed:
        form.status = "REVIEWED"
    elif form.status in {"REVIEWED", "CONFIRMED"}:
        form.status = "NEEDS_REVIEW"


def replace_emails(db: Session, form: LeaveForm, previews: list[dict]) -> None:
    form.emails.clear()
    db.flush()
    for preview in previews:
        form.emails.append(
            EmailPreview(
                to_email=preview.get("to") or "",
                substitute_name=preview.get("substitute_name"),
                assignment_count=preview.get("assignment_count") or 0,
                subject=preview.get("subject") or "",
                body=preview.get("body") or "",
                status=preview.get("status") or "QUEUED",
            )
        )


def persist_pipeline_result(db: Session, form: LeaveForm, result: dict) -> None:
    form.assignments.clear()
    db.flush()

    detection = result.get("detection") or {}
    form.detection_strategy = (
        f"{detection.get('table_strategy')}/{detection.get('row_strategy')}"
    )
    form.demo = bool(result.get("demo"))
    form.summary_json = _dumps(result.get("summary") or {})
    form.status = "NEEDS_REVIEW"
    form.error_message = result.get("warning")
    form.updated_at = _now()

    for assignment in result.get("assignments") or []:
        image_path = assignment.get("image_path")
        form.assignments.append(
            AssignmentRow(
                row_number=assignment.get("row_number") or 0,
                status=assignment.get("status") or "MANUAL_REVIEW_REQUIRED",
                image_path=str(image_path) if image_path else None,
                ink_ratio=assignment.get("ink_ratio"),
                payload_json=_dumps(assignment),
                requires_review=True,
                reviewed=False,
            )
        )

    replace_emails(db, form, result.get("grouped_emails") or [])


def run_processing(form_id: str, demo: bool = False) -> None:
    from database import SessionLocal

    db = SessionLocal()
    form = db.get(LeaveForm, form_id)
    if form is None:
        db.close()
        return

    form.status = "PROCESSING"
    form.error_message = None
    form.updated_at = _now()
    _log(db, form_id, "Processing started")
    db.commit()

    try:
        result = process_uploaded_form(
            image_path=form.stored_path,
            form_id=form.id,
            applicant_name=form.applicant_name,
            year=form.year,
            demo=demo or form.demo,
        )
        persist_pipeline_result(db, form, result)
        _log(db, form_id, "Processing completed")
        db.commit()
    except Exception as exc:
        form.status = "FAILED"
        form.error_message = str(exc)
        form.updated_at = _now()
        _log(db, form_id, traceback.format_exc(), level="ERROR")
        db.commit()
    finally:
        db.close()


@app.on_event("startup")
def startup():
    init_db()
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    FORMS_DIR.mkdir(parents=True, exist_ok=True)


@app.get("/")
def root():
    return {
        "message": "Faculty Leave AI backend is running",
        "demo_mode": DEMO_MODE,
        "supported_input": (
            "Faculty leave-form images or visually similar arrangement tables"
        ),
    }


@app.get("/health")
def health():
    return {
        "ok": True,
        "demo_mode": DEMO_MODE,
        "project_root": str(PROJECT_ROOT),
    }


@app.get("/dashboard")
def dashboard(db: Session = Depends(get_db)):
    forms = db.query(LeaveForm).order_by(LeaveForm.created_at.desc()).all()
    for form in forms:
        sync_form_status(form)
    db.commit()
    status_counts = {}
    for form in forms:
        status_counts[form.status] = status_counts.get(form.status, 0) + 1
    return {
        "form_count": len(forms),
        "status_counts": status_counts,
        "recent": [serialize_form(form, include_assignments=False) for form in forms[:8]],
        "demo_mode": DEMO_MODE,
        "active_semesters": get_active_semesters(),
    }


@app.post("/upload")
async def upload_leave_form(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    applicant_name: str = Form("Unknown"),
    year: int = Form(2026),
    process_now: bool = Form(False),
    demo: bool = Form(False),
    db: Session = Depends(get_db),
):
    allowed_types = {"image/jpeg", "image/png", "image/jpg"}
    suffix = Path(file.filename or "form.jpg").suffix.lower()
    if suffix not in {".jpg", ".jpeg", ".png"} and file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Only JPG and PNG faculty leave-form images are allowed",
        )

    form_id = str(uuid.uuid4())
    paths = form_paths(form_id)
    extension = suffix if suffix in {".jpg", ".jpeg", ".png"} else ".jpg"
    stored_path = paths["root"] / f"original{extension}"

    with open(stored_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    raw_copy = RAW_DIR / f"{form_id}{extension}"
    shutil.copy2(stored_path, raw_copy)

    form = LeaveForm(
        id=form_id,
        original_filename=file.filename or stored_path.name,
        stored_path=str(stored_path),
        applicant_name=applicant_name.strip() or "Unknown",
        year=year,
        status="UPLOADED",
        demo=demo or DEMO_MODE,
    )
    db.add(form)
    _log(db, form_id, f"Uploaded {form.original_filename}")
    db.commit()
    db.refresh(form)

    if process_now:
        background_tasks.add_task(run_processing, form_id, form.demo)
        form.status = "QUEUED"
        db.commit()

    return serialize_form(form, include_assignments=False)


@app.post("/forms/{form_id}/process")
def process_form(
    form_id: str,
    background_tasks: BackgroundTasks,
    payload: Optional[ProcessRequest] = None,
    db: Session = Depends(get_db),
):
    form = db.get(LeaveForm, form_id)
    if form is None:
        raise HTTPException(status_code=404, detail="Form not found")
    if form.status == "PROCESSING":
        raise HTTPException(status_code=409, detail="Form is already processing")

    form.status = "QUEUED"
    demo_flag = bool(payload.demo) if payload is not None else False
    form.demo = form.demo or demo_flag or DEMO_MODE
    form.updated_at = _now()
    db.commit()
    background_tasks.add_task(run_processing, form_id, form.demo)
    return serialize_form(form, include_assignments=False)


@app.post("/demo/run")
def run_demo(
    payload: DemoRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    form_id = str(uuid.uuid4())
    paths = form_paths(form_id)
    placeholder = paths["root"] / "original.txt"
    placeholder.write_text(
        "Demo form placeholder. No OCR is run in demo mode.\n",
        encoding="utf-8",
    )
    form = LeaveForm(
        id=form_id,
        original_filename="demo-leave-form.txt",
        stored_path=str(placeholder),
        applicant_name=payload.applicant_name,
        year=payload.year,
        status="QUEUED",
        demo=True,
    )
    db.add(form)
    _log(db, form_id, "Demo processing queued")
    db.commit()
    background_tasks.add_task(run_processing, form_id, True)
    return serialize_form(form, include_assignments=False)


@app.get("/forms")
def list_forms(db: Session = Depends(get_db)):
    forms = db.query(LeaveForm).order_by(LeaveForm.created_at.desc()).all()
    for form in forms:
        sync_form_status(form)
    db.commit()
    return [serialize_form(form, include_assignments=False) for form in forms]


@app.get("/forms/{form_id}")
def get_form(form_id: str, db: Session = Depends(get_db)):
    form = db.get(LeaveForm, form_id)
    if form is None:
        raise HTTPException(status_code=404, detail="Form not found")
    return serialize_form(form)


@app.delete("/forms/{form_id}")
def delete_form(form_id: str, db: Session = Depends(get_db)):
    form = db.get(LeaveForm, form_id)
    if form is None:
        raise HTTPException(status_code=404, detail="Form not found")

    # Clean up processing logs
    db.query(ProcessingLog).filter(ProcessingLog.form_id == form_id).delete()

    # Clean up physical files on disk
    try:
        paths = form_paths(form_id)
        if paths["root"].exists():
            shutil.rmtree(paths["root"], ignore_errors=True)
        raw_target = RAW_DIR / f"{form_id}.png"
        if raw_target.exists():
            raw_target.unlink(missing_ok=True)
    except Exception as exc:
        print(f"Warning: Failed to delete form disk assets: {exc}")

    # Delete the form (SQLAlchemy cascades delete to assignments and emails)
    db.delete(form)
    db.commit()
    return {"ok": True, "message": f"Form {form_id} deleted successfully"}


@app.get("/forms/{form_id}/review")
def review_form(form_id: str, db: Session = Depends(get_db)):
    form = db.get(LeaveForm, form_id)
    if form is None:
        raise HTTPException(status_code=404, detail="Form not found")
    sync_form_status(form)
    db.commit()
    db.refresh(form)
    return {
        "form": serialize_form(form, include_assignments=True),
        "assignments": [serialize_assignment(row) for row in form.assignments],
        "staff": [
            {
                "staff_id": staff.staff_id,
                "name": staff.name,
                "email": staff.email,
                "department": staff.department,
            }
            for staff in STAFF_MASTER
        ],
        "rooms": sorted(set(SEMESTER_ROOMS.values())),
        "subjects": [
            {
                "semester": subject.semester,
                "code": subject.code,
                "name": subject.name,
            }
            for subject in SUBJECTS
        ],
        "note": (
            "All extracted rows require human review before emails are treated "
            "as approved arrangements."
        ),
    }


@app.put("/forms/{form_id}/assignments/{row_number}")
def update_assignment(
    form_id: str,
    row_number: int,
    payload: AssignmentUpdate,
    db: Session = Depends(get_db),
):
    form = db.get(LeaveForm, form_id)
    if form is None:
        raise HTTPException(status_code=404, detail="Form not found")

    row = next(
        (item for item in form.assignments if item.row_number == row_number),
        None,
    )
    if row is None:
        raise HTTPException(status_code=404, detail="Assignment row not found")

    data = _loads(row.payload_json, {}) or {}
    if payload.parsed is not None:
        data["parsed"] = {**(data.get("parsed") or {}), **payload.parsed}
    if payload.substitute is not None:
        data["substitute"] = payload.substitute
    if payload.timetable is not None:
        data["timetable"] = payload.timetable
    if payload.status is not None:
        data["status"] = payload.status
        row.status = payload.status
    else:
        data["status"] = "REVIEWED"
        row.status = "REVIEWED"

    data["requires_review"] = (
        payload.requires_review
        if payload.requires_review is not None
        else False
    )
    row.payload_json = _dumps(data)
    row.requires_review = bool(data["requires_review"])
    row.reviewed = True
    sync_form_status(form)
    form.updated_at = _now()
    db.commit()
    db.refresh(row)
    db.refresh(form)
    return serialize_assignment(row)


@app.post("/forms/{form_id}/emails")
def generate_emails(form_id: str, db: Session = Depends(get_db)):
    form = db.get(LeaveForm, form_id)
    if form is None:
        raise HTTPException(status_code=404, detail="Form not found")

    assignments = [serialize_assignment(row) for row in form.assignments]
    for item in assignments:
        item["applicant_name"] = form.applicant_name
    previews = generate_grouped_email_previews(assignments, year=form.year)
    replace_emails(db, form, previews)
    sync_form_status(form)
    form.summary_json = _dumps(
        {
            **(_loads(form.summary_json, {}) or {}),
            "emails": len(previews),
        }
    )
    form.updated_at = _now()
    db.commit()
    db.refresh(form)
    return {
        "form_id": form.id,
        "emails": [serialize_email(item) for item in form.emails],
        "count": len(form.emails),
    }


@app.get("/emails")
def list_emails(db: Session = Depends(get_db)):
    items = db.query(EmailPreview).order_by(EmailPreview.generated_at.desc()).all()
    return [serialize_email(item) for item in items]


@app.post("/emails/{email_id}/send")
def send_email(email_id: int, db: Session = Depends(get_db)):
    email = db.get(EmailPreview, email_id)
    if email is None:
        raise HTTPException(status_code=404, detail="Email preview not found")
    email.status = "SENT"
    email.sent_at = _now()
    _log(db, email.form_id, f"Notification sent to {email.substitute_name} ({email.to_email})")
    if email.form:
        sync_form_status(email.form)
        email.form.updated_at = _now()
    db.commit()
    db.refresh(email)
    return serialize_email(email)


@app.post("/forms/{form_id}/emails/send-all")
def send_all_emails(form_id: str, db: Session = Depends(get_db)):
    form = db.get(LeaveForm, form_id)
    if form is None:
        raise HTTPException(status_code=404, detail="Form not found")
    now_time = _now()
    sent_list = []
    for email in form.emails:
        email.status = "SENT"
        email.sent_at = now_time
        sent_list.append(email)
        _log(db, form_id, f"Notification sent to {email.substitute_name} ({email.to_email})")
    form.status = "NOTIFIED"
    form.updated_at = now_time
    db.commit()
    return {
        "form_id": form.id,
        "sent_count": len(sent_list),
        "emails": [serialize_email(e) for e in form.emails],
    }


@app.get("/faculty/{faculty_email}/notifications")
def get_faculty_notifications(faculty_email: str, db: Session = Depends(get_db)):
    target = faculty_email.strip().lower()
    items = (
        db.query(EmailPreview)
        .order_by(EmailPreview.generated_at.desc())
        .all()
    )
    matched = [
        serialize_email(item)
        for item in items
        if item.to_email and (item.to_email.strip().lower() == target or target in item.to_email.lower())
    ]
    return {
        "faculty_email": faculty_email,
        "count": len(matched),
        "notifications": matched,
    }


@app.post("/faculty/notifications/{email_id}/acknowledge")
def acknowledge_notification(email_id: int, db: Session = Depends(get_db)):
    email = db.get(EmailPreview, email_id)
    if email is None:
        raise HTTPException(status_code=404, detail="Notification not found")
    email.status = "ACKNOWLEDGED"
    now_time = _now()
    if email.form:
        sync_form_status(email.form)
        email.form.updated_at = now_time
    db.commit()
    db.refresh(email)
    return serialize_email(email)


@app.get("/forms/{form_id}/files/{kind}")
def get_form_file(
    form_id: str,
    kind: str,
    row: Optional[int] = None,
    db: Session = Depends(get_db),
):
    form = db.get(LeaveForm, form_id)
    if form is None:
        raise HTTPException(status_code=404, detail="Form not found")

    paths = form_paths(form_id)
    mapping = {
        "original": Path(form.stored_path),
        "normalized": paths["processed"] / "normalized.jpg",
        "table": paths["processed"] / "table.jpg",
        "cleaned": paths["processed"] / "table_without_grid.jpg",
        "overlay": paths["processed"] / "detection_overlay.jpg",
    }
    if kind == "row":
        if row is None:
            raise HTTPException(status_code=400, detail="row query parameter is required")
        target = paths["rows"] / f"assignment_row_{row}.jpg"
    else:
        target = mapping.get(kind)

    if target is None or not target.exists() or target.suffix == ".txt":
        raise HTTPException(status_code=404, detail="Requested file is not available")
    return FileResponse(target)


@app.get("/master/staff")
def master_staff():
    return [
        {
            "staff_id": staff.staff_id,
            "name": staff.name,
            "email": staff.email,
            "department": staff.department,
        }
        for staff in STAFF_MASTER
    ]


@app.get("/master/subjects")
def master_subjects():
    return [
        {
            "semester": subject.semester,
            "code": subject.code,
            "name": subject.name,
            "teacher_code": subject.teacher_code,
            "teacher": FACULTY[subject.teacher_code].name,
            "components": subject.components,
        }
        for subject in SUBJECTS
    ]


@app.get("/master/rooms")
def master_rooms():
    return [
        {"semester": semester, "room": room}
        for semester, room in SEMESTER_ROOMS.items()
    ]


@app.get("/master/timetable")
def master_timetable(semester: Optional[int] = None):
    slots = TIMETABLE
    if semester is not None:
        slots = [slot for slot in slots if slot.semester == semester]
    return [
        {
            "semester": slot.semester,
            "division": slot.division,
            "day": slot.day,
            "start_time": slot.start_time,
            "end_time": slot.end_time,
            "room": slot.room,
            "subject": slot.subject,
            "subject_name": slot.subject_name,
            "component": slot.component,
            "faculty": slot.faculty,
        }
        for slot in slots
    ]


@app.get("/samples")
def list_sample_images():
    samples_dir = PROJECT_ROOT / "samples"
    if not samples_dir.exists():
        return []
    items = []
    descriptions = {
        "sample_leave_form_harshad_prajapati.jpg": "Authentic handwritten sheet from Dr. Harshad Prajapati with 2 arrangement rows (covers: Sandeep Suthar & Anand Patel).",
        "sample_leave_form_anand_patel.jpg": "Filled leave application for Dr. Anand K. Patel (covers: Deepak Vegda & Sandeep Suthar).",
        "blank_template_ddu.jpg": "Blank Dharmsinh Desai University faculty leave application format.",
    }
    for f in sorted(samples_dir.glob("*.jpg")):
        items.append({
            "filename": f.name,
            "title": f.stem.replace("_", " ").title(),
            "description": descriptions.get(f.name, "Sample faculty leave arrangement form."),
            "url": f"/samples/{f.name}",
        })
    return items


@app.get("/samples/{filename}")
def get_sample_image(filename: str):
    target = PROJECT_ROOT / "samples" / filename
    if not target.exists() or target.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
        raise HTTPException(status_code=404, detail="Sample not found")
    return FileResponse(target)
