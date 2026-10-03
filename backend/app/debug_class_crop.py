from pathlib import Path
import cv2

from paths import CROPS_DIR


TABLE_PATH = CROPS_DIR / "arrangement_table.jpg"
OUTPUT_DIR = CROPS_DIR / "debug"

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


table = cv2.imread(str(TABLE_PATH))

if table is None:
    print("Could not load arrangement table")
    raise SystemExit


print("Table size:")
print("Width:", table.shape[1])
print("Height:", table.shape[0])


# -------------------------------------------------
# TEMPORARY wider crops for the two handwritten rows
# -------------------------------------------------

# Row containing first handwritten assignment
row2_class = table[
    115:160,
    35:345
]

# Row containing second handwritten assignment
row3_class = table[
    150:195,
    35:345
]


cv2.imwrite(
    str(OUTPUT_DIR / "row2_class_wide.jpg"),
    row2_class
)

cv2.imwrite(
    str(OUTPUT_DIR / "row3_class_wide.jpg"),
    row3_class
)


print("Saved:")
print("row2_class_wide.jpg")
print("row3_class_wide.jpg")