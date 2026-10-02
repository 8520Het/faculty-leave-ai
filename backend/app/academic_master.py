from dataclasses import dataclass
from typing import List


# ============================================================
# FACULTY
# ============================================================

@dataclass
class Faculty:
    code: str
    name: str


FACULTY = {
    "PRM": Faculty(
        "PRM",
        "Pooja Ravi Makwana"
    ),

    "DCV": Faculty(
        "DCV",
        "Deepak Chhaganbhai Vegda"
    ),

    "ANV": Faculty(
        "ANV",
        "Archana Nishit Vyas"
    ),

    "FMV": Faculty(
        "FMV",
        "Fatema Mazarhirbhai Vhora"
    ),

    "SHJ": Faculty(
        "SHJ",
        "Shweta Haribhai Jambukia"
    ),

    "NV": Faculty(
        "NV",
        "Nilamba Vala"
    ),

    "SKV": Faculty(
        "SKV",
        "Sunil Kishorbhai Vithlani"
    ),

    "VS": Faculty(
        "VS",
        "Viral Shah"
    ),

    "VD": Faculty(
        "VD",
        "Vipul Dabhi"
    ),

    "HBP": Faculty(
        "HBP",
        "Harshad B Prajapati"
    ),

    "RV": Faculty(
        "RV",
        "Ravi Vyas"
    ),

    "VP": Faculty(
        "VP",
        "Viranchi Patel"
    )
}


# ============================================================
# SUBJECT
# ============================================================

@dataclass
class Subject:
    semester: int
    code: str
    name: str
    teacher_code: str
    components: List[str]


SUBJECTS = [


    # ========================================================
    # SEMESTER 1
    # ========================================================

    Subject(
        1,
        "C",
        "C Programming",
        "DCV",
        ["LECTURE", "LAB", "TUTORIAL"]
    ),

    Subject(
        1,
        "BEE",
        "Basic Electrical Engineering",
        "ANV",
        ["LECTURE", "LAB", "TUTORIAL"]
    ),

    Subject(
        1,
        "MATH-I",
        "Mathematics I",
        "PRM",
        ["LECTURE", "TUTORIAL"]
    ),

    Subject(
        1,
        "SW",
        "Software Workshop",
        "VP",
        ["LAB"]
    ),

    Subject(
        1,
        "EGD",
        "Engineering Graphics and Designing",
        "RV",
        ["LECTURE", "LAB"]
    ),


    # ========================================================
    # SEMESTER 2
    # ========================================================

    Subject(
        2,
        "CPP",
        "C++",
        "DCV",
        ["LECTURE", "LAB", "TUTORIAL"]
    ),

    Subject(
        2,
        "PHY",
        "Physics",
        "FMV",
        ["LECTURE", "LAB", "TUTORIAL"]
    ),

    Subject(
        2,
        "MATH-II",
        "Mathematics II",
        "PRM",
        ["LECTURE", "TUTORIAL"]
    ),

    Subject(
        2,
        "HW",
        "Hardware Workshop",
        "SKV",
        ["LAB"]
    ),

    Subject(
        2,
        "EVS",
        "Environmental Studies",
        "NV",
        ["LECTURE"]
    ),

    Subject(
        2,
        "ENG",
        "English",
        "SHJ",
        ["LECTURE", "LAB"]
    ),


    # ========================================================
    # SEMESTER 3
    # Default = lecture + lab unless specifically stated
    # ========================================================

    Subject(
        3,
        "OOPJ",
        "Object Oriented Programming with Java",
        "DCV",
        ["LECTURE", "LAB"]
    ),

    Subject(
        3,
        "PTS",
        "Professional and Technical Skills",
        "VP",
        ["LECTURE"]
    ),

    Subject(
        3,
        "CS",
        "Computer Systems",
        "VS",
        ["LECTURE", "LAB"]
    ),

    Subject(
        3,
        "DDC",
        "Digital Design and Computer",
        "SKV",
        ["LECTURE", "LAB"]
    ),

    Subject(
        3,
        "ETC",
        "ETC",
        "ANV",
        ["LECTURE"]
    ),

    Subject(
        3,
        "DSA",
        "Data Structures and Algorithms",
        "HBP",
        ["LECTURE", "LAB"]
    ),


    # ========================================================
    # SEMESTER 4
    # ========================================================

    Subject(
        4,
        "UHV",
        "Universal Human Values",
        "NV",
        ["LECTURE"]
    ),

    Subject(
        4,
        "DM",
        "Discrete Mathematics",
        "PRM",
        ["LECTURE"]
    ),

    Subject(
        4,
        "CCN",
        "Computer Communication and Networks",
        "SHJ",
        ["LECTURE", "LAB"]
    ),

    Subject(
        4,
        "DBMS",
        "Database Management Systems",
        "VS",
        ["LECTURE", "LAB"]
    ),

    Subject(
        4,
        "DAA",
        "Design and Analysis of Algorithms",
        "HBP",
        ["LECTURE", "LAB"]
    ),

    Subject(
        4,
        "MPI",
        "Microprocessor and Interfacing",
        "SKV",
        ["LECTURE", "LAB"]
    ),


    # ========================================================
    # SEMESTER 5
    # ========================================================

    Subject(
        5,
        "TAFL",
        "Theory of Automata and Formal Languages",
        "PRM",
        ["LECTURE"]
    ),

    Subject(
        5,
        "AJT",
        "Advanced Java Technology",
        "HBP",
        ["LECTURE", "LAB"]
    ),

    Subject(
        5,
        "SE",
        "Software Engineering",
        "VP",
        ["LECTURE", "LAB"]
    ),

    Subject(
        5,
        "AD",
        "Application Development",
        "RV",
        ["LECTURE", "LAB"]
    ),

    Subject(
        5,
        "CO",
        "Computer Organization",
        "SKV",
        ["LECTURE", "LAB"]
    ),

    Subject(
        5,
        "ECES",
        "ECES",
        "ANV",
        ["LECTURE"]
    ),


    # ========================================================
    # SEMESTER 6
    # ========================================================

    Subject(
        6,
        "LT",
        "Language Technology",
        "PRM",
        ["LECTURE", "LAB"]
    ),

    Subject(
        6,
        "AOS",
        "Advanced Operating Systems",
        "VS",
        ["LECTURE", "LAB"]
    ),

    Subject(
        6,
        "DAUP",
        "DAUP",
        "FMV",
        ["LAB"]
    ),

    Subject(
        6,
        "FSD",
        "Full Stack Development",
        "VP",
        ["LECTURE", "LAB"]
    ),

    Subject(
        6,
        "PROJECT-I",
        "Project - I",
        "HBP",
        ["LAB"]
    ),

    Subject(
        6,
        "DAIE",
        "DAIE",
        "VD",
        ["LECTURE"]
    ),


    # ========================================================
    # SEMESTER 7
    # ========================================================

    Subject(
        7,
        "AI",
        "Artificial Intelligence",
        "VD",
        ["LECTURE"]
    ),

    Subject(
        7,
        "MLDL",
        "Machine Learning and Deep Learning",
        "PRM",
        ["LECTURE", "LAB"]
    ),

    Subject(
        7,
        "WT",
        "Web Technology",
        "ANV",
        ["LECTURE", "LAB"]
    ),

    Subject(
        7,
        "DC",
        "Distributed Computing",
        "SHJ",
        ["LECTURE", "LAB"]
    ),

    Subject(
        7,
        "PROJECT-II",
        "Project - II",
        "HBP",
        ["LAB"]
    ),

    Subject(
        7,
        "DEVOPS",
        "DevOps",
        "VP",
        ["LAB"]
    )
]


# ============================================================
# HELPERS
# ============================================================

def get_subjects_for_semester(
    semester: int
):

    return [
        subject
        for subject in SUBJECTS
        if subject.semester == semester
    ]


def get_subject_by_code(
    semester: int,
    code: str
):

    code = code.upper().strip()

    for subject in SUBJECTS:

        if (
            subject.semester == semester
            and subject.code.upper() == code
        ):

            return subject

    return None


if __name__ == "__main__":

    for semester in range(1, 8):

        print()
        print(
            f"SEMESTER {semester}"
        )

        for subject in get_subjects_for_semester(
            semester
        ):

            teacher = FACULTY[
                subject.teacher_code
            ]

            print(
                subject.code,
                "->",
                teacher.name,
                "->",
                subject.components
            )