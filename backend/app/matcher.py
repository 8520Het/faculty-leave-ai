from difflib import SequenceMatcher
from dataclasses import dataclass
from typing import Optional


# ============================================================
# SAMPLE MASTER DATA
# Later this will come from PostgreSQL
# ============================================================

VALID_ROOMS = [
    "25",
    "26",
    "27",
    "101",
    "102",
    "201",
    "202"
]

VALID_SUBJECTS = [
    "AJT",
    "AI",
    "ML",
    "DBMS",
    "CN",
    "OS"
]

VALID_STAFF = [
    "Sandeep R. Suthar",
    "Neha Patel",
    "Amit Shah",
    "Rahul Mehta"
]


# ============================================================
# MATCH RESULT
# ============================================================

@dataclass
class MatchResult:
    raw_value: str
    matched_value: Optional[str]
    score: float
    requires_review: bool


# ============================================================
# SIMILARITY
# ============================================================

def similarity(a: str, b: str) -> float:

    a = a.lower().strip()
    b = b.lower().strip()

    return SequenceMatcher(
        None,
        a,
        b
    ).ratio()


# ============================================================
# GENERIC MATCHER
# ============================================================

def best_match(
    raw_value: str,
    candidates: list[str],
    auto_accept_threshold: float = 0.90
) -> MatchResult:

    if not raw_value:
        return MatchResult(
            raw_value=raw_value,
            matched_value=None,
            score=0.0,
            requires_review=True
        )

    best_candidate = None
    best_score = 0.0

    for candidate in candidates:

        score = similarity(
            raw_value,
            candidate
        )

        if score > best_score:

            best_score = score
            best_candidate = candidate

    requires_review = (
        best_score < auto_accept_threshold
    )

    return MatchResult(
        raw_value=raw_value,
        matched_value=best_candidate,
        score=best_score,
        requires_review=requires_review
    )


# ============================================================
# FIELD-SPECIFIC MATCHERS
# ============================================================

def match_room(raw_room: str) -> MatchResult:

    return best_match(
        raw_room,
        VALID_ROOMS,
        auto_accept_threshold=0.95
    )


def match_subject(raw_subject: str) -> MatchResult:

    return best_match(
        raw_subject,
        VALID_SUBJECTS,
        auto_accept_threshold=0.80
    )


def match_staff(raw_staff: str) -> MatchResult:

    return best_match(
        raw_staff,
        VALID_STAFF,
        auto_accept_threshold=0.85
    )


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    room = match_room(
        "25"
    )

    subject = match_subject(
        "ATTS"
    )

    staff = match_staff(
        "Sandeep R. Kuthorff"
    )


    print()
    print("ROOM MATCH")
    print(room)

    print()
    print("SUBJECT MATCH")
    print(subject)

    print()
    print("STAFF MATCH")
    print(staff)