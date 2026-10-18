from collections import defaultdict
from datetime import datetime


# ============================================================
# TIME FORMATTER
# ============================================================

def format_time(time_24h):

    if not time_24h:
        return "Unknown"

    try:

        value = datetime.strptime(
            time_24h,
            "%H:%M"
        )

        return value.strftime(
            "%I:%M %p"
        ).lstrip("0")

    except ValueError:

        return time_24h


# ============================================================
# GROUP ASSIGNMENTS BY SUBSTITUTE EMAIL
# ============================================================

def group_assignments_by_substitute(
    final_results
):

    grouped = defaultdict(list)


    for result in final_results:

        # Only use rows that successfully reached
        # the validated stage.
        if result.get("status") not in {
            "VALIDATED_WITH_REVIEW",
            "ACADEMIC_MATCH_REVIEW",
            "REVIEWED",
            "APPROVED",
        }:
            continue


        timetable = result.get("timetable") or {}
        substitute = result.get("substitute") or {}
        parsed = result.get("parsed") or {}

        email = substitute.get("email")
        semester = timetable.get("semester") or parsed.get("semester")
        division = timetable.get("division") or parsed.get("division")
        subject = timetable.get("subject") or parsed.get("subject")
        room = timetable.get("room") or parsed.get("room")
        start_time = timetable.get("start_time") or parsed.get("start_time")
        end_time = timetable.get("end_time") or parsed.get("end_time")

        if not email or semester is None or not subject:
            continue

        grouped[email].append(
            {
                "row_number": result.get("row_number"),
                "substitute_name": substitute.get("name"),
                "semester": semester,
                "division": division,
                "lecture_day": parsed.get("day"),
                "lecture_month": parsed.get("month"),
                "start_time": start_time,
                "end_time": end_time,
                "room": room,
                "subject": subject,
                "normal_faculty": timetable.get("normal_faculty")
                or result.get("applicant_name"),
            }
        )


    return grouped


# ============================================================
# GENERATE GROUPED EMAILS
# ============================================================

def generate_grouped_email_previews(
    final_results,
    year
):

    grouped = group_assignments_by_substitute(
        final_results
    )

    email_previews = []


    for email, assignments in grouped.items():

        if not assignments:
            continue


        substitute_name = assignments[
            0
        ]["substitute_name"]


        # ----------------------------------------------------
        # SUBJECT
        # ----------------------------------------------------

        if len(assignments) == 1:

            assignment = assignments[0]

            subject_line = (
                f"Lecture Arrangement - "
                f"Sem {assignment['semester']}-"
                f"{assignment['division']}"
            )

        else:

            subject_line = (
                f"Lecture Arrangements - "
                f"{len(assignments)} Lectures"
            )


        # ----------------------------------------------------
        # BODY
        # ----------------------------------------------------

        body_lines = [

            f"Dear {substitute_name},",

            "",

            (
                "According to the submitted faculty leave "
                "arrangement, you have been listed to engage "
                "the following lecture"
                + (
                    ":"
                    if len(assignments) == 1
                    else "s:"
                )
            ),

            ""
        ]


        # ----------------------------------------------------
        # ADD EACH ASSIGNMENT
        # ----------------------------------------------------

        for index, assignment in enumerate(
            assignments,
            start=1
        ):

            start_display = format_time(
                assignment[
                    "start_time"
                ]
            )

            end_display = format_time(
                assignment[
                    "end_time"
                ]
            )


            body_lines.extend(
                [
                    (
                        f"{index}. "
                        f"Sem "
                        f"{assignment['semester']}-"
                        f"{assignment['division']}"
                    ),

                    (
                        f"   Date: "
                        f"{assignment['lecture_day']} "
                        f"{assignment['lecture_month']} "
                        f"{year}"
                    ),

                    (
                        f"   Time: "
                        f"{start_display} - "
                        f"{end_display}"
                    ),

                    (
                        f"   Room: "
                        f"{assignment['room']}"
                    ),

                    (
                        f"   Subject: "
                        f"{assignment['subject']}"
                    ),

                    (
                        f"   Normally assigned to: "
                        f"{assignment['normal_faculty']}"
                    ),

                    ""
                ]
            )


        body_lines.extend(
            [
                (
                    "Please review the above arrangement."
                ),

                "",

                "Regards,",

                (
                    "Faculty Leave Management System"
                )
            ]
        )


        body = "\n".join(
            body_lines
        )


        email_previews.append(
            {
                "to":
                    email,

                "substitute_name":
                    substitute_name,

                "assignment_count":
                    len(assignments),

                "subject":
                    subject_line,

                "body":
                    body
            }
        )


    return email_previews


# ============================================================
# DISPLAY GROUPED EMAILS
# ============================================================

def print_grouped_email_previews(
    email_previews
):

    print()
    print("========================================")
    print("GROUPED EMAIL PREVIEWS")
    print("========================================")


    if not email_previews:

        print(
            "No grouped emails could be generated."
        )

        return


    for index, email in enumerate(
        email_previews,
        start=1
    ):

        print()
        print("----------------------------------------")
        print(
            f"EMAIL {index}"
        )
        print("----------------------------------------")

        print(
            "To:",
            email["to"]
        )

        print(
            "Assignments:",
            email["assignment_count"]
        )

        print()
        print(
            "Subject:"
        )

        print(
            email["subject"]
        )

        print()
        print(
            "Body:"
        )

        print()

        print(
            email["body"]
        )


# ============================================================
# SIMPLE TEST
# ============================================================

if __name__ == "__main__":

    sample_results = [

        {
            "row_number": 2,

            "status":
                "VALIDATED_WITH_REVIEW",

            "parsed": {
                "day": 3,
                "month": "AUG"
            },

            "timetable": {
                "semester": 7,
                "division": "F",
                "start_time": "14:30",
                "end_time": "15:30",
                "room": "26",
                "subject": "AJT",
                "normal_faculty":
                    "Harshad B. Prajapati"
            },

            "substitute": {
                "name":
                    "Sandeep R. Suthar",

                "email":
                    "sandeep.suthar@ddu.ac.in"
            }
        },


        {
            "row_number": 4,

            "status":
                "VALIDATED_WITH_REVIEW",

            "parsed": {
                "day": 3,
                "month": "AUG"
            },

            "timetable": {
                "semester": 7,
                "division": "F",
                "start_time": "15:30",
                "end_time": "16:30",
                "room": "27",
                "subject": "AI",
                "normal_faculty":
                    "Harshad B. Prajapati"
            },

            "substitute": {
                "name":
                    "Sandeep R. Suthar",

                "email":
                    "sandeep.suthar@ddu.ac.in"
            }
        }
    ]


    previews = generate_grouped_email_previews(
        sample_results,
        year=2026
    )


    print_grouped_email_previews(
        previews
    )