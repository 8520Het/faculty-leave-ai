from pathlib import Path

import cv2

from ocr_fields import run_trocr
from paths import PROJECT_ROOT, CROPS_DIR


# ============================================================
# PREPROCESS CLASS REGION
# ============================================================

def preprocess_class_region(image):

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    # Upscale more aggressively than normal field OCR
    gray = cv2.resize(
        gray,
        None,
        fx=4,
        fy=4,
        interpolation=cv2.INTER_CUBIC
    )

    # Improve contrast
    clahe = cv2.createCLAHE(
        clipLimit=2.5,
        tileGridSize=(8, 8)
    )

    gray = clahe.apply(
        gray
    )

    # Mild denoise
    gray = cv2.GaussianBlur(
        gray,
        (3, 3),
        0
    )

    # Sharpen
    blurred = cv2.GaussianBlur(
        gray,
        (0, 0),
        1
    )

    gray = cv2.addWeighted(
        gray,
        1.7,
        blurred,
        -0.7,
        0
    )

    # Large white padding
    gray = cv2.copyMakeBorder(
        gray,
        35,
        35,
        35,
        35,
        cv2.BORDER_CONSTANT,
        value=255
    )

    return gray


# ============================================================
# SECOND-PASS CLASS OCR
# ============================================================

def ocr_class_second_pass(
    row_image_path,
    debug_dir=None
):

    row_image_path = Path(
        row_image_path
    )

    row = cv2.imread(
        str(row_image_path)
    )

    if row is None:
        raise FileNotFoundError(
            f"Could not read row: {row_image_path}"
        )

    height, width = row.shape[:2]

    # Wider region than normal class crop.
    #
    # We deliberately include a little of Room because
    # handwriting may cross the column boundary.
    x1 = int(
        width * 0.02
    )

    x2 = int(
        width * 0.37
    )

    crop = row[
        0:height,
        x1:x2
    ]

    processed = preprocess_class_region(
        crop
    )


    # ========================================================
    # DEBUG OUTPUT
    # ========================================================

    if debug_dir is None:
        debug_dir = CROPS_DIR / "class_second_pass"

    debug_dir = Path(debug_dir)
    debug_dir.mkdir(parents=True, exist_ok=True)

    debug_path = (
        debug_dir
        / f"{row_image_path.stem}_class_second_pass.jpg"
    )

    cv2.imwrite(
        str(debug_path),
        processed
    )


    # ========================================================
    # OCR
    # ========================================================

    result = run_trocr(
        processed
    )

    return result


# ============================================================
# TEST BOTH ROWS
# ============================================================

if __name__ == "__main__":

    ROW_DIR = (
        PROJECT_ROOT
        / "data"
        / "crops"
        / "detected_rows"
    )

    rows = [
        ROW_DIR
        / "assignment_row_2.jpg",

        ROW_DIR
        / "assignment_row_3.jpg"
    ]

    print()
    print("====================================")
    print("SECOND-PASS CLASS OCR")
    print("====================================")

    for row_path in rows:

        result = ocr_class_second_pass(
            row_path
        )

        print()
        print(
            row_path.name
        )

        print(
            "CLASS:",
            result
        )