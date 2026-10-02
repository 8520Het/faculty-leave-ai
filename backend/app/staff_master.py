from dataclasses import dataclass


@dataclass
class StaffMember:
    staff_id: int
    name: str
    email: str
    department: str


STAFF_MASTER = [
    StaffMember(
        staff_id=1,
        name="Sandeep R. Suthar",
        email="sandeep.suthar@ddu.ac.in",
        department="IT"
    ),
    StaffMember(
        staff_id=2,
        name="Anand K. Patel",
        email="anand.patel@ddu.ac.in",
        department="IT"
    ),
    StaffMember(
        staff_id=3,
        name="Harshad B. Prajapati",
        email="harshad.prajapati@ddu.ac.in",
        department="IT"
    ),
     StaffMember(
        staff_id=4,
        name="Deepak C. Vegda",
        email="deepak.vegda@ddu.ac.in",
        department="IT"
    ),
]


if __name__ == "__main__":

    for staff in STAFF_MASTER:
        print(
            staff.staff_id,
            staff.name,
            staff.email,
            staff.department
        )