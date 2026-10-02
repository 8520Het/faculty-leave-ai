from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

from academic_master import (
    SUBJECTS,
    FACULTY,
    get_subjects_for_semester
)


# ============================================================
# CONFIGURATION
# ============================================================

# Change this to "EVEN" when testing Sem 2 / 4 / 6.
ACTIVE_TERM = "ODD"


ODD_SEMESTERS = [1, 3, 5, 7]
EVEN_SEMESTERS = [2, 4, 6]


# ------------------------------------------------------------
# One room per semester for the current demo.
# Later this can come from the database.
# ------------------------------------------------------------

SEMESTER_ROOMS = {
    1: "21",
    2: "22",
    3: "23",
    4: "24",
    5: "26",
    6: "27",
    7: "25"
}


DIVISION = "F"


# ============================================================
# DAYS
# ============================================================

DAYS = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday"
]


# ============================================================
# DAY TYPES
#
# These are the four timing combinations requested.
# ============================================================

DAY_WINDOWS = {

    "EARLY_SHORT": {
        "start": "08:30",
        "end": "15:30"
    },

    "LATE_LONG": {
        "start": "10:30",
        "end": "17:30"
    },

    "LATE_SHORT": {
        "start": "10:30",
        "end": "15:30"
    },

    "EARLY_LONG": {
        "start": "08:30",
        "end": "17:30"
    }
}


# ============================================================
# DIFFERENT DAY PATTERNS FOR EACH SEMESTER
# ============================================================

SEMESTER_DAY_PATTERNS = {

    1: {
        "Monday": "EARLY_SHORT",
        "Tuesday": "LATE_LONG",
        "Wednesday": "EARLY_LONG",
        "Thursday": "LATE_SHORT",
        "Friday": "EARLY_SHORT"
    },

    2: {
        "Monday": "LATE_LONG",
        "Tuesday": "EARLY_LONG",
        "Wednesday": "EARLY_SHORT",
        "Thursday": "LATE_LONG",
        "Friday": "EARLY_SHORT"
    },

    3: {
        "Monday": "EARLY_LONG",
        "Tuesday": "EARLY_SHORT",
        "Wednesday": "LATE_LONG",
        "Thursday": "EARLY_LONG",
        "Friday": "LATE_SHORT"
    },

    4: {
        "Monday": "LATE_SHORT",
        "Tuesday": "EARLY_LONG",
        "Wednesday": "LATE_LONG",
        "Thursday": "EARLY_SHORT",
        "Friday": "EARLY_LONG"
    },

    5: {
        "Monday": "EARLY_SHORT",
        "Tuesday": "EARLY_LONG",
        "Wednesday": "LATE_LONG",
        "Thursday": "EARLY_LONG",
        "Friday": "LATE_SHORT"
    },

    6: {
        "Monday": "LATE_LONG",
        "Tuesday": "EARLY_SHORT",
        "Wednesday": "EARLY_LONG",
        "Thursday": "LATE_LONG",
        "Friday": "EARLY_SHORT"
    },

    7: {
        "Monday": "EARLY_LONG",
        "Tuesday": "LATE_LONG",
        "Wednesday": "EARLY_SHORT",
        "Thursday": "EARLY_LONG",
        "Friday": "LATE_SHORT"
    }
}


# ============================================================
# BREAK
# ============================================================

BREAK_START = "12:40"
BREAK_END = "13:30"


# ============================================================
# TIMETABLE SLOT
# ============================================================

@dataclass
class TimetableSlot:

    semester: int
    division: str

    day: str

    start_time: str
    end_time: str

    room: str

    subject: str
    subject_name: str

    component: str

    faculty: str
    faculty_code: str


# ============================================================
# TIME HELPERS
# ============================================================

def time_to_minutes(
    value: str
) -> int:

    hour, minute = map(
        int,
        value.split(":")
    )

    return (
        hour * 60
        + minute
    )


def minutes_to_time(
    minutes: int
) -> str:

    hour = minutes // 60
    minute = minutes % 60

    return (
        f"{hour:02d}:{minute:02d}"
    )


def add_minutes(
    value: str,
    amount: int
) -> str:

    return minutes_to_time(
        time_to_minutes(value)
        + amount
    )


# ============================================================
# CHECK BREAK OVERLAP
# ============================================================

def overlaps_break(
    start_time: str,
    end_time: str
) -> bool:

    start = time_to_minutes(
        start_time
    )

    end = time_to_minutes(
        end_time
    )

    break_start = time_to_minutes(
        BREAK_START
    )

    break_end = time_to_minutes(
        BREAK_END
    )

    return (
        start < break_end
        and
        end > break_start
    )


# ============================================================
# AVAILABLE 1-HOUR PERIODS FOR A DAY
# ============================================================

def get_hour_slots(
    semester: int,
    day: str
):

    pattern_name = (
        SEMESTER_DAY_PATTERNS[
            semester
        ][day]
    )

    window = DAY_WINDOWS[
        pattern_name
    ]

    start = time_to_minutes(
        window["start"]
    )

    end = time_to_minutes(
        window["end"]
    )

    slots = []

    current = start

    while current + 60 <= end:

        slot_start = minutes_to_time(
            current
        )

        slot_end = minutes_to_time(
            current + 60
        )

        if not overlaps_break(
            slot_start,
            slot_end
        ):

            slots.append(
                (
                    slot_start,
                    slot_end
                )
            )

        current += 60

    return slots


# ============================================================
# AVAILABLE 2-HOUR LAB BLOCKS
# ============================================================

def get_lab_slots(
    semester: int,
    day: str
):

    one_hour_slots = get_hour_slots(
        semester,
        day
    )

    lab_slots = []

    for index in range(
        len(one_hour_slots) - 1
    ):

        first = one_hour_slots[index]
        second = one_hour_slots[
            index + 1
        ]

        # Must be exactly consecutive.
        if first[1] != second[0]:
            continue

        start_time = first[0]
        end_time = second[1]

        if overlaps_break(
            start_time,
            end_time
        ):
            continue

        lab_slots.append(
            (
                start_time,
                end_time
            )
        )

    return lab_slots


# ============================================================
# OCCUPANCY HELPERS
# ============================================================

def occupied_keys(
    day: str,
    start_time: str,
    end_time: str
):

    keys = []

    current = time_to_minutes(
        start_time
    )

    end = time_to_minutes(
        end_time
    )

    while current < end:

        keys.append(
            (
                day,
                minutes_to_time(current)
            )
        )

        current += 60

    return keys


# ============================================================
# SESSION REQUIREMENTS
#
# Demo assumption:
#
# LECTURE  -> 2 periods / week
# TUTORIAL -> 1 period / week
# LAB      -> 1 two-hour block / week
# ============================================================

def build_required_sessions(
    semester: int
):

    sessions = []

    subjects = get_subjects_for_semester(
        semester
    )

    for subject in subjects:

        if "LAB" in subject.components:

            sessions.append(
                {
                    "subject": subject,
                    "component": "LAB",
                    "duration": 120
                }
            )

        if "TUTORIAL" in subject.components:

            sessions.append(
                {
                    "subject": subject,
                    "component": "TUTORIAL",
                    "duration": 60
                }
            )

        if "LECTURE" in subject.components:

            # Two lectures per week.
            for _ in range(2):

                sessions.append(
                    {
                        "subject": subject,
                        "component": "LECTURE",
                        "duration": 60
                    }
                )

    # Labs first because 2-hour blocks are harder to place.
    component_order = {
        "LAB": 0,
        "TUTORIAL": 1,
        "LECTURE": 2
    }

    sessions.sort(
        key=lambda item:
            component_order[
                item["component"]
            ]
    )

    return sessions


# ============================================================
# GENERATE TIMETABLE
# ============================================================

def generate_timetable():

    timetable = []

    # Semester occupancy:
    #
    # {
    #   semester:
    #       {("Monday", "08:30"), ...}
    # }
    semester_occupied = {
        semester: set()
        for semester in range(1, 8)
    }


    # Teacher occupancy:
    #
    # {
    #   "PRM":
    #       {("Monday", "08:30"), ...}
    # }
    teacher_occupied = {
        code: set()
        for code in FACULTY
    }


    # Used for balancing number of sessions per day.
    semester_day_load = {
        semester: {
            day: 0
            for day in DAYS
        }
        for semester in range(1, 8)
    }


    # Track whether the same subject already appears that day.
    subject_days = {}


    # ========================================================
    # PROCESS SEMESTERS
    # ========================================================

    for semester in range(1, 8):

        sessions = build_required_sessions(
            semester
        )


        for session in sessions:

            subject = session[
                "subject"
            ]

            component = session[
                "component"
            ]

            duration = session[
                "duration"
            ]

            teacher_code = (
                subject.teacher_code
            )

            teacher = FACULTY[
                teacher_code
            ]

            room = SEMESTER_ROOMS[
                semester
            ]


            # ------------------------------------------------
            # Generate every possible candidate position.
            # ------------------------------------------------

            candidates = []


            for day_index, day in enumerate(
                DAYS
            ):

                if duration == 120:

                    possible_slots = (
                        get_lab_slots(
                            semester,
                            day
                        )
                    )

                else:

                    possible_slots = (
                        get_hour_slots(
                            semester,
                            day
                        )
                    )


                for slot_index, (
                    start_time,
                    end_time
                ) in enumerate(
                    possible_slots
                ):

                    keys = occupied_keys(
                        day,
                        start_time,
                        end_time
                    )


                    # ----------------------------------------
                    # Semester conflict
                    # ----------------------------------------

                    if any(
                        key
                        in semester_occupied[
                            semester
                        ]
                        for key in keys
                    ):

                        continue


                    # ----------------------------------------
                    # Teacher conflict
                    # ----------------------------------------

                    if any(
                        key
                        in teacher_occupied[
                            teacher_code
                        ]
                        for key in keys
                    ):

                        continue


                    subject_key = (
                        semester,
                        subject.code
                    )

                    existing_days = (
                        subject_days.get(
                            subject_key,
                            set()
                        )
                    )


                    # ----------------------------------------
                    # Candidate score
                    #
                    # Lower score is better.
                    # ----------------------------------------

                    score = 0


                    # Balance semester workload.
                    score += (
                        semester_day_load[
                            semester
                        ][day]
                        * 5
                    )


                    # Prefer spreading the same subject
                    # across different days.
                    if day in existing_days:

                        score += 15


                    # Slight rotation prevents every semester
                    # from always receiving Monday morning.
                    score += (
                        (
                            day_index
                            + semester
                        )
                        % len(DAYS)
                    )


                    # Later slot gets a tiny penalty.
                    score += (
                        slot_index
                        * 0.1
                    )


                    candidates.append(
                        (
                            score,
                            day,
                            start_time,
                            end_time,
                            keys
                        )
                    )


            # ------------------------------------------------
            # No valid slot found
            # ------------------------------------------------

            if not candidates:

                raise RuntimeError(
                    (
                        "Could not schedule: "
                        f"Semester {semester}, "
                        f"{subject.code}, "
                        f"{component}, "
                        f"Teacher {teacher.name}"
                    )
                )


            # ------------------------------------------------
            # Choose best candidate
            # ------------------------------------------------

            candidates.sort(
                key=lambda item:
                    item[0]
            )

            (
                _,
                selected_day,
                selected_start,
                selected_end,
                selected_keys
            ) = candidates[0]


            # ------------------------------------------------
            # Reserve slots
            # ------------------------------------------------

            for key in selected_keys:

                semester_occupied[
                    semester
                ].add(
                    key
                )

                teacher_occupied[
                    teacher_code
                ].add(
                    key
                )


            semester_day_load[
                semester
            ][selected_day] += (
                duration // 60
            )


            subject_key = (
                semester,
                subject.code
            )

            if subject_key not in subject_days:

                subject_days[
                    subject_key
                ] = set()

            subject_days[
                subject_key
            ].add(
                selected_day
            )


            # ------------------------------------------------
            # Add timetable record
            # ------------------------------------------------

            timetable.append(

                TimetableSlot(

                    semester=
                        semester,

                    division=
                        DIVISION,

                    day=
                        selected_day,

                    start_time=
                        selected_start,

                    end_time=
                        selected_end,

                    room=
                        room,

                    subject=
                        subject.code,

                    subject_name=
                        subject.name,

                    component=
                        component,

                    faculty=
                        teacher.name,

                    faculty_code=
                        teacher.code
                )
            )


    return timetable


# ============================================================
# GENERATE ALL TIMETABLE RECORDS
# ============================================================

TIMETABLE = generate_timetable()


# ============================================================
# ACTIVE SEMESTERS
# ============================================================

def get_active_semesters():

    if ACTIVE_TERM.upper() == "ODD":

        return ODD_SEMESTERS

    return EVEN_SEMESTERS


# ============================================================
# DATE -> WEEKDAY
# ============================================================

def get_weekday(
    day: Optional[int],
    month: Optional[str],
    year: int
) -> Optional[str]:

    if (
        day is None
        or month is None
    ):

        return None


    month_lookup = {

        "JAN": 1,
        "FEB": 2,
        "MAR": 3,
        "APR": 4,
        "MAY": 5,
        "JUN": 6,
        "JUL": 7,
        "AUG": 8,
        "SEP": 9,
        "OCT": 10,
        "NOV": 11,
        "DEC": 12
    }


    month_number = (
        month_lookup.get(
            month.upper()
        )
    )


    if month_number is None:

        return None


    try:

        value = datetime(
            year,
            month_number,
            day
        )

        return value.strftime(
            "%A"
        )

    except ValueError:

        return None


# ============================================================
# FIND MATCHING TIMETABLE SLOTS
# ============================================================

def find_matching_slots(
    semester: Optional[int],
    division: Optional[str],
    day: Optional[int],
    month: Optional[str],
    year: int,
    start_time: Optional[str],
    end_time: Optional[str]
):

    weekday = get_weekday(
        day=day,
        month=month,
        year=year
    )


    active_semesters = (
        get_active_semesters()
    )


    matches = []


    for slot in TIMETABLE:

        # ----------------------------------------------------
        # Active odd/even term
        # ----------------------------------------------------

        if (
            slot.semester
            not in active_semesters
        ):

            continue


        # ----------------------------------------------------
        # Semester
        # ----------------------------------------------------

        if (
            semester is not None
            and slot.semester
            != semester
        ):

            continue


        # ----------------------------------------------------
        # Division
        # ----------------------------------------------------

        if (
            division is not None
            and slot.division.upper()
            != division.upper()
        ):

            continue


        # ----------------------------------------------------
        # Weekday
        # ----------------------------------------------------

        if (
            weekday is not None
            and slot.day
            != weekday
        ):

            continue


        # ----------------------------------------------------
        # Start
        # ----------------------------------------------------

        if (
            start_time is not None
            and slot.start_time
            != start_time
        ):

            continue


        # ----------------------------------------------------
        # End
        # ----------------------------------------------------

        if (
            end_time is not None
            and slot.end_time
            != end_time
        ):

            continue


        matches.append(
            slot
        )


    return matches


# ============================================================
# CHECK FOR TEACHER CONFLICTS
# ============================================================

def check_teacher_conflicts():

    seen = {}

    conflicts = []


    for slot in TIMETABLE:

        keys = occupied_keys(
            slot.day,
            slot.start_time,
            slot.end_time
        )


        for key in keys:

            teacher_key = (
                slot.faculty_code,
                key[0],
                key[1]
            )


            if teacher_key in seen:

                conflicts.append(
                    (
                        seen[
                            teacher_key
                        ],
                        slot
                    )
                )

            else:

                seen[
                    teacher_key
                ] = slot


    return conflicts


# ============================================================
# DISPLAY TIMETABLE
# ============================================================

def print_semester_timetable(
    semester: int
):

    slots = [

        slot
        for slot in TIMETABLE

        if slot.semester
        == semester
    ]


    day_order = {
        day: index
        for index, day in enumerate(
            DAYS
        )
    }


    slots.sort(
        key=lambda slot: (
            day_order[
                slot.day
            ],
            slot.start_time
        )
    )


    print()
    print(
        "=" * 70
    )

    print(
        f"SEMESTER {semester}-{DIVISION}"
    )

    print(
        "Room:",
        SEMESTER_ROOMS[
            semester
        ]
    )

    print(
        "=" * 70
    )


    current_day = None


    for slot in slots:

        if slot.day != current_day:

            current_day = slot.day

            print()
            print(
                current_day.upper()
            )


        print(
            f"{slot.start_time}-{slot.end_time} "
            f"| {slot.subject:<10} "
            f"| {slot.component:<8} "
            f"| {slot.faculty}"
        )


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print()
    print(
        "Active term:",
        ACTIVE_TERM
    )

    print(
        "Active semesters:",
        get_active_semesters()
    )


    for semester in range(
        1,
        8
    ):

        print_semester_timetable(
            semester
        )


    conflicts = (
        check_teacher_conflicts()
    )


    print()
    print(
        "=" * 70
    )

    print(
        "TEACHER CONFLICT CHECK"
    )

    print(
        "=" * 70
    )


    if conflicts:

        print(
            "Conflicts found:",
            len(conflicts)
        )

        for first, second in conflicts:

            print()

            print(
                first.faculty,
                first.day,
                first.start_time,
                first.subject,
                "<->",
                second.subject
            )

    else:

        print(
            "No teacher conflicts found."
        )


    print()

    print(
        "Total timetable slots:",
        len(TIMETABLE)
    )