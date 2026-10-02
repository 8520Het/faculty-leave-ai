from pathlib import Path

import cv2
import numpy as np


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent

PROCESSED_DIR = BASE_DIR / "data" / "processed"
CROPS_DIR = BASE_DIR / "data" / "crops"

TABLE_PATH = PROCESSED_DIR / "table_without_grid.jpg"

OUTPUT_DIR = CROPS_DIR / "detected_rows"
OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# ROW BOUNDARIES
#
# These come from the fixed leave-form template.
# There are 5 arrangement rows.
# ============================================================

Y_POSITIONS = [
    88,
    122,
    156,
    190,
    224,
    258
]


# ============================================================
# CHECK WHETHER A ROW CONTAINS HANDWRITING
# ============================================================

def calculate_ink_ratio(row_image):

    gray = cv2.cvtColor(
        row_image,
        cv2.COLOR_BGR2GRAY
    )

    # Ignore small borders where remnants
    # of table lines may remain.
    height, width = gray.shape

    margin_x = 8
    margin_y = 4

    if (
        width > margin_x * 2
        and height > margin_y * 2
    ):
        gray = gray[
            margin_y:height - margin_y,
            margin_x:width - margin_x
        ]

    # Anything sufficiently dark is considered ink.
    dark_pixels = gray < 180

    ink_pixels = np.count_nonzero(
        dark_pixels
    )

    total_pixels = gray.size

    if total_pixels == 0:
        return 0.0

    return ink_pixels / total_pixels


# ============================================================
# DETECT FILLED ROWS
# ============================================================

def detect_filled_rows(
    table_path,
    ink_threshold=0.05
):

    table_path = Path(
        table_path
    )

    table = cv2.imread(
        str(table_path)
    )

    if table is None:
        raise FileNotFoundError(
            f"Could not read cleaned table: {table_path}"
        )

    detected_rows = []

    print()
    print("====================================")
    print("ROW DETECTION")
    print("====================================")

    for index in range(
        len(Y_POSITIONS) - 1
    ):

        y1 = Y_POSITIONS[index]
        y2 = Y_POSITIONS[index + 1]

        row = table[
            y1:y2,
            :
        ]

        ink_ratio = calculate_ink_ratio(
            row
        )

        row_number = index + 1

        print(
            f"Row {row_number}: "
            f"ink ratio = {ink_ratio:.4f}"
        )

        # Save every row temporarily
        # so we can visually inspect them.
        debug_path = (
            OUTPUT_DIR
            / f"row_{row_number}_debug.jpg"
        )

        cv2.imwrite(
            str(debug_path),
            row
        )

        if ink_ratio >= ink_threshold:

            detected_path = (
                OUTPUT_DIR
                / f"assignment_row_{row_number}.jpg"
            )

            cv2.imwrite(
                str(detected_path),
                row
            )

            detected_rows.append(
                {
                    "row_number": row_number,
                    "image_path": detected_path,
                    "ink_ratio": ink_ratio
                }
            )

            print(
                "   -> FILLED"
            )

        else:

            print(
                "   -> EMPTY"
            )

    print()
    print(
        "Detected filled rows:",
        len(detected_rows)
    )

    return detected_rows


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    rows = detect_filled_rows(
        TABLE_PATH
    )

    print()
    print("====================================")
    print("FILLED ROWS")
    print("====================================")

    for row in rows:

        print(
            "Row:",
            row["row_number"]
        )

        print(
            "Ink ratio:",
            round(
                row["ink_ratio"],
                4
            )
        )

        print(
            "Image:",
            row["image_path"]
        )

        print()