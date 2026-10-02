from pathlib import Path
from dataclasses import dataclass

from ocr_fields import ocr_assignment_row
from class_ocr import ocr_class_second_pass
from parser import parse_class_field


# ============================================================
# RESULT
# ============================================================

@dataclass
class ClassSelectionResult:
    selected_text: str
    source: str
    evidence_score: int
    parsed_result: object


# ============================================================
# SCORE PARSED CLASS INFORMATION
# ============================================================

def calculate_evidence_score(parsed):

    score = 0

    if parsed.semester is not None:
        score += 1

    if parsed.division is not None:
        score += 1

    if (
        parsed.day is not None
        and parsed.month is not None
    ):
        score += 2

    if parsed.start_time is not None:
        score += 1

    if parsed.end_time is not None:
        score += 1

    return score


# ============================================================
# CHOOSE BEST CLASS OCR
# ============================================================

def choose_best_class_ocr(
    row_image_path
):

    # --------------------------------------------------------
    # Normal OCR
    # --------------------------------------------------------

    normal_ocr = ocr_assignment_row(
        row_image_path
    )["class"]

    normal_parsed = parse_class_field(
        normal_ocr
    )

    normal_score = calculate_evidence_score(
        normal_parsed
    )


    # --------------------------------------------------------
    # Second-pass OCR
    # --------------------------------------------------------

    second_ocr = ocr_class_second_pass(
        row_image_path
    )

    second_parsed = parse_class_field(
        second_ocr
    )

    second_score = calculate_evidence_score(
        second_parsed
    )


    # --------------------------------------------------------
    # Choose whichever produced more structured evidence
    # --------------------------------------------------------

    if second_score > normal_score:

        return ClassSelectionResult(
            selected_text=second_ocr,
            source="second_pass",
            evidence_score=second_score,
            parsed_result=second_parsed
        )

    return ClassSelectionResult(
        selected_text=normal_ocr,
        source="normal",
        evidence_score=normal_score,
        parsed_result=normal_parsed
    )


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    BASE_DIR = (
        Path(__file__)
        .resolve()
        .parent
        .parent
        .parent
    )

    ROW_DIR = (
        BASE_DIR
        / "data"
        / "crops"
        / "detected_rows"
    )

    rows = [
        ROW_DIR / "assignment_row_2.jpg",
        ROW_DIR / "assignment_row_3.jpg"
    ]


    print()
    print("========================================")
    print("CLASS OCR SELECTION")
    print("========================================")


    for row_path in rows:

        result = choose_best_class_ocr(
            row_path
        )

        parsed = result.parsed_result

        print()
        print("----------------------------------------")
        print(row_path.name)
        print("----------------------------------------")

        print(
            "Selected source:",
            result.source
        )

        print(
            "Selected OCR:",
            result.selected_text
        )

        print(
            "Evidence score:",
            result.evidence_score
        )

        print()
        print("PARSED")

        print(
            "Semester:",
            parsed.semester
        )

        print(
            "Division:",
            parsed.division
        )

        print(
            "Day:",
            parsed.day
        )

        print(
            "Month:",
            parsed.month
        )

        print(
            "Start:",
            parsed.start_time
        )

        print(
            "End:",
            parsed.end_time
        )

        print(
            "Requires review:",
            parsed.requires_review
        )