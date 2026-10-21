from __future__ import annotations

import json
import re
import shutil
import traceback
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Any

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
    TimetableEntry,
    get_db,
    init_db,
)
from form_pipeline import process_uploaded_form
from grouped_email import generate_grouped_email_previews
from header_verifier import verify_applicant_identity
from paths import FORMS_DIR, PROJECT_ROOT, RAW_DIR, form_paths
from staff_master import STAFF_MASTER
from staff_matcher import match_staff_member, similarity
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


class TimetableSlotCommit(BaseModel):
    day: str
    time_slot: str
    subject: str
    faculty_code: str
    faculty_name: Optional[str] = ""
    room: Optional[str] = "26"
    batch: Optional[str] = "ALL"
    is_lab: Optional[bool] = False
    raw_text: Optional[str] = None


class TimetableCommitRequest(BaseModel):
    semester: str
    division: str
    academic_year: Optional[str] = "2026-27"
    slots: list[TimetableSlotCommit]


class ConflictCheckRequest(BaseModel):
    day: Optional[str] = None
    date_day: Optional[Any] = None
    date_month: Optional[Any] = None
    date_year: Optional[Any] = 2026
    time_slot: Optional[str] = ""
    substitute_name: Optional[str] = None
    substitute_code: Optional[str] = None
    applicant_name: Optional[str] = None
    room: Optional[Any] = None
    semester: Optional[Any] = None
    division: Optional[Any] = None
    subject: Optional[str] = None



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


def is_form_owned_by_faculty(
    form_applicant: str,
    query_applicant: Optional[str] = None,
    query_email: Optional[str] = None,
) -> bool:
    if not query_applicant and not query_email:
        return True

    target_staff = None
    if query_email:
        clean_email = query_email.strip().lower()
        for staff in STAFF_MASTER:
            if staff.email.lower() == clean_email:
                target_staff = staff
                break

    if not target_staff and query_applicant:
        target_staff = match_staff_member(query_applicant).matched_staff

    form_staff = match_staff_member(form_applicant).matched_staff

    if target_staff and form_staff:
        return target_staff.staff_id == form_staff.staff_id

    if target_staff and similarity(target_staff.name, form_applicant) >= 0.70:
        return True
    if query_applicant and similarity(query_applicant, form_applicant) >= 0.70:
        return True

    return False


def get_faculty_active_semesters(
    applicant_name: Optional[str] = None,
    faculty_email: Optional[str] = None,
) -> list[int]:
    target_staff = None
    if faculty_email:
        clean_email = faculty_email.strip().lower()
        for staff in STAFF_MASTER:
            if staff.email.lower() == clean_email:
                target_staff = staff
                break

    if not target_staff and applicant_name:
        target_staff = match_staff_member(applicant_name).matched_staff

    target_name = target_staff.name if target_staff else (applicant_name or "")
    active_term_sems = set(get_active_semesters())
    teacher_codes = []
    for code, f in FACULTY.items():
        if target_staff and (
            target_staff.name.lower() in f.name.lower()
            or f.name.lower() in target_staff.name.lower()
        ):
            teacher_codes.append(code)
        elif target_name and (
            target_name.lower() in f.name.lower()
            or f.name.lower() in target_name.lower()
        ):
            teacher_codes.append(code)

    if not teacher_codes and target_name:
        parts = [
            p[0].upper()
            for p in target_name.replace("Dr.", "").replace("Prof.", "").split()
            if p
        ]
        code_guess = "".join(parts)
        if code_guess in FACULTY:
            teacher_codes.append(code_guess)

    sems = set()
    for s in SUBJECTS:
        if any(tc == s.teacher_code for tc in teacher_codes):
            if s.semester in active_term_sems:
                sems.add(s.semester)

    if sems:
        return sorted(list(sems))

    if "anand" in target_name.lower() or "akp" in teacher_codes:
        return [5]
    if "sunil" in target_name.lower() or "skv" in teacher_codes:
        return [3, 5]
    if "sandeep" in target_name.lower() or "srs" in teacher_codes:
        return [3]
    if "harshad" in target_name.lower() or "hbp" in teacher_codes:
        return [3, 5, 7]
    if "deepak" in target_name.lower() or "dcv" in teacher_codes:
        return [1, 3, 5]

    return get_active_semesters()


@app.get("/dashboard")
def dashboard(
    applicant_name: Optional[str] = None,
    faculty_email: Optional[str] = None,
    db: Session = Depends(get_db),
):
    all_forms = db.query(LeaveForm).order_by(LeaveForm.created_at.desc()).all()
    for form in all_forms:
        sync_form_status(form)
    db.commit()

    if applicant_name or faculty_email:
        forms = [
            f
            for f in all_forms
            if is_form_owned_by_faculty(
                f.applicant_name,
                query_applicant=applicant_name,
                query_email=faculty_email,
            )
        ]
        faculty_sems = get_faculty_active_semesters(applicant_name, faculty_email)
    else:
        forms = all_forms
        faculty_sems = get_active_semesters()

    status_counts = {}
    for form in forms:
        status_counts[form.status] = status_counts.get(form.status, 0) + 1
    return {
        "form_count": len(forms),
        "status_counts": status_counts,
        "recent": [serialize_form(form, include_assignments=False) for form in forms[:8]],
        "demo_mode": DEMO_MODE,
        "active_semesters": faculty_sems,
    }


@app.post("/upload")
def upload_leave_form(
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

    # Validate that handwritten applicant name in 'Name in Full' matches logged-in faculty
    clean_applicant = applicant_name.strip()
    if not (demo or DEMO_MODE) and clean_applicant and clean_applicant.lower() != "unknown":
        verification = verify_applicant_identity(stored_path, clean_applicant)
        if not verification.get("valid", True):
            try:
                stored_path.unlink(missing_ok=True)
                raw_copy.unlink(missing_ok=True)
                shutil.rmtree(paths["root"], ignore_errors=True)
            except Exception:
                pass
            raise HTTPException(
                status_code=400,
                detail=verification.get("error") or "Identity Mismatch on form.",
            )

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
def list_forms(
    applicant_name: Optional[str] = None,
    faculty_email: Optional[str] = None,
    db: Session = Depends(get_db),
):
    forms = db.query(LeaveForm).order_by(LeaveForm.created_at.desc()).all()
    for form in forms:
        sync_form_status(form)
    db.commit()

    if applicant_name or faculty_email:
        forms = [
            f
            for f in forms
            if is_form_owned_by_faculty(
                f.applicant_name,
                query_applicant=applicant_name,
                query_email=faculty_email,
            )
        ]

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
def review_form(
    form_id: str,
    applicant_name: Optional[str] = None,
    faculty_email: Optional[str] = None,
    db: Session = Depends(get_db),
):
    form = db.get(LeaveForm, form_id)
    if form is None:
        raise HTTPException(status_code=404, detail="Form not found")

    if (applicant_name or faculty_email) and not is_form_owned_by_faculty(
        form.applicant_name,
        query_applicant=applicant_name,
        query_email=faculty_email,
    ):
        raise HTTPException(
            status_code=403,
            detail="Access Denied: You can only view and review leave forms submitted by your account.",
        )

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
def list_emails(
    faculty_email: Optional[str] = None,
    faculty_name: Optional[str] = None,
    is_admin: bool = False,
    db: Session = Depends(get_db),
):
    items = db.query(EmailPreview).order_by(EmailPreview.generated_at.desc()).all()
    if is_admin:
        return [serialize_email(item) for item in items]

    if faculty_email or faculty_name:
        filtered = []
        for item in items:
            # Check 1: Recipient email matches
            if faculty_email and item.to_email and faculty_email.strip().lower() in item.to_email.strip().lower():
                filtered.append(item)
                continue
            # Check 2: Recipient substitute name matches
            if faculty_name and item.substitute_name and (
                similarity(faculty_name.strip().lower(), item.substitute_name.strip().lower()) >= 0.70
                or faculty_name.strip().lower() in item.substitute_name.strip().lower()
                or item.substitute_name.strip().lower() in faculty_name.strip().lower()
            ):
                filtered.append(item)
                continue
            # Check 3: Current user is the applicant who generated the notifications
            if item.form and is_form_owned_by_faculty(
                item.form.applicant_name,
                query_applicant=faculty_name,
                query_email=faculty_email,
            ):
                filtered.append(item)
                continue
        return [serialize_email(item) for item in filtered]

    return [serialize_email(item) for item in items]


@app.get("/admin/emails")
def list_admin_emails(db: Session = Depends(get_db)):
    items = db.query(EmailPreview).order_by(EmailPreview.generated_at.desc()).all()
    return [serialize_email(item) for item in items]


@app.get("/admin/forms")
def list_admin_forms(db: Session = Depends(get_db)):
    forms = db.query(LeaveForm).order_by(LeaveForm.created_at.desc()).all()
    for form in forms:
        sync_form_status(form)
    db.commit()
    return [serialize_form(form, include_assignments=True) for form in forms]



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


# ============================================================
# TIMETABLE MANAGEMENT & PERSONAL SCHEDULE ENDPOINTS
# ============================================================

@app.post("/admin/timetable/upload")
def upload_admin_timetable(
    file: UploadFile = File(...),
):
    file_bytes = file.file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Empty timetable image file")


    from timetable_parser import parse_timetable_image
    result = parse_timetable_image(file_bytes)
    return result


@app.post("/admin/timetable/load-sample")
def load_sample_timetable(
    sample_key: str = "VII-F",
):
    from timetable_parser import KNOWN_TIMETABLES, resolve_faculty, SUBJECT_MAP
    if sample_key not in KNOWN_TIMETABLES:
        raise HTTPException(status_code=404, detail="Sample timetable not found")

    template = KNOWN_TIMETABLES[sample_key]
    populated_slots = []
    for i, s in enumerate(template["slots"]):
        fac = resolve_faculty(s["faculty_code"])
        populated_slots.append(
            {
                **s,
                "id": f"slot_{i+1}",
                "faculty_name": fac["name"],
                "faculty_email": fac["email"],
                "subject_name": SUBJECT_MAP.get(s["subject"], s["subject"]),
                "raw_text": f"{s['subject']} / {s['faculty_code']}" if not s["is_lab"] else f"{s['batch']}-{s['subject']}-{s['faculty_code']} {s['room']}",
            }
        )

    return {
        "semester": template["semester"],
        "division": template["division"],
        "academic_year": template["academic_year"],
        "default_room": template["default_room"],
        "slots": populated_slots,
        "total_slots": len(populated_slots),
        "source": "SAMPLE_PRESET",
    }


@app.post("/admin/timetable/commit")
def commit_admin_timetable(
    payload: TimetableCommitRequest,
    db: Session = Depends(get_db),
):
    db.query(TimetableEntry).filter(
        TimetableEntry.semester == payload.semester,
        TimetableEntry.division == payload.division,
    ).delete()

    created = []
    for slot in payload.slots:
        entry = TimetableEntry(
            academic_year=payload.academic_year or "2026-27",
            semester=payload.semester,
            division=payload.division,
            day=slot.day,
            time_slot=slot.time_slot,
            room=slot.room or "26",
            subject=slot.subject,
            faculty_code=slot.faculty_code,
            faculty_name=slot.faculty_name or "",
            batch=slot.batch or "ALL",
            is_lab=bool(slot.is_lab),
            raw_text=slot.raw_text,
        )
        db.add(entry)
        created.append(entry)

    db.commit()
    return {
        "ok": True,
        "message": f"Successfully committed {len(created)} slots for Semester {payload.semester} Division {payload.division}",
        "count": len(created),
    }


PERIOD_MAP = {
    "8:30 TO 9:30": {1},
    "08:30 TO 09:30": {1},
    "09:30 TO 10:30": {2},
    "9:30 TO 10:30": {2},
    "8:30 TO 10:30": {1, 2},
    "08:30 TO 10:30": {1, 2},
    "10:45 TO 11:45": {3},
    "11:45 TO 12:45": {4},
    "10:45 TO 12:45": {3, 4},
    "1:30 TO 2:30": {5},
    "01:30 TO 02:30": {5},
    "2:30 TO 3:30": {6},
    "02:30 TO 03:30": {6},
    "1:30 TO 3:30": {5, 6},
    "01:30 TO 03:30": {5, 6},
    "3:30 TO 4:30": {7},
    "03:30 TO 04:30": {7},
    "4:30 TO 5:30": {8},
    "04:30 TO 05:30": {8},
    "3:30 TO 5:30": {7, 8},
    "03:30 TO 05:30": {7, 8},
}


def slots_overlap(s1: Optional[str], s2: Optional[str]) -> bool:
    if not s1 or not s2:
        return False
    norm1 = re.sub(r"\s+", " ", str(s1).strip().upper())
    norm2 = re.sub(r"\s+", " ", str(s2).strip().upper())
    if norm1 == norm2:
        return True
    p1 = PERIOD_MAP.get(norm1)
    p2 = PERIOD_MAP.get(norm2)
    if p1 and p2:
        return bool(p1.intersection(p2))
    return False


@app.get("/admin/timetable/entries")
def get_timetable_entries(
    semester: Optional[str] = None,
    division: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(TimetableEntry)
    if semester and semester != "ALL":
        query = query.filter(TimetableEntry.semester == semester)
    if division and division != "ALL":
        query = query.filter(TimetableEntry.division == division)
    entries = query.order_by(TimetableEntry.day, TimetableEntry.time_slot).all()

    return [
        {
            "id": e.id,
            "academic_year": e.academic_year,
            "semester": e.semester,
            "division": e.division,
            "day": e.day,
            "time_slot": e.time_slot,
            "room": e.room,
            "subject": e.subject,
            "faculty_code": e.faculty_code,
            "faculty_name": e.faculty_name,
            "batch": e.batch,
            "is_lab": e.is_lab,
            "raw_text": e.raw_text,
        }
        for e in entries
    ]


@app.delete("/admin/timetable/entries")
def delete_timetable_entries(
    semester: Optional[str] = None,
    division: Optional[str] = None,
    clear_all: bool = False,
    db: Session = Depends(get_db),
):
    if clear_all:
        count = db.query(TimetableEntry).delete()
        db.commit()
        return {
            "ok": True,
            "message": f"Successfully deleted all {count} timetable entries across all semesters and divisions.",
            "count": count,
        }

    if not semester or not division:
        raise HTTPException(
            status_code=400,
            detail="To delete a specific timetable, please specify both semester and division (e.g. semester=VII&division=E)."
        )

    clean_sem = str(semester).strip().upper()
    clean_div = str(division).strip().upper()

    query = db.query(TimetableEntry)
    if clean_sem in ("7", "VII"):
        query = query.filter(TimetableEntry.semester.in_(["7", "VII"]))
    elif clean_sem in ("5", "V"):
        query = query.filter(TimetableEntry.semester.in_(["5", "V"]))
    elif clean_sem in ("3", "III"):
        query = query.filter(TimetableEntry.semester.in_(["3", "III"]))
    else:
        query = query.filter(TimetableEntry.semester == clean_sem)

    query = query.filter(TimetableEntry.division == clean_div)
    count = query.delete(synchronize_session=False)
    db.commit()
    return {
        "ok": True,
        "message": f"Deleted {count} slots for Semester {clean_sem} Division {clean_div}",
        "count": count,
    }


@app.post("/admin/timetable/seed-defaults")
def seed_default_timetables(
    db: Session = Depends(get_db),
):
    from timetable_parser import KNOWN_TIMETABLES, resolve_faculty
    count = 0
    # Keep strictly ONE preset timetable: Semester VII - Division F (Official IT Dept sample)
    preset_keys = ["VII-F"]
    for key in preset_keys:
        template = KNOWN_TIMETABLES.get(key)
        if not template:
            continue
        exists = db.query(TimetableEntry).filter(
            TimetableEntry.semester == template["semester"],
            TimetableEntry.division == template["division"],
        ).first()
        if exists:
            continue
        for s in template["slots"]:
            fac = resolve_faculty(s["faculty_code"])
            db.add(
                TimetableEntry(
                    academic_year=template["academic_year"],
                    semester=template["semester"],
                    division=template["division"],
                    day=s["day"],
                    time_slot=s["time_slot"],
                    room=s["room"],
                    subject=s["subject"],
                    faculty_code=s["faculty_code"],
                    faculty_name=fac["name"],
                    batch=s.get("batch", "ALL"),
                    is_lab=bool(s.get("is_lab", False)),
                )
            )
            count += 1
    db.commit()
    return {
        "ok": True,
        "message": f"Successfully loaded official preset timetable for Sem VII Div F ({count} slots).",
        "count": count,
    }


@app.get("/timetable/my-schedule")
def get_my_schedule(
    faculty_email: Optional[str] = None,
    faculty_name: Optional[str] = None,
    db: Session = Depends(get_db),
):
    entries = db.query(TimetableEntry).all()
    from timetable_parser import FACULTY_MAP
    my_slots = []
    for e in entries:
        matches = False
        if faculty_name and (
            similarity(e.faculty_name.lower(), faculty_name.lower()) >= 0.70
            or faculty_name.lower() in e.faculty_name.lower()
            or e.faculty_name.lower() in faculty_name.lower()
        ):
            matches = True
        if not matches and faculty_email:
            fac_info = FACULTY_MAP.get(e.faculty_code)
            if fac_info and fac_info.get("email", "").lower() == faculty_email.lower():
                matches = True
            elif faculty_email.lower().split("@")[0].replace(".", "") in e.faculty_name.lower().replace(" ", "").replace(".", ""):
                matches = True

        if matches:
            my_slots.append(
                {
                    "id": e.id,
                    "academic_year": e.academic_year,
                    "semester": e.semester,
                    "division": e.division,
                    "day": e.day,
                    "time_slot": e.time_slot,
                    "room": e.room,
                    "subject": e.subject,
                    "faculty_code": e.faculty_code,
                    "faculty_name": e.faculty_name,
                    "batch": e.batch,
                    "is_lab": e.is_lab,
                }
            )

    return {
        "faculty_name": faculty_name,
        "faculty_email": faculty_email,
        "count": len(my_slots),
        "schedule": my_slots,
    }


MONTHS_MAP = {
    "JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5, "JUN": 6,
    "JUL": 7, "AUG": 8, "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12
}


def resolve_day_of_week(day_name=None, date_day=None, date_month=None, date_year=2026) -> str:
    valid_days = {"Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"}
    if day_name and str(day_name).strip().capitalize() in valid_days:
        return str(day_name).strip().capitalize()
    if date_day is not None and date_month:
        try:
            m_str = str(date_month).strip().upper()[:3]
            m_num = MONTHS_MAP.get(m_str)
            if not m_num:
                m_digits = re.search(r"\d+", str(date_month))
                if m_digits:
                    m_num = int(m_digits.group(0))
            if m_num:
                d_match = re.search(r"\d+", str(date_day))
                if d_match:
                    d_num = int(d_match.group(0))
                    y_num = int(date_year or 2026)
                    dt = datetime(y_num, m_num, d_num)
                    return dt.strftime("%A")
        except Exception:
            pass
    return "Monday"


def normalize_time_slot(raw: Optional[str]) -> str:
    if not raw:
        return ""
    s = str(raw).strip().upper()
    s = re.sub(r"(\d{1,2})\.(\d{2})", r"\1:\2", s)
    parts = re.split(r"\s*(?:TO|-)\s*", s)

    def to_12h(t: str) -> str:
        m = re.search(r"(\d{1,2}):(\d{2})", t)
        if not m:
            return t
        hr, mn = int(m.group(1)), m.group(2)
        if hr > 12:
            hr -= 12
        return f"{hr}:{mn}"

    if len(parts) >= 2:
        return f"{to_12h(parts[0])} TO {to_12h(parts[1])}"
    elif len(parts) == 1:
        st = to_12h(parts[0])
        if st in ["8:30", "08:30"]: return "8:30 TO 9:30"
        if st in ["9:30", "09:30"]: return "09:30 TO 10:30"
        if st in ["10:45"]: return "10:45 TO 11:45"
        if st in ["11:45"]: return "11:45 TO 12:45"
        if st in ["1:30", "01:30"]: return "1:30 TO 2:30"
        if st in ["2:30", "02:30"]: return "2:30 TO 3:30"
        if st in ["3:30", "03:30"]: return "3:30 TO 4:30"
        if st in ["4:30", "04:30"]: return "4:30 TO 5:30"
        return st
    return s


CURRICULUM_MASTER = {
    "VII": {
        "codes": ["AI", "WT", "MLDL", "DEVOPS", "DC", "COI", "PROJ-II", "PROJECT-II"],
        "names": {
            "AI": "Artificial Intelligence",
            "WT": "Web Technology",
            "MLDL": "Machine Learning & Deep Learning",
            "DEVOPS": "DevOps Engineering",
            "DC": "Distributed Computing",
            "COI": "Constitution of India",
            "PROJ-II": "Project II",
            "PROJECT-II": "Project II",
        },
        "divisions": ["E", "F"],
    },
    "V": {
        "codes": ["FSD", "MPI", "SE", "ITE", "CO", "TAFL", "PROJ-I"],
        "names": {
            "FSD": "Full Stack Development",
            "MPI": "Microprocessor & Interfacing",
            "SE": "Software Engineering",
            "ITE": "Information Technology & Enterprise",
            "CO": "Computer Organization",
            "TAFL": "Theory of Automata & Formal Languages",
        },
        "divisions": ["E"],
    },
    "III": {
        "codes": ["DSA", "DBMS", "OOP", "DELD", "MATHS-III"],
        "names": {
            "DSA": "Data Structures & Algorithms",
            "DBMS": "Database Management Systems",
            "OOP": "Object Oriented Programming",
            "DELD": "Digital Electronics & Logic Design",
        },
        "divisions": ["E"],
    },
}


@app.post("/timetable/check-conflict")
def check_timetable_conflict(
    payload: ConflictCheckRequest,
    db: Session = Depends(get_db),
):
    conflicts = []
    warnings = []

    # 1. Resolve Day of Week
    day = resolve_day_of_week(
        day_name=payload.day,
        date_day=payload.date_day,
        date_month=payload.date_month,
        date_year=payload.date_year,
    )
    raw_slot = str(payload.time_slot or "").strip()
    norm_time_slot = normalize_time_slot(raw_slot)

    # 2. Timing validation
    if not raw_slot:
        warnings.append(
            "Missing Lecture Time: Lecture start and end times were not detected or entered. Please verify or enter the lecture timing."
        )
    else:
        # Check if the time slot aligns with any official academic periods in PERIOD_MAP
        period_set = PERIOD_MAP.get(norm_time_slot)
        if not period_set:
            matched_any = any(slots_overlap(k, norm_time_slot) for k in PERIOD_MAP)
            if not matched_any:
                warnings.append(
                    f"Invalid Timing Discrepancy: '{raw_slot}' does not match any official academic lecture (1 hr) or lab (2 hrs) slot in department schedule."
                )

    # Clean Semester and Division
    clean_sem = str(payload.semester or "").strip().upper()
    if clean_sem in ("5", "V"): clean_sem = "V"
    elif clean_sem in ("7", "VII"): clean_sem = "VII"
    elif clean_sem in ("3", "III"): clean_sem = "III"

    clean_div = str(payload.division or "").strip().upper()

    # 3. Check Division validity in IT curriculum
    if clean_sem in CURRICULUM_MASTER:
        official_divs = CURRICULUM_MASTER[clean_sem]["divisions"]
        if clean_div and clean_div not in official_divs:
            warnings.append(
                f"Division Discrepancy: Division '{clean_div}' is not found for Semester {clean_sem} (Official IT division: {', '.join(official_divs)})."
            )

    # 4. Check Subject validity in curriculum (e.g. C, 2000S, etc.)
    raw_sub = str(payload.subject or "").strip()
    clean_sub = re.sub(r"^\d+[\.\s]+", "", raw_sub).strip().upper()
    clean_sub = re.sub(r"[^A-Za-z0-9\-]", "", clean_sub)
    if clean_sub and clean_sem in CURRICULUM_MASTER:
        known_codes = CURRICULUM_MASTER[clean_sem]["codes"]
        known_names = CURRICULUM_MASTER[clean_sem]["names"]
        is_known = any(
            clean_sub == c.upper()
            or c.upper() in clean_sub
            or clean_sub in c.upper()
            or any(clean_sub in full.upper() for full in known_names.values())
            for c in known_codes
        )
        if not is_known:
            warnings.append(
                f"Unrecognized Course: Subject '{raw_sub}' is not an active curriculum course for Semester {clean_sem} (Official courses: {', '.join(known_codes)})."
            )

    # 5. Cross-check against active department timetable slots in DB
    if clean_sem and norm_time_slot:
        query = db.query(TimetableEntry).filter(
            TimetableEntry.day == day,
            TimetableEntry.semester == clean_sem,
        )
        if clean_div:
            matching_slots = [
                s for s in query.filter(TimetableEntry.division == clean_div).all()
                if slots_overlap(s.time_slot, norm_time_slot)
            ]
        else:
            matching_slots = [
                s for s in query.all()
                if slots_overlap(s.time_slot, norm_time_slot)
            ]

        if matching_slots:
            # A) Subject Mismatch Check
            expected_subjects = list({s.subject for s in matching_slots if s.subject})
            if clean_sub and expected_subjects:
                sub_matched = any(
                    clean_sub == exp.upper()
                    or clean_sub in exp.upper()
                    or exp.upper() in clean_sub
                    for exp in expected_subjects
                )
                if not sub_matched:
                    exp_display = ", ".join(expected_subjects)
                    warnings.append(
                        f"Subject Mismatch: Form specifies subject '{raw_sub}', but official timetable lists '{exp_display}' for Semester {clean_sem} Division {clean_div} on {day} at {norm_time_slot}."
                    )

            # B) Room Discrepancy Check
            clean_room = str(payload.room or "").strip().upper()
            expected_rooms = list({s.room for s in matching_slots if s.room})
            if clean_room and expected_rooms and not any(r.upper() == clean_room for r in expected_rooms):
                warnings.append(
                    f"Room Discrepancy: Form specifies Room/Lab {clean_room}, but official timetable lists Room/Lab {', '.join(expected_rooms)} for Semester {clean_sem} on {day} at {norm_time_slot}."
                )

            # C) Instructor Discrepancy Check
            if payload.applicant_name:
                expected_instructors = list({s.faculty_name for s in matching_slots if s.faculty_name})
                if expected_instructors:
                    app_clean = payload.applicant_name.lower().replace("dr.", "").replace("prof.", "").replace(" ", "").replace(".", "")
                    matches_app = any(
                        app_clean in inst.lower().replace("dr.", "").replace("prof.", "").replace(" ", "").replace(".", "")
                        or inst.lower().replace("dr.", "").replace("prof.", "").replace(" ", "").replace(".", "") in app_clean
                        or similarity(payload.applicant_name.lower(), inst.lower()) >= 0.70
                        for inst in expected_instructors
                    )
                    if not matches_app:
                        warnings.append(
                            f"Instructor Discrepancy: Official timetable shows this lecture ({matching_slots[0].subject}) is scheduled for {', '.join(expected_instructors)}, not applicant {payload.applicant_name}."
                        )
        else:
            # Check if this class has timetable in DB, but no slot exists at this time
            class_slots_count = db.query(TimetableEntry).filter(
                TimetableEntry.semester == clean_sem,
                TimetableEntry.division == clean_div,
            ).count()
            if class_slots_count > 0:
                warnings.append(
                    f"No Class Scheduled: Official timetable has no lecture or lab scheduled for Semester {clean_sem} Division {clean_div} on {day} at {norm_time_slot}."
                )

    # 6. Check: Substitute Faculty busy/teaching conflict (including combined 2h labs)
    if payload.substitute_name or payload.substitute_code:
        sub_slots = db.query(TimetableEntry).filter(
            TimetableEntry.day == day,
        ).all()
        for slot in sub_slots:
            if not norm_time_slot or not slots_overlap(slot.time_slot, norm_time_slot):
                continue
            is_sub = False
            if payload.substitute_code and slot.faculty_code.upper() == payload.substitute_code.upper():
                is_sub = True
            elif payload.substitute_name and (
                similarity(slot.faculty_name.lower(), payload.substitute_name.lower()) >= 0.70
                or payload.substitute_name.lower() in slot.faculty_name.lower()
                or slot.faculty_name.lower() in payload.substitute_name.lower()
            ):
                is_sub = True

            if is_sub:
                conflicts.append(
                    f"Substitute Conflict: Substitute {slot.faculty_name} is NOT free at this time. Already scheduled to teach {slot.subject} ({'Lab ' + slot.batch if slot.is_lab else 'Lecture'}) in Room/Lab {slot.room} on {day} at {slot.time_slot}."
                )

    return {
        "day_resolved": day,
        "time_slot_normalized": norm_time_slot,
        "has_conflict": len(conflicts) > 0,
        "has_warning": len(warnings) > 0,
        "conflicts": conflicts,
        "warnings": warnings,
        "require_confirmation": len(conflicts) > 0 or len(warnings) > 0,
    }

