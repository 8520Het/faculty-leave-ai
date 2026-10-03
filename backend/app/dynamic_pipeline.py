from pathlib import Path

from ocr_fields import ocr_assignment_row
from parser import parse_class_field
from field_parser import parse_assignment_fields
from timetable_validator import rank_timetable_matches
from staff_matcher import match_staff_member
from email_preview import generate_email_preview
from paths import PROJECT_ROOT


# ============================================================
# TIME NORMALIZATION
# ============================================================

def normalize_college_time(time_value):

    if time_value is None:
        return None

    time_map = {
        "01:30": "13:30",
        "02:30": "14:30",
        "03:30": "15:30",
        "04:30": "16:30",
        "05:30": "17:30"
    }

    return time_map.get(
        time_value,
        time_value
    )


# ============================================================
# DYNAMIC PIPELINE
# ============================================================

def process_assignment_row(
    row_image_path,
    applicant_name,
    year
):

    print()
    print("========================================")
    print("1. RUNNING OCR")
    print("========================================")

    ocr_result = ocr_assignment_row(
        row_image_path
    )

    print("Class OCR:", ocr_result["class"])
    print("Room OCR:", ocr_result["room"])
    print("Subject OCR:", ocr_result["subject"])
    print("Staff OCR:", ocr_result["staff_name"])


    # ========================================================
    # PARSE CLASS
    # ========================================================

    class_result = parse_class_field(
        ocr_result["class"]
    )


    # ========================================================
    # PARSE OTHER FIELDS
    # ========================================================

    field_result = parse_assignment_fields(

        room_text=ocr_result["room"],

        subject_text=ocr_result["subject"],

        staff_text=ocr_result["staff_name"]
    )


    # ========================================================
    # NORMALIZE TIME
    # ========================================================

    start_time = normalize_college_time(
        class_result.start_time
    )

    end_time = normalize_college_time(
        class_result.end_time
    )


    # ========================================================
    # TIMETABLE VALIDATION
    # ========================================================

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


    # ========================================================
    # STAFF MATCHING
    # ========================================================

    staff_match = match_staff_member(
        field_result.staff_name_raw
    )


    # ========================================================
    # PRINT VALIDATION
    # ========================================================

    print()
    print("========================================")
    print("2. VALIDATION RESULT")
    print("========================================")

    if best_timetable:

        print(
            "Semester:",
            best_timetable.semester
        )

        print(
            "Division:",
            best_timetable.division
        )

        print(
            "Subject:",
            best_timetable.subject
        )

        print(
            "Room:",
            best_timetable.room
        )

        print(
            "Normal Faculty:",
            best_timetable.faculty
        )

        print(
            "Timetable Confidence:",
            round(
                best_timetable.total_score,
                2
            )
        )

    else:

        print(
            "No timetable match found"
        )


    print()

    if staff_match.matched_staff:

        print(
            "Substitute Suggestion:",
            staff_match.matched_staff.name
        )

        print(
            "Substitute Email:",
            staff_match.matched_staff.email
        )

        print(
            "Staff Confidence:",
            round(
                staff_match.score,
                2
            )
        )

    else:

        print(
            "No substitute staff match found"
        )


    # ========================================================
    # EMAIL PREVIEW
    # ========================================================

    if (
        best_timetable
        and
        staff_match.matched_staff
        and
        class_result.day
        and
        class_result.month
    ):

        email = generate_email_preview(

            substitute_name=
                staff_match.matched_staff.name,

            substitute_email=
                staff_match.matched_staff.email,

            applicant_name=
                best_timetable.faculty,

            semester=
                best_timetable.semester,

            division=
                best_timetable.division,

            lecture_day=
                class_result.day,

            lecture_month=
                class_result.month,

            lecture_year=
                year,

            start_time=
                best_timetable.start_time,

            end_time=
                best_timetable.end_time,

            room=
                best_timetable.room,

            subject=
                best_timetable.subject
        )


        print()
        print("========================================")
        print("3. FINAL EMAIL PREVIEW")
        print("========================================")

        print()
        print("To:")
        print(email["to"])

        print()
        print("Subject:")
        print(email["subject"])

        print()
        print("Body:")
        print()
        print(email["body"])

    else:

        print()
        print(
            "Email preview could not be generated."
        )

        print(
            "Human review is required."
        )


# ============================================================
# TEST WITH CURRENT ROW
# ============================================================

if __name__ == "__main__":

    ROW_PATH = (
        PROJECT_ROOT
        / "data"
        / "crops"
        / "clean_rows"
        / "assignment_row_1.jpg"
    )

    process_assignment_row(

        row_image_path=ROW_PATH,

        applicant_name=
            "Harshad B. Prajapati",

        year=2026
    )