from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Optional

from staff_master import STAFF_MASTER, StaffMember


@dataclass
class StaffMatchResult:
    raw_name: str
    matched_staff: Optional[StaffMember]
    score: float
    requires_review: bool


def normalize_name(name: str) -> str:
    return (
        name.lower()
        .replace(".", "")
        .replace(",", "")
        .strip()
    )


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(
        None,
        normalize_name(a),
        normalize_name(b)
    ).ratio()


def match_staff_member(
    raw_name: str,
    auto_accept_threshold: float = 0.90
) -> StaffMatchResult:

    best_staff = None
    best_score = 0.0

    for staff in STAFF_MASTER:

        score = similarity(
            raw_name,
            staff.name
        )

        if score > best_score:
            best_score = score
            best_staff = staff

    requires_review = (
        best_staff is None
        or best_score < auto_accept_threshold
    )

    return StaffMatchResult(
        raw_name=raw_name,
        matched_staff=best_staff,
        score=best_score,
        requires_review=requires_review
    )


if __name__ == "__main__":

    raw_ocr_name = "Sandeep R. Kuthorff"

    result = match_staff_member(
        raw_ocr_name
    )

    print()
    print("====================================")
    print("STAFF MATCH")
    print("====================================")

    print("OCR Name:", result.raw_name)

    if result.matched_staff:

        print(
            "Suggested Name:",
            result.matched_staff.name
        )

        print(
            "Email:",
            result.matched_staff.email
        )

        print(
            "Department:",
            result.matched_staff.department
        )

    else:
        print("No staff member matched")

    print(
        "Score:",
        round(result.score, 2)
    )

    print(
        "Requires Review:",
        result.requires_review
    )

    print("====================================")