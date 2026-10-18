from __future__ import annotations

import traceback
from pathlib import Path

import cv2

from clean_table_rows import clean_table_image
from config import DEMO_MODE, INK_THRESHOLD, SKIP_OCR
from detect_filled_rows import detect_filled_rows
from grouped_email import generate_grouped_email_previews
from multi_row_pipeline import process_all_rows
from page_normalize import normalize_page
from paths import form_paths
from table_detect import detect_arrangement_table


DEMO_ASSIGNMENTS = [
    {
        "row_number": 2,
        "status": "VALIDATED_WITH_REVIEW",
        "class_ocr": {
            "normal": "Sem 7F 3 Aug 2:30-3:30",
            "selected": "Sem 7F 3 Aug 2:30-3:30",
            "source": "demo",
            "evidence_score": 6,
        },
        "ocr": {
            "room": "25",
            "subject": "AI",
            "staff": "Sandeep R. Suthar",
        },
        "subject_second_pass": {
            "ocr_text": "AI",
            "candidate": "AI",
            "accepted_subject": "AI",
            "score": 1.0,
        },
        "selected_subject": {
            "value": "AI",
            "source": "demo",
            "confidence": 1.0,
        },
        "parsed": {
            "semester": 7,
            "division": "F",
            "day": 3,
            "month": "AUG",
            "start_time": "14:30",
            "end_time": "15:30",
            "room": "25",
            "room_candidates": ["25"],
            "subject": "AI",
            "staff": "Sandeep R. Suthar",
        },
        "semester_hint": {
            "semester": 7,
            "subject_candidate": "AI",
            "subject_score": 1.0,
            "room_score": 1.0,
            "combined_score": 1.0,
            "requires_review": True,
        },
        "academic_match": {
            "semester": 7,
            "subject_code": "AI",
            "subject_name": "Artificial Intelligence",
            "room": "25",
            "teacher_code": "VD",
            "subject_score": 1.0,
            "room_score": 1.0,
            "total_score": 1.0,
            "subject_accepted": True,
            "requires_review": True,
        },
        "timetable": {
            "semester": 7,
            "division": "F",
            "day": "Monday",
            "start_time": "14:30",
            "end_time": "15:30",
            "room": "25",
            "subject": "AI",
            "normal_faculty": "Harshad B Prajapati",
            "confidence": 0.92,
        },
        "rejected_timetable_candidate": None,
        "substitute": {
            "staff_id": 1,
            "name": "Sandeep R. Suthar",
            "email": "sandeep.suthar@ddu.ac.in",
            "department": "IT",
            "confidence": 1.0,
            "accepted": True,
            "requires_review": False,
        },
        "requires_review": True,
    },
    {
        "row_number": 3,
        "status": "ACADEMIC_MATCH_REVIEW",
        "class_ocr": {
            "normal": "Sem 5F 4 Aug 10:30-11:30",
            "selected": "Sem 5F 4 Aug 10:30-11:30",
            "source": "demo",
            "evidence_score": 6,
        },
        "ocr": {
            "room": "26",
            "subject": "AJT",
            "staff": "Anand K. Patel",
        },
        "subject_second_pass": {
            "ocr_text": "AJT",
            "candidate": "AJT",
            "accepted_subject": "AJT",
            "score": 1.0,
        },
        "selected_subject": {
            "value": "AJT",
            "source": "demo",
            "confidence": 1.0,
        },
        "parsed": {
            "semester": 5,
            "division": "F",
            "day": 4,
            "month": "AUG",
            "start_time": "10:30",
            "end_time": "11:30",
            "room": "26",
            "room_candidates": ["26"],
            "subject": "AJT",
            "staff": "Anand K. Patel",
        },
        "semester_hint": {
            "semester": 5,
            "subject_candidate": "AJT",
            "subject_score": 1.0,
            "room_score": 1.0,
            "combined_score": 1.0,
            "requires_review": True,
        },
        "academic_match": {
            "semester": 5,
            "subject_code": "AJT",
            "subject_name": "Advanced Java Technology",
            "room": "26",
            "teacher_code": "HBP",
            "subject_score": 1.0,
            "room_score": 1.0,
            "total_score": 1.0,
            "subject_accepted": True,
            "requires_review": True,
        },
        "timetable": None,
        "rejected_timetable_candidate": None,
        "substitute": {
            "staff_id": 2,
            "name": "Anand K. Patel",
            "email": "anand.patel@ddu.ac.in",
            "department": "IT",
            "confidence": 1.0,
            "accepted": True,
            "requires_review": False,
        },
        "requires_review": True,
    },
]


def _write(path: Path, image) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(path), image)
    return str(path)


def extract_table_and_rows(image_path: Path, form_id: str) -> dict:
    paths = form_paths(form_id)
    image = cv2.imread(str(image_path))
    if image is None:
        raise FileNotFoundError(f"Could not read uploaded image: {image_path}")

    normalized = normalize_page(image)
    page = normalized["image"]
    _write(paths["processed"] / "normalized.jpg", page)

    table, box, table_strategy = detect_arrangement_table(page)
    table_path = paths["processed"] / "table.jpg"
    _write(table_path, table)

    overlay = page.copy()
    x, y, w, h = box
    cv2.rectangle(overlay, (x, y), (x + w, y + h), (40, 90, 220), 3)
    _write(paths["processed"] / "detection_overlay.jpg", overlay)

    cleaned = clean_table_image(table)
    cleaned_path = paths["processed"] / "table_without_grid.jpg"
    _write(cleaned_path, cleaned)

    rows = detect_filled_rows(
        table_path,
        ink_threshold=INK_THRESHOLD,
        output_dir=paths["rows"],
        crop_table_path=cleaned_path,
    )

    row_strategy = rows[0]["strategy"] if rows else "no_filled_rows"

    return {
        "paths": paths,
        "table_strategy": table_strategy,
        "row_strategy": row_strategy,
        "deskew_angle": normalized["angle"],
        "rows": rows,
        "table_path": table_path,
        "cleaned_path": cleaned_path,
    }


def process_uploaded_form(
    image_path,
    form_id: str,
    applicant_name: str,
    year: int,
    demo: bool = False,
) -> dict:
    image_path = Path(image_path)
    use_demo = demo or DEMO_MODE or SKIP_OCR

    if use_demo:
        assignments = [dict(item) for item in DEMO_ASSIGNMENTS]
        for item in assignments:
            item["requires_review"] = True
        pipeline_result = {
            "assignments": assignments,
            "grouped_emails": generate_grouped_email_previews(
                assignments,
                year=year,
            ),
            "summary": {
                "total": len(assignments),
                "exact": 1,
                "academic_review": 1,
                "manual_review": 0,
                "emails": 1,
            },
        }
        return {
            "demo": True,
            "detection": {
                "table_strategy": "demo_fixture",
                "row_strategy": "demo_fixture",
                "deskew_angle": 0.0,
            },
            **pipeline_result,
        }

    detection = extract_table_and_rows(image_path, form_id)
    paths = detection["paths"]

    try:
        pipeline_result = process_all_rows(
            applicant_name=applicant_name,
            year=year,
            table_path=detection["cleaned_path"],
            output_dir=paths["rows"],
            rows=detection["rows"],
            debug_dirs={
                "ocr_debug": paths["ocr_debug"],
                "class_second_pass": paths["class_second_pass"],
                "subject_second_pass": paths["subject_second_pass"],
            },
        )
    except Exception as exc:
        traceback.print_exc()
        raise RuntimeError(
            "OCR processing failed. The form image was saved and table/row "
            f"detection ran ({detection['table_strategy']} / "
            f"{detection['row_strategy']}). Underlying error: {exc}"
        ) from exc

    if not pipeline_result["assignments"]:
        pipeline_result["assignments"] = []
        pipeline_result.setdefault(
            "summary",
            {
                "total": 0,
                "exact": 0,
                "academic_review": 0,
                "manual_review": 0,
                "emails": 0,
            },
        )
        pipeline_result["warning"] = (
            "No filled assignment rows were detected. "
            "Human review can still add rows manually."
        )

    return {
        "demo": False,
        "detection": {
            "table_strategy": detection["table_strategy"],
            "row_strategy": detection["row_strategy"],
            "deskew_angle": detection["deskew_angle"],
        },
        **pipeline_result,
    }
