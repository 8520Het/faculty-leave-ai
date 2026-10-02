from datetime import datetime


def format_time(time_24h: str) -> str:
    """
    Convert 24-hour HH:MM to readable 12-hour format.
    Example:
    14:30 -> 2:30 PM
    """

    value = datetime.strptime(
        time_24h,
        "%H:%M"
    )

    return value.strftime(
        "%I:%M %p"
    ).lstrip("0")


def generate_email_preview(
    substitute_name: str,
    substitute_email: str,
    applicant_name: str,
    semester: int,
    division: str,
    lecture_day: int,
    lecture_month: str,
    lecture_year: int,
    start_time: str,
    end_time: str,
    room: str,
    subject: str
):

    start_display = format_time(
        start_time
    )

    end_display = format_time(
        end_time
    )

    subject_line = (
        f"Lecture Arrangement - "
        f"Sem {semester}-{division} - "
        f"{lecture_day} {lecture_month}"
    )

    body = f"""
Respected {substitute_name},

According to the submitted faculty leave arrangement, you have been listed to engage the following lecture:

Semester: {semester}-{division}
Date: {lecture_day} {lecture_month} {lecture_year}
Time: {start_display} - {end_display}
Room: {room}
Subject: {subject}

This lecture is normally assigned to {applicant_name}.

Please review the above arrangement.

Regards,
Faculty Leave Management System
""".strip()

    return {
        "to": substitute_email,
        "subject": subject_line,
        "body": body
    }


if __name__ == "__main__":

    email = generate_email_preview(

        substitute_name="Sandeep R. Suthar",

        substitute_email="sandeep.suthar@ddu.ac.in",

        applicant_name="Harshad B. Prajapati",

        semester=7,
        division="F",

        lecture_day=3,
        lecture_month="AUG",
        lecture_year=2026,

        start_time="14:30",
        end_time="15:30",

        room="26",
        subject="AJT"
    )

    print()
    print("====================================")
    print("EMAIL PREVIEW")
    print("====================================")

    print()
    print("To:")
    print(email["to"])

    print()
    print("Subject:")
    print(email["subject"])

    print()
    print("Body:")
    print()
    print(email["body"])

    print()
    print("====================================")