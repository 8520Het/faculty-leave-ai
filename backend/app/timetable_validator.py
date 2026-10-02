from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Optional

from timetable import (
    SEMESTER_ROOMS,
    get_active_semesters,
    find_matching_slots
)

from academic_master import SUBJECTS


# ============================================================
# THRESHOLDS
# ============================================================

SUBJECT_ACCEPT_THRESHOLD = 0.60


# ============================================================
# NORMALIZATION
# ============================================================

def normalize_text(
    value: Optional[str]
) -> str:

    if not value:
        return ""

    value = value.upper()

    replacements = {
        ".": "",
        ",": "",
        '"': "",
        "'": "",
        "-": "",
        "_": "",
        " ": ""
    }

    for old, new in replacements.items():

        value = value.replace(
            old,
            new
        )

    return value.strip()


# ============================================================
# SIMILARITY
# ============================================================

def similarity(
    a: Optional[str],
    b: Optional[str]
) -> float:

    if not a or not b:
        return 0.0

    return SequenceMatcher(
        None,
        normalize_text(a),
        normalize_text(b)
    ).ratio()


# ============================================================
# RESULT OBJECTS
# ============================================================

@dataclass
class RankedTimetableMatch:
    semester: int
    division: str

    day: str

    start_time: str
    end_time: str

    room: str

    subject: str
    faculty: str

    subject_score: float
    room_score: float
    faculty_score: float

    total_score: float


@dataclass
class SemesterHint:
    semester: Optional[int]

    subject_candidate: Optional[str]

    subject_score: float
    room_score: float

    combined_score: float

    reason: str

    requires_review: bool


# ============================================================
# CLEAN ROOM
# ============================================================

def clean_room(
    raw_room: Optional[str]
) -> str:

    if not raw_room:
        return ""

    return "".join(
        character
        for character in raw_room
        if character.isdigit()
    )


# ============================================================
# SEMESTER HINT
# ============================================================

def infer_semester_from_subject_room(
    subject_ocr: Optional[str],
    room_ocr: Optional[str]
) -> SemesterHint:

    active_semesters = (
        get_active_semesters()
    )

    cleaned_room = clean_room(
        room_ocr
    )

    best_semester = None
    best_subject = None

    best_subject_score = 0.0
    best_room_score = 0.0
    best_combined = 0.0


    for subject in SUBJECTS:

        if (
            subject.semester
            not in active_semesters
        ):
            continue


        code_score = similarity(
            subject_ocr,
            subject.code
        )

        name_score = similarity(
            subject_ocr,
            subject.name
        )

        subject_score = max(
            code_score,
            name_score
        )


        expected_room = (
            SEMESTER_ROOMS.get(
                subject.semester
            )
        )


        room_score = 0.0

        if (
            cleaned_room
            and expected_room
            and cleaned_room == expected_room
        ):

            room_score = 1.0


        combined_score = (
            subject_score * 0.65
            +
            room_score * 0.35
        )


        if (
            combined_score
            > best_combined
        ):

            best_combined = (
                combined_score
            )

            best_semester = (
                subject.semester
            )

            best_subject_score = (
                subject_score
            )

            best_room_score = (
                room_score
            )

            if (
                subject_score
                >= SUBJECT_ACCEPT_THRESHOLD
            ):

                best_subject = (
                    subject.code
                )

            else:

                best_subject = None


    if best_semester is None:

        return SemesterHint(

            semester=None,

            subject_candidate=None,

            subject_score=0.0,

            room_score=0.0,

            combined_score=0.0,

            reason=
                "No useful academic evidence.",

            requires_review=True
        )


    # --------------------------------------------------------
    # Decision explanation
    # --------------------------------------------------------

    if (
        best_room_score == 1.0
        and
        best_subject_score
        >= SUBJECT_ACCEPT_THRESHOLD
    ):

        reason = (
            "Room and subject both support "
            "the academic candidate."
        )

    elif (
        best_room_score == 1.0
        and
        best_subject_score
        < SUBJECT_ACCEPT_THRESHOLD
    ):

        reason = (
            "Room suggests the semester, "
            "but subject OCR is too weak "
            "to identify the subject."
        )

    elif (
        best_subject_score
        >= SUBJECT_ACCEPT_THRESHOLD
    ):

        reason = (
            "Subject is plausible, "
            "but room does not support it."
        )

    else:

        reason = (
            "Evidence is weak and requires "
            "manual review."
        )


    return SemesterHint(

        semester=
            best_semester,

        subject_candidate=
            best_subject,

        subject_score=
            best_subject_score,

        room_score=
            best_room_score,

        combined_score=
            best_combined,

        reason=
            reason,

        requires_review=
            True
    )


# ============================================================
# TIMETABLE RANKING
# ============================================================

def rank_timetable_matches(
    semester,
    division,
    day,
    month,
    year,
    start_time,
    end_time,
    room_ocr,
    subject_ocr,
    applicant_name
):

    semester_hint = (
        infer_semester_from_subject_room(

            subject_ocr=
                subject_ocr,

            room_ocr=
                room_ocr
        )
    )


    effective_semester = semester


    # --------------------------------------------------------
    # We may use room-supported semester as a filtering hint.
    #
    # It still does NOT validate the exact lecture.
    # --------------------------------------------------------

    if (
        effective_semester is None
        and
        semester_hint.semester
        is not None
        and
        semester_hint.room_score == 1.0
    ):

        effective_semester = (
            semester_hint.semester
        )


    # --------------------------------------------------------
    # REQUIRE AT LEAST TWO CLASS CLUES
    # --------------------------------------------------------

    evidence_count = 0

    if effective_semester is not None:
        evidence_count += 1

    if division is not None:
        evidence_count += 1

    if (
        day is not None
        and month is not None
    ):
        evidence_count += 1

    if (
        start_time is not None
        and end_time is not None
    ):
        evidence_count += 1


    if evidence_count < 2:
        return []


    matches = find_matching_slots(

        semester=
            effective_semester,

        division=
            division,

        day=
            day,

        month=
            month,

        year=
            year,

        start_time=
            start_time,

        end_time=
            end_time
    )


    ranked = []


    for slot in matches:

        subject_score = similarity(
            subject_ocr,
            slot.subject
        )


        cleaned_room = clean_room(
            room_ocr
        )

        room_score = 0.0

        if (
            cleaned_room
            and slot.room
            and cleaned_room == slot.room
        ):

            room_score = 1.0


        faculty_score = similarity(
            applicant_name,
            slot.faculty
        )


        total_score = (
            subject_score * 0.40
            +
            room_score * 0.25
            +
            faculty_score * 0.35
        )


        ranked.append(

            RankedTimetableMatch(

                semester=
                    slot.semester,

                division=
                    slot.division,

                day=
                    slot.day,

                start_time=
                    slot.start_time,

                end_time=
                    slot.end_time,

                room=
                    slot.room,

                subject=
                    slot.subject,

                faculty=
                    slot.faculty,

                subject_score=
                    subject_score,

                room_score=
                    room_score,

                faculty_score=
                    faculty_score,

                total_score=
                    total_score
            )
        )


    ranked.sort(
        key=lambda item:
            item.total_score,
        reverse=True
    )

    return ranked