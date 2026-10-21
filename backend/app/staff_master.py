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
    StaffMember(
        staff_id=5,
        name="Vipul K. Dabhi",
        email="vipul.dabhi@ddu.ac.in",
        department="IT"
    ),
    StaffMember(
        staff_id=6,
        name="Nikita Desai",
        email="nikita.desai@ddu.ac.in",
        department="IT"
    ),
    StaffMember(
        staff_id=7,
        name="Archana N. Vyas",
        email="archana.vyas@ddu.ac.in",
        department="IT"
    ),
    StaffMember(
        staff_id=8,
        name="Sunil K. Vithlani",
        email="sunil.vithlani@ddu.ac.in",
        department="IT"
    ),
    StaffMember(
        staff_id=9,
        name="Viral H. Shah",
        email="viral.shah@ddu.ac.in",
        department="IT"
    ),
    StaffMember(
        staff_id=10,
        name="Pooja R. Makwana",
        email="pooja.makwana@ddu.ac.in",
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