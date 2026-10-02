from pathlib import Path
import cv2
import numpy as np


BASE_DIR = Path(__file__).resolve().parent.parent.parent

TABLE_PATH = BASE_DIR / "data" / "crops" / "arrangement_table.jpg"

PROCESSED_DIR = BASE_DIR / "data" / "processed"
ROW_DIR = BASE_DIR / "data" / "crops" / "clean_rows"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
ROW_DIR.mkdir(parents=True, exist_ok=True)


table = cv2.imread(str(TABLE_PATH))

if table is None:
    print("Could not read arrangement_table.jpg")
    raise SystemExit


print("Table loaded")


# -------------------------------------------------
# 1. Convert to grayscale
# -------------------------------------------------

gray = cv2.cvtColor(
    table,
    cv2.COLOR_BGR2GRAY
)


# -------------------------------------------------
# 2. Binary image
# -------------------------------------------------

binary = cv2.adaptiveThreshold(
    gray,
    255,
    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
    cv2.THRESH_BINARY_INV,
    15,
    8
)

height, width = binary.shape


# -------------------------------------------------
# 3. Detect horizontal lines
# -------------------------------------------------

horizontal_kernel = cv2.getStructuringElement(
    cv2.MORPH_RECT,
    (max(width // 20, 10), 1)
)

horizontal = cv2.morphologyEx(
    binary,
    cv2.MORPH_OPEN,
    horizontal_kernel
)


# -------------------------------------------------
# 4. Detect vertical lines
# -------------------------------------------------

vertical_kernel = cv2.getStructuringElement(
    cv2.MORPH_RECT,
    (1, max(height // 10, 10))
)

vertical = cv2.morphologyEx(
    binary,
    cv2.MORPH_OPEN,
    vertical_kernel
)


# -------------------------------------------------
# 5. Combine grid-line mask
# -------------------------------------------------

grid_mask = cv2.bitwise_or(
    horizontal,
    vertical
)


# Slightly thicken mask so lines are fully removed
grid_mask = cv2.dilate(
    grid_mask,
    np.ones((3, 3), np.uint8),
    iterations=1
)


# -------------------------------------------------
# 6. Remove table lines
# -------------------------------------------------

clean_binary = cv2.subtract(
    binary,
    grid_mask
)


# Convert back to black text on white background
clean_image = cv2.bitwise_not(
    clean_binary
)


# -------------------------------------------------
# 7. Save full cleaned table
# -------------------------------------------------

cv2.imwrite(
    str(PROCESSED_DIR / "table_without_grid.jpg"),
    clean_image
)


# -------------------------------------------------
# 8. Crop handwritten data rows
#
# Based on your current table:
# row 2 and row 3 contain actual handwritten data.
# We'll later detect these dynamically.
# -------------------------------------------------

row_1 = clean_image[
    115:160,
    0:width
]

row_2 = clean_image[
    150:195,
    0:width
]


# -------------------------------------------------
# 9. Enlarge rows for OCR
# -------------------------------------------------

def enlarge_row(row):

    return cv2.resize(
        row,
        None,
        fx=3,
        fy=3,
        interpolation=cv2.INTER_CUBIC
    )


row_1_large = enlarge_row(row_1)
row_2_large = enlarge_row(row_2)


# -------------------------------------------------
# 10. Add white padding
# -------------------------------------------------

def add_padding(row):

    return cv2.copyMakeBorder(
        row,
        30,
        30,
        30,
        30,
        cv2.BORDER_CONSTANT,
        value=255
    )


row_1_final = add_padding(row_1_large)
row_2_final = add_padding(row_2_large)


# -------------------------------------------------
# 11. Save cleaned rows
# -------------------------------------------------

cv2.imwrite(
    str(ROW_DIR / "assignment_row_1.jpg"),
    row_1_final
)

cv2.imwrite(
    str(ROW_DIR / "assignment_row_2.jpg"),
    row_2_final
)


print("Saved:")
print("table_without_grid.jpg")
print("assignment_row_1.jpg")
print("assignment_row_2.jpg")