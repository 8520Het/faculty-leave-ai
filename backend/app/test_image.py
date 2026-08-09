from pathlib import Path
import cv2


# -------------------------------------------------
# Project paths
# -------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent.parent

CROPS_DIR = BASE_DIR / "data" / "crops"

TABLE_PATH = CROPS_DIR / "arrangement_table.jpg"
ASSIGNMENT_DIR = CROPS_DIR / "assignment_cells"

ASSIGNMENT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# -------------------------------------------------
# Load table
# -------------------------------------------------

table = cv2.imread(str(TABLE_PATH))

if table is None:
    print("Could not read arrangement_table.jpg")
    raise SystemExit

print("Table loaded")


# -------------------------------------------------
# Detected column boundaries
#
# These values come from your current table.
# We will automate them later.
# -------------------------------------------------

x_positions = [
    10,    # left edge
    40,    # No.
    181,   # Class
    234,   # Room
    364,   # Subject
    557,   # Staff name
    678    # Signature / right edge
]


# -------------------------------------------------
# Detected horizontal boundaries
#
# Header occupies top part.
# Data rows start after approximately y = 88.
# -------------------------------------------------

y_positions = [
    88,
    122,
    156,
    190,
    224,
    258
]


# -------------------------------------------------
# Column names
# -------------------------------------------------

column_names = [
    "number",
    "class",
    "room",
    "subject",
    "staff_name",
    "signature"
]


# -------------------------------------------------
# Crop each data row
# -------------------------------------------------

padding = 4

row_number = 1


for row_index in range(
    len(y_positions) - 1
):

    y1 = y_positions[row_index] + padding
    y2 = y_positions[row_index + 1] - padding

    print()
    print("Processing row:", row_number)

    for column_index in range(
        len(x_positions) - 1
    ):

        x1 = (
            x_positions[column_index]
            + padding
        )

        x2 = (
            x_positions[column_index + 1]
            - padding
        )

        if x2 <= x1 or y2 <= y1:
            continue

        cell = table[
            y1:y2,
            x1:x2
        ]

        column_name = (
            column_names[column_index]
        )

        filename = (
            f"row_{row_number}_"
            f"{column_name}.jpg"
        )

        output_path = (
            ASSIGNMENT_DIR / filename
        )

        cv2.imwrite(
            str(output_path),
            cell
        )

        print(
            "Saved:",
            filename
        )

    row_number += 1


print()
print("Done")
print(
    "Cells saved to:",
    ASSIGNMENT_DIR
)