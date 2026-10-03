from pathlib import Path

import cv2

from paths import PROJECT_ROOT, CROPS_DIR


PROCESSOR = None
MODEL = None
DEVICE = None
_MODEL_LOAD_ERROR = None


def _load_trocr():
    global PROCESSOR, MODEL, DEVICE, _MODEL_LOAD_ERROR

    if MODEL is not None:
        return

    if _MODEL_LOAD_ERROR is not None:
        raise RuntimeError(_MODEL_LOAD_ERROR)

    try:
        import torch
        from transformers import TrOCRProcessor, VisionEncoderDecoderModel
        from PIL import Image  # noqa: F401
    except Exception as exc:
        _MODEL_LOAD_ERROR = (
            "TrOCR dependencies are not available. "
            "Install torch and transformers, or use DEMO_MODE=1. "
            f"Original error: {exc}"
        )
        raise RuntimeError(_MODEL_LOAD_ERROR) from exc

    print("Loading TrOCR model...")

    PROCESSOR = TrOCRProcessor.from_pretrained(
        "microsoft/trocr-base-handwritten"
    )
    MODEL = VisionEncoderDecoderModel.from_pretrained(
        "microsoft/trocr-base-handwritten"
    )
    DEVICE = torch.device(
        "cuda" if torch.cuda.is_available() else "cpu"
    )
    MODEL.to(DEVICE)
    MODEL.eval()

    print("TrOCR model loaded on:", DEVICE)


# ============================================================
# IMAGE PREPROCESSING
# ============================================================

def preprocess_crop(image):

    if image is None or image.size == 0:
        raise ValueError("Empty OCR crop")

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    # Upscale handwriting
    gray = cv2.resize(
        gray,
        None,
        fx=3,
        fy=3,
        interpolation=cv2.INTER_CUBIC
    )

    # Improve local contrast
    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    gray = clahe.apply(gray)

    # Mild noise reduction
    gray = cv2.GaussianBlur(
        gray,
        (3, 3),
        0
    )

    # Mild sharpening
    blurred = cv2.GaussianBlur(
        gray,
        (0, 0),
        1
    )

    gray = cv2.addWeighted(
        gray,
        1.5,
        blurred,
        -0.5,
        0
    )

    # White space around handwriting
    gray = cv2.copyMakeBorder(
        gray,
        25,
        25,
        25,
        25,
        cv2.BORDER_CONSTANT,
        value=255
    )

    return gray


# ============================================================
# TrOCR
# ============================================================

def run_trocr(image):
    from PIL import Image
    import torch

    _load_trocr()

    if len(image.shape) == 2:
        rgb = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    else:
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    pil_image = Image.fromarray(rgb)

    pixel_values = PROCESSOR(
        images=pil_image,
        return_tensors="pt"
    ).pixel_values.to(DEVICE)

    with torch.no_grad():
        generated_ids = MODEL.generate(
            pixel_values,
            max_new_tokens=40,
            num_beams=1
        )

    text = PROCESSOR.batch_decode(
        generated_ids,
        skip_special_tokens=True
    )[0]

    return text.strip()


# ============================================================
# OCR ONE ASSIGNMENT ROW
# ============================================================

def ocr_assignment_row(row_image_path, debug_dir=None):

    row_image_path = Path(row_image_path)

    row = cv2.imread(
        str(row_image_path)
    )

    if row is None:
        raise FileNotFoundError(
            f"Could not read row image: {row_image_path}"
        )

    height, width = row.shape[:2]

    # ========================================================
    # FIELD REGIONS
    #
    # Adjusted using the actual detected row images.
    #
    # We intentionally keep SMALL overlaps because handwriting
    # sometimes crosses table borders.
    # ========================================================

    field_regions = {

        # Skip most of the serial-number column
        "class": (
            int(width * 0.035),
            int(width * 0.295)
        ),

        "room": (
            int(width * 0.280),
            int(width * 0.365)
        ),

        "subject": (
            int(width * 0.350),
            int(width * 0.545)
        ),

        "staff_name": (
            int(width * 0.525),
            int(width * 0.845)
        )
    }


    # ========================================================
    # DEBUG DIRECTORY
    # ========================================================

    if debug_dir is None:
        debug_dir = CROPS_DIR / "ocr_debug"

    debug_dir = Path(debug_dir)
    debug_dir.mkdir(parents=True, exist_ok=True)

    row_name = row_image_path.stem

    results = {}


    # ========================================================
    # PROCESS EACH FIELD
    # ========================================================

    for field_name, (
        x1,
        x2
    ) in field_regions.items():

        crop = row[
            0:height,
            x1:x2
        ]

        processed = preprocess_crop(
            crop
        )

        # Save each crop separately so Row 2
        # does not overwrite Row 3 debug images.
        debug_path = (
            debug_dir
            / f"{row_name}_{field_name}.jpg"
        )

        cv2.imwrite(
            str(debug_path),
            processed
        )

        text = run_trocr(
            processed
        )

        results[field_name] = text

    return results


# ============================================================
# MANUAL TEST
# ============================================================

if __name__ == "__main__":

    TEST_ROW = (
        PROJECT_ROOT
        / "data"
        / "crops"
        / "detected_rows"
        / "assignment_row_2.jpg"
    )

    result = ocr_assignment_row(
        TEST_ROW
    )

    print()
    print("====================================")
    print("OCR RESULT")
    print("====================================")

    print(
        "CLASS:",
        result["class"]
    )

    print(
        "ROOM:",
        result["room"]
    )

    print(
        "SUBJECT:",
        result["subject"]
    )

    print(
        "STAFF:",
        result["staff_name"]
    )