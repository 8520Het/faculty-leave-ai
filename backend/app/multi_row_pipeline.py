from detect_filled_rows import detect_filled_rows, TABLE_PATH
from ocr_fields import ocr_assignment_row

from class_selector import choose_best_class_ocr
from field_parser import parse_assignment_fields

from subject_ocr import run_subject_second_pass

from timetable_validator import (
    rank_timetable_matches,
    infer_semester_from_subject_room
)

from academic_matcher import (
    get_best_academic_candidate
)

from staff_matcher import match_staff_member

from grouped_email import (
    generate_grouped_email_previews,
    print_grouped_email_previews
)


# ============================================================
# THRESHOLDS
# ============================================================

TIMETABLE_ACCEPT_THRESHOLD = 0.65
STAFF_ACCEPT_THRESHOLD = 0.80
ACADEMIC_ACCEPT_THRESHOLD = 0.65
SUBJECT_ACCEPT_THRESHOLD = 0.60


# ============================================================
# TIME NORMALIZATION
# ============================================================

def normalize_college_time(
    time_value
):

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
# MAIN PIPELINE
# ============================================================

def process_all_rows(
    applicant_name,
    year
):

    rows = detect_filled_rows(
        TABLE_PATH
    )

    final_results = []

    print()
    print(
        "========================================"
    )
    print(
        "MULTI-ROW PROCESSING"
    )
    print(
        "========================================"
    )


    # ========================================================
    # PROCESS EACH FILLED ROW
    # ========================================================

    for row in rows:

        row_number = (
            row["row_number"]
        )

        image_path = (
            row["image_path"]
        )


        print()
        print(
            "----------------------------------------"
        )
        print(
            f"PROCESSING ROW {row_number}"
        )
        print(
            "----------------------------------------"
        )


        # ====================================================
        # STEP 1
        # NORMAL OCR
        # ====================================================

        ocr_result = ocr_assignment_row(
            image_path
        )


        print()
        print(
            "NORMAL OCR"
        )

        print(
            "Class:",
            ocr_result["class"]
        )

        print(
            "Room:",
            ocr_result["room"]
        )

        print(
            "Subject:",
            ocr_result["subject"]
        )

        print(
            "Staff:",
            ocr_result["staff_name"]
        )


        # ====================================================
        # STEP 2
        # BEST CLASS OCR
        # ====================================================

        class_selection = (
            choose_best_class_ocr(
                image_path
            )
        )

        class_result = (
            class_selection.parsed_result
        )


        print()
        print(
            "BEST CLASS OCR"
        )

        print(
            "Source:",
            class_selection.source
        )

        print(
            "Text:",
            class_selection.selected_text
        )

        print(
            "Evidence score:",
            class_selection.evidence_score
        )


        # ====================================================
        # STEP 3
        # PARSED CLASS
        # ====================================================

        print()
        print(
            "PARSED CLASS"
        )

        print(
            "Semester:",
            class_result.semester
        )

        print(
            "Division:",
            class_result.division
        )

        print(
            "Day:",
            class_result.day
        )

        print(
            "Month:",
            class_result.month
        )

        print(
            "Start:",
            class_result.start_time
        )

        print(
            "End:",
            class_result.end_time
        )

        print(
            "Requires Review:",
            class_result.requires_review
        )


        # ====================================================
        # STEP 4
        # PARSE ROOM / SUBJECT / STAFF
        # ====================================================

        field_result = (
            parse_assignment_fields(

                room_text=
                    ocr_result["room"],

                subject_text=
                    ocr_result["subject"],

                staff_text=
                    ocr_result["staff_name"]
            )
        )


        print()
        print(
            "PARSED FIELDS"
        )

        print(
            "Room OCR:",
            ocr_result["room"]
        )

        print(
            "Room Candidates:",
            field_result.room_candidates
        )

        print(
            "Selected Room:",
            field_result.room_number
        )

        print(
            "Normal Subject:",
            field_result.subject
        )

        print(
            "Clean Staff:",
            field_result.staff_name_raw
        )


        # ====================================================
        # STEP 5
        # SUBJECT SECOND PASS
        # ====================================================

        subject_second_pass = (
            run_subject_second_pass(
                image_path
            )
        )

        best_subject_second_pass = (
            subject_second_pass[
                "best"
            ]
        )


        print()
        print(
            "SUBJECT SECOND PASS"
        )


        if best_subject_second_pass:

            print(
                "Variant:",
                best_subject_second_pass[
                    "variant"
                ]
            )

            print(
                "OCR:",
                best_subject_second_pass[
                    "ocr_text"
                ]
            )

            print(
                "Raw Candidate:",
                best_subject_second_pass[
                    "raw_subject_candidate"
                ]
            )

            print(
                "Accepted Subject:",
                (
                    best_subject_second_pass[
                        "subject"
                    ]
                    if
                    best_subject_second_pass[
                        "subject"
                    ]
                    else
                    "UNKNOWN"
                )
            )

            print(
                "Score:",
                round(
                    best_subject_second_pass[
                        "score"
                    ],
                    2
                )
            )

            print(
                "Accepted:",
                best_subject_second_pass[
                    "accepted"
                ]
            )

        else:

            print(
                "No second-pass subject result"
            )


        # ====================================================
        # STEP 6
        # SELECT SUBJECT SOURCE
        # ====================================================

        selected_subject_text = (
            field_result.subject
        )

        selected_subject_source = (
            "normal"
        )

        selected_subject_score = 0.0


        if best_subject_second_pass:

            if (
                best_subject_second_pass[
                    "accepted"
                ]
            ):

                selected_subject_text = (
                    best_subject_second_pass[
                        "subject"
                    ]
                )

                selected_subject_source = (
                    "second_pass"
                )

                selected_subject_score = (
                    best_subject_second_pass[
                        "score"
                    ]
                )


        print()
        print(
            "SELECTED SUBJECT"
        )

        print(
            "Subject:",
            selected_subject_text
        )

        print(
            "Source:",
            selected_subject_source
        )

        print(
            "Confidence:",
            round(
                selected_subject_score,
                2
            )
        )


        # ====================================================
        # STEP 7
        # SEMESTER HINT
        # ====================================================

        semester_hint = (
            infer_semester_from_subject_room(

                subject_ocr=
                    selected_subject_text,

                room_ocr=
                    field_result.room_number
            )
        )


        print()
        print(
            "SEMESTER HINT"
        )

        print(
            "Semester:",
            semester_hint.semester
        )

        print(
            "Subject Candidate:",
            (
                semester_hint.subject_candidate
                if
                semester_hint.subject_candidate
                else
                "UNKNOWN"
            )
        )

        print(
            "Subject Score:",
            round(
                semester_hint.subject_score,
                2
            )
        )

        print(
            "Room Score:",
            round(
                semester_hint.room_score,
                2
            )
        )

        print(
            "Combined Score:",
            round(
                semester_hint.combined_score,
                2
            )
        )

        print(
            "Reason:",
            semester_hint.reason
        )

        print(
            "Requires Review:",
            semester_hint.requires_review
        )


        # ====================================================
        # STEP 8
        # ACADEMIC MATCH
        # ====================================================

        academic_candidate = (
            get_best_academic_candidate(

                subject_ocr=
                    selected_subject_text,

                room_ocr=
                    field_result.room_number
            )
        )


        print()
        print(
            "ACADEMIC MATCH"
        )


        if academic_candidate:

            print(
                "Semester:",
                academic_candidate.semester
            )

            print(
                "Subject:",
                (
                    academic_candidate.subject_code
                    if
                    academic_candidate.subject_accepted
                    else
                    "UNKNOWN"
                )
            )

            print(
                "Subject Name:",
                (
                    academic_candidate.subject_name
                    if
                    academic_candidate.subject_accepted
                    else
                    "UNKNOWN"
                )
            )

            print(
                "Room:",
                academic_candidate.room
            )

            print(
                "Subject Score:",
                round(
                    academic_candidate.subject_score,
                    2
                )
            )

            print(
                "Room Score:",
                round(
                    academic_candidate.room_score,
                    2
                )
            )

            print(
                "Combined Score:",
                round(
                    academic_candidate.total_score,
                    2
                )
            )

            print(
                "Subject Accepted:",
                academic_candidate.subject_accepted
            )

        else:

            print(
                "No academic candidate found"
            )


        # ====================================================
        # STEP 9
        # NORMALIZE TIME
        # ====================================================

        start_time = (
            normalize_college_time(
                class_result.start_time
            )
        )

        end_time = (
            normalize_college_time(
                class_result.end_time
            )
        )


        # ====================================================
        # STEP 10
        # TIMETABLE MATCHING
        # ====================================================

        timetable_matches = (
            rank_timetable_matches(

                semester=
                    class_result.semester,

                division=
                    class_result.division,

                day=
                    class_result.day,

                month=
                    class_result.month,

                year=
                    year,

                start_time=
                    start_time,

                end_time=
                    end_time,

                room_ocr=
                    field_result.room_number,

                subject_ocr=
                    selected_subject_text,

                applicant_name=
                    applicant_name
            )
        )


        raw_best_timetable = (
            timetable_matches[0]
            if timetable_matches
            else None
        )


        # ====================================================
        # STEP 11
        # ACCEPT / REJECT TIMETABLE
        # ====================================================

        best_timetable = None


        if raw_best_timetable is not None:

            if (
                raw_best_timetable.total_score
                >=
                TIMETABLE_ACCEPT_THRESHOLD
            ):

                best_timetable = (
                    raw_best_timetable
                )


        # ====================================================
        # STEP 12
        # STAFF MATCHING
        # ====================================================

        staff_match = (
            match_staff_member(
                field_result.staff_name_raw
            )
        )


        staff_is_reliable = False


        if (
            staff_match.matched_staff
            is not None
            and
            staff_match.score
            >=
            STAFF_ACCEPT_THRESHOLD
        ):

            staff_is_reliable = True


        # ====================================================
        # STEP 13
        # ACADEMIC MATCH QUALITY
        # ====================================================

        academic_is_reliable = False


        if (
            academic_candidate
            is not None
            and
            academic_candidate.subject_accepted
            and
            academic_candidate.total_score
            >=
            ACADEMIC_ACCEPT_THRESHOLD
        ):

            academic_is_reliable = True


        # ====================================================
        # STEP 14
        # DETERMINE STATUS
        # ====================================================

        if (
            best_timetable
            is not None
            and
            staff_is_reliable
        ):

            row_status = (
                "VALIDATED_WITH_REVIEW"
            )


        elif academic_is_reliable:

            row_status = (
                "ACADEMIC_MATCH_REVIEW"
            )


        else:

            row_status = (
                "MANUAL_REVIEW_REQUIRED"
            )


        # ====================================================
        # STEP 15
        # BUILD RESULT
        # ====================================================

        result = {

            "row_number":
                row_number,

            "status":
                row_status,


            "class_ocr": {

                "normal":
                    ocr_result["class"],

                "selected":
                    class_selection.selected_text,

                "source":
                    class_selection.source,

                "evidence_score":
                    class_selection.evidence_score
            },


            "ocr": {

                "room":
                    ocr_result["room"],

                "subject":
                    ocr_result["subject"],

                "staff":
                    ocr_result["staff_name"]
            },


            "subject_second_pass": {

                "ocr_text":
                    (
                        best_subject_second_pass[
                            "ocr_text"
                        ]
                        if
                        best_subject_second_pass
                        else
                        None
                    ),

                "candidate":
                    (
                        best_subject_second_pass[
                            "raw_subject_candidate"
                        ]
                        if
                        best_subject_second_pass
                        else
                        None
                    ),

                "accepted_subject":
                    (
                        best_subject_second_pass[
                            "subject"
                        ]
                        if
                        best_subject_second_pass
                        else
                        None
                    ),

                "score":
                    (
                        round(
                            best_subject_second_pass[
                                "score"
                            ],
                            2
                        )
                        if
                        best_subject_second_pass
                        else
                        0.0
                    )
            },


            "selected_subject": {

                "value":
                    selected_subject_text,

                "source":
                    selected_subject_source,

                "confidence":
                    round(
                        selected_subject_score,
                        2
                    )
            },


            "parsed": {

                "semester":
                    class_result.semester,

                "division":
                    class_result.division,

                "day":
                    class_result.day,

                "month":
                    class_result.month,

                "start_time":
                    start_time,

                "end_time":
                    end_time,

                "room":
                    field_result.room_number,

                "room_candidates":
                    field_result.room_candidates,

                "subject":
                    selected_subject_text,

                "staff":
                    field_result.staff_name_raw
            },


            "semester_hint": {

                "semester":
                    semester_hint.semester,

                "subject_candidate":
                    semester_hint.subject_candidate,

                "subject_score":
                    round(
                        semester_hint.subject_score,
                        2
                    ),

                "room_score":
                    round(
                        semester_hint.room_score,
                        2
                    ),

                "combined_score":
                    round(
                        semester_hint.combined_score,
                        2
                    ),

                "requires_review":
                    semester_hint.requires_review
            },


            "academic_match":
                None,

            "timetable":
                None,

            "rejected_timetable_candidate":
                None,

            "substitute":
                None,

            "requires_review":
                True
        }


        # ====================================================
        # STEP 16
        # STORE ACADEMIC MATCH
        # ====================================================

        if academic_candidate:

            result[
                "academic_match"
            ] = {

                "semester":
                    academic_candidate.semester,

                "subject_code":
                    academic_candidate.subject_code,

                "subject_name":
                    academic_candidate.subject_name,

                "room":
                    academic_candidate.room,

                "teacher_code":
                    academic_candidate.teacher_code,

                "subject_score":
                    round(
                        academic_candidate.subject_score,
                        2
                    ),

                "room_score":
                    round(
                        academic_candidate.room_score,
                        2
                    ),

                "total_score":
                    round(
                        academic_candidate.total_score,
                        2
                    ),

                "subject_accepted":
                    academic_candidate.subject_accepted,

                "requires_review":
                    academic_candidate.requires_review
            }


        # ====================================================
        # STEP 17
        # STORE REJECTED TIMETABLE CANDIDATE
        # ====================================================

        if (
            raw_best_timetable
            is not None
            and
            best_timetable
            is None
        ):

            result[
                "rejected_timetable_candidate"
            ] = {

                "semester":
                    raw_best_timetable.semester,

                "subject":
                    raw_best_timetable.subject,

                "room":
                    raw_best_timetable.room,

                "faculty":
                    raw_best_timetable.faculty,

                "confidence":
                    round(
                        raw_best_timetable.total_score,
                        2
                    ),

                "reason":
                    "Below timetable confidence threshold"
            }


        # ====================================================
        # STEP 18
        # STORE ACCEPTED TIMETABLE
        # ====================================================

        if best_timetable:

            result[
                "timetable"
            ] = {

                "semester":
                    best_timetable.semester,

                "division":
                    best_timetable.division,

                "day":
                    best_timetable.day,

                "start_time":
                    best_timetable.start_time,

                "end_time":
                    best_timetable.end_time,

                "room":
                    best_timetable.room,

                "subject":
                    best_timetable.subject,

                "normal_faculty":
                    best_timetable.faculty,

                "confidence":
                    round(
                        best_timetable.total_score,
                        2
                    )
            }


        # ====================================================
        # STEP 19
        # STORE SUBSTITUTE
        # ====================================================

        if staff_match.matched_staff:

            result[
                "substitute"
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

                "accepted":
                    staff_is_reliable,

                "requires_review":
                    not staff_is_reliable
            }


        final_results.append(
            result
        )


        # ====================================================
        # STEP 20
        # DISPLAY FINAL VALIDATION
        # ====================================================

        print()
        print(
            "VALIDATION"
        )


        if best_timetable:

            print(
                "Accepted exact timetable match"
            )

            print(
                "Semester:",
                best_timetable.semester
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
                "Confidence:",
                round(
                    best_timetable.total_score,
                    2
                )
            )


        elif raw_best_timetable:

            print(
                "Timetable candidate rejected"
            )

            print(
                "Candidate:",
                raw_best_timetable.subject
            )

            print(
                "Confidence:",
                round(
                    raw_best_timetable.total_score,
                    2
                )
            )

            print(
                "Required:",
                TIMETABLE_ACCEPT_THRESHOLD
            )


        else:

            print(
                "No exact timetable candidate"
            )


        # ====================================================
        # ACADEMIC SUGGESTION
        # ====================================================

        if academic_candidate:

            print()
            print(
                "Academic suggestion:"
            )

            print(
                "Semester:",
                academic_candidate.semester
            )

            print(
                "Subject:",
                (
                    academic_candidate.subject_code
                    if
                    academic_candidate.subject_accepted
                    else
                    "UNKNOWN"
                )
            )

            print(
                "Room:",
                academic_candidate.room
            )

            print(
                "Subject Confidence:",
                round(
                    academic_candidate.subject_score,
                    2
                )
            )

            print(
                "Combined Confidence:",
                round(
                    academic_candidate.total_score,
                    2
                )
            )


        # ====================================================
        # SUBSTITUTE
        # ====================================================

        if staff_match.matched_staff:

            print()
            print(
                "Substitute suggestion:",
                staff_match.matched_staff.name
            )

            print(
                "Email:",
                staff_match.matched_staff.email
            )

            print(
                "Confidence:",
                round(
                    staff_match.score,
                    2
                )
            )

            print(
                "Accepted:",
                staff_is_reliable
            )


        print()
        print(
            "Row Status:",
            row_status
        )


    # ========================================================
    # SUMMARY COUNTS
    # ========================================================

    exact_count = sum(

        1

        for item in final_results

        if item["status"]
        ==
        "VALIDATED_WITH_REVIEW"
    )


    academic_count = sum(

        1

        for item in final_results

        if item["status"]
        ==
        "ACADEMIC_MATCH_REVIEW"
    )


    manual_count = sum(

        1

        for item in final_results

        if item["status"]
        ==
        "MANUAL_REVIEW_REQUIRED"
    )


    print()
    print(
        "========================================"
    )
    print(
        "FINAL SUMMARY"
    )
    print(
        "========================================"
    )

    print(
        "Total assignments:",
        len(
            final_results
        )
    )

    print(
        "Exact timetable matches:",
        exact_count
    )

    print(
        "Academic review matches:",
        academic_count
    )

    print(
        "Manual review required:",
        manual_count
    )

    print(
        "========================================"
    )


    # ========================================================
    # GROUPED EMAIL PREVIEWS
    # ========================================================

    grouped_email_previews = (
        generate_grouped_email_previews(

            final_results,

            year=
                year
        )
    )


    print()
    print(
        "Grouped email previews generated:",
        len(
            grouped_email_previews
        )
    )


    print_grouped_email_previews(
        grouped_email_previews
    )


    # ========================================================
    # RETURN
    # ========================================================

    return {

        "assignments":
            final_results,

        "grouped_emails":
            grouped_email_previews,

        "summary": {

            "total":
                len(
                    final_results
                ),

            "exact":
                exact_count,

            "academic_review":
                academic_count,

            "manual_review":
                manual_count,

            "emails":
                len(
                    grouped_email_previews
                )
        }
    }


# ============================================================
# CURRENT TEST FORM
# ============================================================

if __name__ == "__main__":

    process_all_rows(

        applicant_name=
            "Anand K. Patel",

        year=
            2026
    )