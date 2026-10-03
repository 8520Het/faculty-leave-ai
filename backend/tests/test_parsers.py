from parser import parse_class_field
from field_parser import parse_assignment_fields, parse_room
from grouped_email import generate_grouped_email_previews


def test_parse_class_field_recovers_ocr_noise():
    parsed = parse_class_field("1 . Semi-F.3Avg 2.30.3.30. 2")
    assert parsed.division == "F"
    assert parsed.day == 3
    assert parsed.month == "AUG"
    assert parsed.start_time == "02:30"
    assert parsed.end_time == "03:30"


def test_parse_room_prefers_known_master_room():
    room, candidates = parse_room("30 25")
    assert "25" in candidates
    assert room == "25"


def test_parse_assignment_fields():
    result = parse_assignment_fields("25 .", "AJT", "Sandeep R. Suthar")
    assert result.room_number == "25"
    assert result.subject == "AJT"
    assert "Sandeep" in result.staff_name_raw


def test_grouped_email_after_review():
    previews = generate_grouped_email_previews(
        [
            {
                "row_number": 2,
                "status": "REVIEWED",
                "parsed": {
                    "day": 3,
                    "month": "AUG",
                    "semester": 7,
                    "division": "F",
                    "subject": "AI",
                    "room": "25",
                    "start_time": "14:30",
                    "end_time": "15:30",
                },
                "substitute": {
                    "name": "Sandeep R. Suthar",
                    "email": "sandeep.suthar@ddu.ac.in",
                },
            }
        ],
        year=2026,
    )
    assert len(previews) == 1
    assert previews[0]["to"] == "sandeep.suthar@ddu.ac.in"
    assert "AI" in previews[0]["body"]
