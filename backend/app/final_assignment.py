import json

from parser import parse_class_field
from field_parser import parse_assignment_fields
from timetable_validator import rank_timetable_matches
from staff_matcher import match_staff_member


# ============================================================
# CURRENT OCR OUTPUTS
# ============================================================

class_ocr = "1 . Semi-F.3Avg 2.30.3.30. 2"
room_ocr = "25 ."
subject_ocr = ". AT.T.S"
staff_ocr = "Sandeep R. Kuthorff ,"

applicant_name = "Harshad B. Prajapati"
year = 2026


# ============================================================
# STEP 1: PARSE CLASS
# ============================================================

class_result = parse_class_field(
    class_ocr
)


# ============================================================
# STEP 2: PARSE ROOM / SUBJECT / STAFF
# ============================================================

field_result = parse_assignment_fields(
    room_text=room_ocr,
    subject_text=subject_ocr,
    staff_text=staff_ocr
)


# ============================================================
# STEP 3: NORMALIZE TIME
#
# For now, known afternoon college slots:
# 02:30 -> 14:30
# 03:30 -> 15:30
#
# Later we'll make this configurable.
# ============================================================

start_time = class_result.start_time
end_time = class_result.end_time

if start_time == "02:30":
    start_time = "14:30"

if end_time == "03:30":
    end_time = "15:30"


# ============================================================
# STEP 4: TIMETABLE VALIDATION
# ============================================================

timetable_matches = rank_timetable_matches(
    semester=class_result.semester,
    division=class_result.division,
    day=class_result.day,
    month=class_result.month,
    year=year,
    start_time=start_time,
    end_time=end_time,
    room_ocr=field_result.room_number,
    subject_ocr=field_result.subject,
    applicant_name=applicant_name
)

best_timetable = (
    timetable_matches[0]
    if timetable_matches
    else None
)


# ============================================================
# STEP 5: SUBSTITUTE STAFF MATCHING
# ============================================================

staff_match = match_staff_member(
    field_result.staff_name_raw
)


# ============================================================
# STEP 6: FINAL REVIEW DECISION
# ============================================================

requires_review = True

if (
    best_timetable is not None
    and
    staff_match.matched_staff is not None
):

    # We still keep review=True for now because
    # OCR quality is imperfect and email sending
    # must not happen automatically yet.
    requires_review = True


# ============================================================
# STEP 7: BUILD FINAL JSON
# ============================================================

final_result = {

    "applicant": {
        "name": applicant_name
    },

    "ocr": {
        "class_raw": class_ocr,
        "room_raw": room_ocr,
        "subject_raw": subject_ocr,
        "staff_raw": staff_ocr
    },

    "parsed": {
        "semester": class_result.semester,
        "division": class_result.division,
        "day": class_result.day,
        "month": class_result.month,
        "year": year,
        "start_time": start_time,
        "end_time": end_time,
        "room": field_result.room_number,
        "subject": field_result.subject,
        "substitute_staff_raw": field_result.staff_name_raw
    },

    "timetable_suggestion": None,

    "substitute_staff_suggestion": None,

    "requires_review": requires_review
}


# ============================================================
# ADD TIMETABLE SUGGESTION
# ============================================================

if best_timetable:

    final_result[
        "timetable_suggestion"
    ] = {

        "semester": best_timetable.semester,
        "division": best_timetable.division,

        "day": best_timetable.day,

        "start_time": best_timetable.start_time,
        "end_time": best_timetable.end_time,

        "room": best_timetable.room,
        "subject": best_timetable.subject,

        "normal_faculty": best_timetable.faculty,

        "confidence": round(
            best_timetable.total_score,
            2
        )
    }


# ============================================================
# ADD SUBSTITUTE STAFF SUGGESTION
# ============================================================

if staff_match.matched_staff:

    final_result[
        "substitute_staff_suggestion"
    ] = {

        "staff_id":
            staff_match.matched_staff.staff_id,

        "name":
            staff_match.matched_staff.name,

        "email":
            staff_match.matched_staff.email,

        "department":
            staff_match.matched_staff.department,

        "confidence":
            round(
                staff_match.score,
                2
            ),

        "requires_review":
            staff_match.requires_review
    }


# ============================================================
# PRINT FINAL JSON
# ============================================================

print()
print(
    "========================================"
)

print(
    "FINAL ASSIGNMENT JSON"
)

print(
    "========================================"
)

print(
    json.dumps(
        final_result,
        indent=4
    )
)