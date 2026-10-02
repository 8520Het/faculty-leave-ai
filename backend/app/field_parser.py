import re
from dataclasses import dataclass
from typing import Optional, List

from timetable import SEMESTER_ROOMS


# ============================================================
# STRUCTURED OUTPUT
# ============================================================

@dataclass
class ParsedAssignment:
    room_number: Optional[str]
    room_candidates: List[str]

    subject: Optional[str]
    staff_name_raw: Optional[str]

    room_requires_review: bool
    subject_requires_review: bool
    staff_requires_review: bool

    requires_review: bool


# ============================================================
# BASIC NORMALIZATION
# ============================================================

def normalize_text(
    text: str
) -> str:

    if not text:
        return ""

    text = text.strip()

    text = text.replace(
        '"',
        ''
    )

    text = text.replace(
        "'",
        ''
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# VALID ROOM MASTER
# ============================================================

VALID_ROOMS = set(
    SEMESTER_ROOMS.values()
)


# ============================================================
# ROOM CANDIDATES
# ============================================================

def extract_room_candidates(
    raw_text: str
) -> List[str]:

    text = normalize_text(
        raw_text
    )

    matches = re.findall(
        r"\b\d{1,4}\b",
        text
    )

    candidates = []

    for match in matches:

        if match not in candidates:

            candidates.append(
                match
            )

    return candidates


# ============================================================
# CHOOSE ROOM
# ============================================================

def choose_room_candidate(
    candidates: List[str]
) -> Optional[str]:

    if not candidates:
        return None


    # --------------------------------------------------------
    # Prefer a room that exists in our configured room master.
    # --------------------------------------------------------

    for candidate in candidates:

        if candidate in VALID_ROOMS:

            return candidate


    # --------------------------------------------------------
    # Otherwise retain first OCR candidate,
    # but downstream validation will mark it uncertain.
    # --------------------------------------------------------

    return candidates[0]


# ============================================================
# ROOM PARSER
# ============================================================

def parse_room(
    raw_text: str
):

    candidates = extract_room_candidates(
        raw_text
    )

    selected = choose_room_candidate(
        candidates
    )

    return (
        selected,
        candidates
    )


# ============================================================
# SUBJECT PARSER
# ============================================================

def parse_subject(
    raw_text: str
) -> Optional[str]:

    text = normalize_text(
        raw_text
    ).upper()

    text = re.sub(
        r"[^A-Z0-9 ]",
        "",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    if not text:
        return None

    return text


# ============================================================
# STAFF PARSER
# ============================================================

def parse_staff_name(
    raw_text: str
) -> Optional[str]:

    text = normalize_text(
        raw_text
    )

    text = re.sub(
        r"[^A-Za-z. ]",
        "",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    if not text:
        return None

    return text


# ============================================================
# MAIN
# ============================================================

def parse_assignment_fields(
    room_text: str,
    subject_text: str,
    staff_text: str
) -> ParsedAssignment:

    (
        room,
        room_candidates
    ) = parse_room(
        room_text
    )


    subject = parse_subject(
        subject_text
    )


    staff_name = parse_staff_name(
        staff_text
    )


    # ========================================================
    # ROOM REVIEW
    # ========================================================

    room_requires_review = True

    if (
        room is not None
        and
        room in VALID_ROOMS
    ):

        room_requires_review = False


    # ========================================================
    # SUBJECT / STAFF REVIEW
    # ========================================================

    subject_requires_review = (
        subject is None
    )

    staff_requires_review = (
        staff_name is None
    )


    # ========================================================
    # OVERALL
    #
    # OCR output always stays reviewable until validation.
    # ========================================================

    requires_review = True


    return ParsedAssignment(

        room_number=
            room,

        room_candidates=
            room_candidates,

        subject=
            subject,

        staff_name_raw=
            staff_name,

        room_requires_review=
            room_requires_review,

        subject_requires_review=
            subject_requires_review,

        staff_requires_review=
            staff_requires_review,

        requires_review=
            requires_review
    )


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    tests = [

        "25 .",

        "30 25",

        ". 26 .",

        "Room 27",

        "99",

        ""
    ]


    for test in tests:

        room, candidates = parse_room(
            test
        )

        print()
        print(
            "Raw:",
            repr(test)
        )

        print(
            "Candidates:",
            candidates
        )

        print(
            "Selected:",
            room
        )