import re
from dataclasses import dataclass
from typing import Optional


# ============================================================
# OUTPUT STRUCTURE
# ============================================================

@dataclass
class ParsedClassField:

    raw_text: str

    semester: Optional[int]
    division: Optional[str]

    day: Optional[int]
    month: Optional[str]

    start_time: Optional[str]
    end_time: Optional[str]

    requires_review: bool


# ============================================================
# MONTH NORMALIZATION
#
# OCR commonly confuses:
#
# Aug -> Avg
# Aug -> Auy
# ============================================================

MONTH_CORRECTIONS = {

    "JAN": "JAN",
    "JANUARY": "JAN",

    "FEB": "FEB",
    "FEBRUARY": "FEB",

    "MAR": "MAR",
    "MARCH": "MAR",

    "APR": "APR",
    "APRIL": "APR",

    "MAY": "MAY",

    "JUN": "JUN",
    "JUNE": "JUN",

    "JUL": "JUL",
    "JULY": "JUL",

    "AUG": "AUG",
    "AVG": "AUG",
    "AUQ": "AUG",
    "AUY": "AUG",
    "AUGUST": "AUG",

    "SEP": "SEP",
    "SEPT": "SEP",
    "SEPTEMBER": "SEP",

    "OCT": "OCT",
    "OCTOBER": "OCT",

    "NOV": "NOV",
    "NOVEMBER": "NOV",

    "DEC": "DEC",
    "DECEMBER": "DEC"
}


# ============================================================
# NORMALIZE OCR TEXT
# ============================================================

def normalize_text(text: str) -> str:

    text = text.upper()

    # Remove quotes
    text = text.replace('"', ' ')
    text = text.replace("'", " ")

    # Normalize long dashes
    text = text.replace("–", "-")
    text = text.replace("—", "-")

    # Normalize "to"
    text = re.sub(
        r"\bTO\b",
        "-",
        text
    )

    # Collapse spaces
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# EXTRACT SEMESTER + DIVISION
# ============================================================

def extract_semester_division(text: str):

    # Examples:
    #
    # SEM 7F
    # SEM 7-F
    # 7F
    # 7-F

    patterns = [

        r"\bSEM(?:ESTER)?\s*(\d{1,2})\s*[- ]?\s*([A-Z])\b",

        r"\b(\d{1,2})\s*[-]?\s*([A-Z])\b"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text
        )

        if match:

            semester = int(
                match.group(1)
            )

            division = match.group(2)

            return semester, division

    # Sometimes OCR sees something like:
    #
    # SEMI-F
    #
    # Division F is still recoverable,
    # but semester is uncertain.

    division_match = re.search(
        r"\bSEM[A-Z]*\s*[- ]?\s*([A-Z])\b",
        text
    )

    if division_match:

        return None, division_match.group(1)

    return None, None


# ============================================================
# EXTRACT DATE
# ============================================================

def extract_date(text: str):

    # First check textual dates:
    #
    # 3 AUG
    # 3 AVG
    # 03 AUGUST

    month_words = "|".join(
        MONTH_CORRECTIONS.keys()
    )

    match = re.search(
        rf"\b(\d{{1,2}})\s*({month_words})\b",
        text
    )

    if match:

        day = int(
            match.group(1)
        )

        detected_month = match.group(2)

        month = MONTH_CORRECTIONS[
            detected_month
        ]

        return day, month

    # Numeric date example:
    #
    # 03/08/26
    # 03-08-2026

    numeric_match = re.search(
        r"\b(\d{1,2})[-/](\d{1,2})(?:[-/](\d{2,4}))?\b",
        text
    )

    if numeric_match:

        day = int(
            numeric_match.group(1)
        )

        month_number = int(
            numeric_match.group(2)
        )

        month_lookup = {

            1: "JAN",
            2: "FEB",
            3: "MAR",
            4: "APR",
            5: "MAY",
            6: "JUN",
            7: "JUL",
            8: "AUG",
            9: "SEP",
            10: "OCT",
            11: "NOV",
            12: "DEC"
        }

        month = month_lookup.get(
            month_number
        )

        return day, month

    return None, None


# ============================================================
# EXTRACT TIME RANGE
# ============================================================

def extract_time_range(text: str):

    # Normalize OCR time separators.
    #
    # 2.30 -> 2:30

    time_text = re.sub(
        r"(?<=\d)[.](?=\d{2}\b)",
        ":",
        text
    )

    # Standard version:
    #
    # 2:30-3:30
    # 2:30 3:30

    times = re.findall(
        r"\b(\d{1,2})[:.](\d{2})\b",
        time_text
    )

    valid_times = []

    for hour_text, minute_text in times:

        hour = int(hour_text)
        minute = int(minute_text)

        if (
            1 <= hour <= 12
            and
            0 <= minute <= 59
        ):

            valid_times.append(
                f"{hour:02d}:{minute:02d}"
            )

    if len(valid_times) >= 2:

        return (
            valid_times[0],
            valid_times[1]
        )

    return None, None


# ============================================================
# MAIN CLASS PARSER
# ============================================================

def parse_class_field(
    raw_text: str
) -> ParsedClassField:

    normalized = normalize_text(
        raw_text
    )

    semester, division = (
        extract_semester_division(
            normalized
        )
    )

    day, month = extract_date(
        normalized
    )

    start_time, end_time = (
        extract_time_range(
            normalized
        )
    )

    requires_review = any(
        value is None
        for value in [
            semester,
            division,
            day,
            month,
            start_time,
            end_time
        ]
    )

    return ParsedClassField(

        raw_text=raw_text,

        semester=semester,
        division=division,

        day=day,
        month=month,

        start_time=start_time,
        end_time=end_time,

        requires_review=requires_review
    )


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    test_values = [

        # Perfect OCR
        "Sem 7F 3 Aug 2:30-3:30",

        # Your current TrOCR result
        "1 . Semi-F.3Avg 2.30.3.30. 2",

        # Other formats we expect
        "Sem 6-F 11 August 2:30 to 3:30",

        "6F 11 Aug 2.30-3.30"
    ]

    for value in test_values:

        print()
        print("====================================")

        print(
            "INPUT:",
            value
        )

        parsed = parse_class_field(
            value
        )

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