from pathlib import Path

import cv2
import numpy as np

from paths import PROJECT_ROOT, PROCESSED_DIR, CROPS_DIR


def clean_table_image(table):
    """Remove grid lines from an arrangement-table crop.

    Preserves the original morphology-based cleaning used by
    the CLI workflow.
    """
    if table is None or table.size == 0:
        raise ValueError("Empty table image")

    if len(table.shape) == 3:
        gray = cv2.cvtColor(table, cv2.COLOR_BGR2GRAY)
    else:
        gray = table

    binary = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        15,
        8,
    )

    height, width = binary.shape

    horizontal_kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT,
        (max(width // 20, 10), 1),
    )
    horizontal = cv2.morphologyEx(
        binary,
        cv2.MORPH_OPEN,
        horizontal_kernel,
    )

    vertical_kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT,
        (1, max(height // 10, 10)),
    )
    vertical = cv2.morphologyEx(
        binary,
        cv2.MORPH_OPEN,
        vertical_kernel,
    )

    grid_mask = cv2.bitwise_or(horizontal, vertical)
    grid_mask = cv2.dilate(
        grid_mask,
        np.ones((3, 3), np.uint8),
        iterations=1,
    )

    clean_binary = cv2.subtract(binary, grid_mask)
    clean_image = cv2.bitwise_not(clean_binary)

    if len(table.shape) == 3:
        return cv2.cvtColor(clean_image, cv2.COLOR_GRAY2BGR)

    return clean_image


def enlarge_row(row):
    return cv2.resize(
        row,
        None,
        fx=3,
        fy=3,
        interpolation=cv2.INTER_CUBIC,
    )


def add_padding(row):
    return cv2.copyMakeBorder(
        row,
        30,
        30,
        30,
        30,
        cv2.BORDER_CONSTANT,
        value=255,
    )


if __name__ == "__main__":
    table_path = CROPS_DIR / "arrangement_table.jpg"
    row_dir = CROPS_DIR / "clean_rows"
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    row_dir.mkdir(parents=True, exist_ok=True)

    table = cv2.imread(str(table_path))
    if table is None:
        print("Could not read arrangement_table.jpg")
        raise SystemExit

    print("Table loaded")
    clean_image = clean_table_image(table)
    if len(clean_image.shape) == 3:
        save_image = cv2.cvtColor(clean_image, cv2.COLOR_BGR2GRAY)
    else:
        save_image = clean_image

    cv2.imwrite(str(PROCESSED_DIR / "table_without_grid.jpg"), save_image)

    height, width = save_image.shape[:2]
    row_1 = save_image[115:160, 0:width]
    row_2 = save_image[150:195, 0:width]

    cv2.imwrite(str(row_dir / "assignment_row_1.jpg"), add_padding(enlarge_row(row_1)))
    cv2.imwrite(str(row_dir / "assignment_row_2.jpg"), add_padding(enlarge_row(row_2)))

    print("Saved:")
    print("table_without_grid.jpg")
    print("assignment_row_1.jpg")
    print("assignment_row_2.jpg")
    print("Project root:", PROJECT_ROOT)
