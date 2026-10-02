from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Optional

from academic_master import SUBJECTS
from timetable import (
    SEMESTER_ROOMS,
    get_active_semesters
)


# ============================================================
# THRESHOLDS
# ============================================================

SUBJECT_ACCEPT_THRESHOLD = 0.60
ACADEMIC_ACCEPT_THRESHOLD = 0.65


# ============================================================
# RESULT
# ============================================================

@dataclass
class AcademicCandidate:
    semester: Optional[int]

    subject_code: Optional[str]
    subject_name: Optional[str]

    teacher_code: Optional[str]

    room: Optional[str]

    subject_score: float
    room_score: float
    total_score: float

    subject_accepted: bool
    requires_review: bool


# ============================================================
# NORMALIZATION
# ============================================================

def normalize_text(
    value: Optional[str]
) -> str:

    if not value:
        return ""

    value = value.upper()

    for character in [
        ".",
        ",",
        '"',
        "'",
        "-",
        "_",
        "(",
        ")",
        "/",
        "\\"
    ]:

        value = value.replace(
            character,
            ""
        )

    value = value.replace(
        " ",
        ""
    )

    return value.strip()


# ============================================================
# SIMILARITY
# ============================================================

def similarity(
    first: Optional[str],
    second: Optional[str]
) -> float:

    first = normalize_text(
        first
    )

    second = normalize_text(
        second
    )

    if not first or not second:
        return 0.0

    return SequenceMatcher(
        None,
        first,
        second
    ).ratio()


# ============================================================
# CLEAN ROOM
# ============================================================

def clean_room(
    value: Optional[str]
) -> str:

    if not value:
        return ""

    return "".join(
        character
        for character in value
        if character.isdigit()
    )


# ============================================================
# FIND ACADEMIC CANDIDATES
# ============================================================

def find_academic_candidates(
    subject_ocr: Optional[str],
    room_ocr: Optional[str],
    limit: int = 5
):

    active_semesters = (
        get_active_semesters()
    )

    room_value = clean_room(
        room_ocr
    )

    candidates = []


    for subject in SUBJECTS:

        if (
            subject.semester
            not in active_semesters
        ):
            continue


        # ----------------------------------------------------
        # SUBJECT SIMILARITY
        # ----------------------------------------------------

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


        # ----------------------------------------------------
        # ROOM
        # ----------------------------------------------------

        expected_room = (
            SEMESTER_ROOMS.get(
                subject.semester,
                ""
            )
        )

        room_score = 0.0

        if (
            room_value
            and expected_room
            and room_value == expected_room
        ):

            room_score = 1.0


        # ----------------------------------------------------
        # COMBINED SCORE
        # ----------------------------------------------------

        total_score = (
            subject_score * 0.65
            +
            room_score * 0.35
        )


        # ----------------------------------------------------
        # IMPORTANT:
        #
        # Room may suggest semester,
        # but weak subject OCR must NOT decide subject.
        # ----------------------------------------------------

        subject_accepted = (
            subject_score
            >= SUBJECT_ACCEPT_THRESHOLD
        )


        candidates.append(

            AcademicCandidate(

                semester=
                    subject.semester,

                subject_code=
                    (
                        subject.code
                        if subject_accepted
                        else None
                    ),

                subject_name=
                    (
                        subject.name
                        if subject_accepted
                        else None
                    ),

                teacher_code=
                    (
                        subject.teacher_code
                        if subject_accepted
                        else None
                    ),

                room=
                    expected_room,

                subject_score=
                    subject_score,

                room_score=
                    room_score,

                total_score=
                    total_score,

                subject_accepted=
                    subject_accepted,

                requires_review=
                    True
            )
        )


    candidates.sort(
        key=lambda candidate:
            candidate.total_score,
        reverse=True
    )


    return candidates[:limit]


# ============================================================
# BEST CANDIDATE
# ============================================================

def get_best_academic_candidate(
    subject_ocr,
    room_ocr
):

    candidates = find_academic_candidates(

        subject_ocr=
            subject_ocr,

        room_ocr=
            room_ocr,

        limit=1
    )

    if not candidates:
        return None

    return candidates[0]


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    tests = [

        ("AJT", "26"),
        ("AD", "26"),
        ("DEVOPS", "25"),
        ("AT T", "25"),
        ("RAD", "25")
    ]


    for subject_ocr, room_ocr in tests:

        print()
        print("====================================")

        print(
            "OCR Subject:",
            subject_ocr
        )

        print(
            "OCR Room:",
            room_ocr
        )

        print("====================================")


        candidate = (
            get_best_academic_candidate(

                subject_ocr=
                    subject_ocr,

                room_ocr=
                    room_ocr
            )
        )


        if not candidate:

            print(
                "No candidate"
            )

            continue


        print(
            "Semester Hint:",
            candidate.semester
        )

        print(
            "Subject:",
            (
                candidate.subject_code
                if candidate.subject_code
                else "UNKNOWN"
            )
        )

        print(
            "Subject Score:",
            round(
                candidate.subject_score,
                2
            )
        )

        print(
            "Room Score:",
            round(
                candidate.room_score,
                2
            )
        )

        print(
            "Combined:",
            round(
                candidate.total_score,
                2
            )
        )

        print(
            "Subject Accepted:",
            candidate.subject_accepted
        )