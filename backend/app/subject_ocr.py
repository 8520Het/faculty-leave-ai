from pathlib import Path
from difflib import SequenceMatcher

import cv2

from ocr_fields import run_trocr
from academic_master import SUBJECTS
from timetable import get_active_semesters
from paths import PROJECT_ROOT, CROPS_DIR


# ============================================================
# CONFIGURATION
# ============================================================

SUBJECT_ACCEPT_THRESHOLD = 0.60


# ============================================================
# NORMALIZATION
# ============================================================

def normalize_text(value):

    if not value:
        return ""

    value = str(value).upper()

    for character in [
        ".",
        ",",
        '"',
        "'",
        "-",
        "_",
        "(",
        ")",
        "/",
        "\\",
        ":",
        ";"
    ]:

        value = value.replace(
            character,
            ""
        )

    value = value.replace(
        " ",
        ""
    )

    return value.strip()


# ============================================================
# SIMILARITY
# ============================================================

def similarity(
    first,
    second
):

    first = normalize_text(
        first
    )

    second = normalize_text(
        second
    )

    if not first or not second:
        return 0.0

    if first == second:
        return 1.0

    if second in first:
        coverage = len(second) / len(first)
        return max(0.70 + 0.28 * coverage, SequenceMatcher(None, first, second).ratio())

    if len(first) >= 2 and first in second:
        return max(0.85, SequenceMatcher(None, first, second).ratio())

    return SequenceMatcher(
        None,
        first,
        second
    ).ratio()


# ============================================================
# SUBJECT MASTER MATCHING
# ============================================================

def find_best_subject_match(text):

    active_semesters = (
        get_active_semesters()
    )

    best_subject = None
    best_score = 0.0


    for subject in SUBJECTS:

        if (
            subject.semester
            not in active_semesters
        ):
            continue


        # ----------------------------------------------------
        # Compare OCR against subject code
        # ----------------------------------------------------

        code_score = similarity(
            text,
            subject.code
        )


        # ----------------------------------------------------
        # Compare OCR against full subject name
        # ----------------------------------------------------

        name_score = similarity(
            text,
            subject.name
        )


        score = max(
            code_score,
            name_score
        )


        if score > best_score:

            best_score = score
            best_subject = subject


    return (
        best_subject,
        best_score
    )


# ============================================================
# ENSURE GRAYSCALE
# ============================================================

def ensure_grayscale(image):

    if image is None:
        return None


    # Already grayscale
    if len(image.shape) == 2:

        return image


    # BGR image
    if (
        len(image.shape) == 3
        and
        image.shape[2] == 3
    ):

        return cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY
        )


    # BGRA image
    if (
        len(image.shape) == 3
        and
        image.shape[2] == 4
    ):

        return cv2.cvtColor(
            image,
            cv2.COLOR_BGRA2GRAY
        )


    return image


# ============================================================
# WHITE PADDING
# ============================================================

def add_padding(
    image,
    padding=40
):

    image = ensure_grayscale(
        image
    )

    return cv2.copyMakeBorder(

        image,

        padding,
        padding,
        padding,
        padding,

        cv2.BORDER_CONSTANT,

        value=255
    )


# ============================================================
# VARIANT 1
# CLAHE
# ============================================================

def preprocess_variant_1(image):

    resized = cv2.resize(

        image,

        None,

        fx=4,
        fy=4,

        interpolation=
            cv2.INTER_CUBIC
    )


    gray = cv2.cvtColor(

        resized,

        cv2.COLOR_BGR2GRAY
    )


    clahe = cv2.createCLAHE(

        clipLimit=2.5,

        tileGridSize=(8, 8)
    )


    enhanced = clahe.apply(
        gray
    )


    enhanced = cv2.GaussianBlur(

        enhanced,

        (3, 3),

        0
    )


    return enhanced


# ============================================================
# VARIANT 2
# ADAPTIVE THRESHOLD
# ============================================================

def preprocess_variant_2(image):

    resized = cv2.resize(

        image,

        None,

        fx=4,
        fy=4,

        interpolation=
            cv2.INTER_CUBIC
    )


    gray = cv2.cvtColor(

        resized,

        cv2.COLOR_BGR2GRAY
    )


    threshold = cv2.adaptiveThreshold(

        gray,

        255,

        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,

        cv2.THRESH_BINARY,

        31,

        11
    )


    return threshold


# ============================================================
# VARIANT 3
# SHARPEN
# ============================================================

def preprocess_variant_3(image):

    resized = cv2.resize(

        image,

        None,

        fx=4,
        fy=4,

        interpolation=
            cv2.INTER_CUBIC
    )


    gray = cv2.cvtColor(

        resized,

        cv2.COLOR_BGR2GRAY
    )


    blur = cv2.GaussianBlur(

        gray,

        (0, 0),

        2
    )


    sharpened = cv2.addWeighted(

        gray,
        1.8,

        blur,
        -0.8,

        0
    )


    return sharpened


# ============================================================
# VARIANT 4
# OTSU THRESHOLD
# ============================================================

def preprocess_variant_4(image):

    resized = cv2.resize(

        image,

        None,

        fx=4,
        fy=4,

        interpolation=
            cv2.INTER_CUBIC
    )


    gray = cv2.cvtColor(

        resized,

        cv2.COLOR_BGR2GRAY
    )


    _, threshold = cv2.threshold(

        gray,

        0,

        255,

        cv2.THRESH_BINARY
        +
        cv2.THRESH_OTSU
    )


    return threshold


# ============================================================
# SUBJECT SECOND PASS
# ============================================================

def run_subject_second_pass(
    row_image_path,
    debug_dir=None
):

    row_image_path = Path(
        row_image_path
    )


    print()
    print(
        "Subject OCR input:"
    )

    print(
        row_image_path
    )


    # ========================================================
    # READ ROW IMAGE
    # ========================================================

    row_image = cv2.imread(
        str(
            row_image_path
        )
    )


    if row_image is None:

        raise FileNotFoundError(

            "Could not read row image: "
            f"{row_image_path}"
        )


    height, width = (
        row_image.shape[:2]
    )


    # ========================================================
    # SUBJECT REGION
    #
    # Slightly wider crop than normal OCR.
    # ========================================================

    x1 = int(
        width * 0.365
    )

    x2 = int(
        width * 0.555
    )


    subject_crop = row_image[
        0:height,
        x1:x2
    ]


    if (
        subject_crop is None
        or
        subject_crop.size == 0
    ):

        raise ValueError(
            "Subject crop is empty."
        )


    # ========================================================
    # PREPROCESS VARIANTS
    # ========================================================

    variants = [

        (
            "clahe",
            preprocess_variant_1(
                subject_crop
            )
        ),

        (
            "adaptive",
            preprocess_variant_2(
                subject_crop
            )
        ),

        (
            "sharpen",
            preprocess_variant_3(
                subject_crop
            )
        ),

        (
            "otsu",
            preprocess_variant_4(
                subject_crop
            )
        )
    ]


    results = []


    row_name = (
        row_image_path.stem
    )


    # ========================================================
    # RUN EACH VARIANT
    # ========================================================

    for (
        variant_name,
        processed_image
    ) in variants:


        processed_image = (
            ensure_grayscale(
                processed_image
            )
        )


        padded = add_padding(
            processed_image
        )


        padded = ensure_grayscale(
            padded
        )


        # ----------------------------------------------------
        # Save debug image
        # ----------------------------------------------------

        if debug_dir is None:
            output_dir = CROPS_DIR / "subject_second_pass"
        else:
            output_dir = Path(debug_dir)

        output_dir.mkdir(parents=True, exist_ok=True)

        debug_path = (
            output_dir
            / f"{row_name}_{variant_name}.jpg"
        )


        cv2.imwrite(

            str(
                debug_path
            ),

            padded
        )


        # ----------------------------------------------------
        # TrOCR
        # ----------------------------------------------------

        ocr_text = run_trocr(
            padded
        )


        # ----------------------------------------------------
        # Match against academic master
        # ----------------------------------------------------

        (
            subject_match,
            score
        ) = find_best_subject_match(
            ocr_text
        )


        subject_accepted = (
            score
            >=
            SUBJECT_ACCEPT_THRESHOLD
        )


        # ----------------------------------------------------
        # Store result
        # ----------------------------------------------------

        results.append({

            "variant":
                variant_name,

            "ocr_text":
                ocr_text,

            "raw_subject_candidate":
                (
                    subject_match.code
                    if subject_match
                    else None
                ),

            "subject":
                (
                    subject_match.code
                    if (
                        subject_match
                        and
                        subject_accepted
                    )
                    else None
                ),

            "subject_name":
                (
                    subject_match.name
                    if (
                        subject_match
                        and
                        subject_accepted
                    )
                    else None
                ),

            "semester":
                (
                    subject_match.semester
                    if subject_match
                    else None
                ),

            "score":
                score,

            "accepted":
                subject_accepted,

            "debug_path":
                str(
                    debug_path
                )
        })


    # ========================================================
    # SORT BEST FIRST
    # ========================================================

    results.sort(

        key=lambda result:
            result["score"],

        reverse=True
    )


    best = (
        results[0]
        if results
        else None
    )


    return {

        "best":
            best,

        "all_results":
            results
    }


# ============================================================
# STANDALONE TEST
# ============================================================

if __name__ == "__main__":


    # ========================================================
    # REAL ROW-2 PATH
    # ========================================================

    test_path = (

        PROJECT_ROOT

        /

        "data"

        /

        "crops"

        /

        "detected_rows"

        /

        "assignment_row_2.jpg"
    )


    print()
    print(
        "======================================"
    )

    print(
        "SUBJECT OCR TEST"
    )

    print(
        "======================================"
    )


    print(
        "Project root:"
    )

    print(
        PROJECT_ROOT
    )


    print()
    print(
        "Test image:"
    )

    print(
        test_path
    )


    print()
    print(
        "Exists:"
    )

    print(
        test_path.exists()
    )


    # --------------------------------------------------------
    # Stop immediately if path does not exist
    # --------------------------------------------------------

    if not test_path.exists():

        raise FileNotFoundError(

            "Test image does not exist: "
            f"{test_path}"
        )


    # ========================================================
    # RUN SECOND PASS
    # ========================================================

    result = (
        run_subject_second_pass(
            test_path
        )
    )


    # ========================================================
    # PRINT ALL RESULTS
    # ========================================================

    print()
    print(
        "======================================"
    )

    print(
        "SUBJECT SECOND PASS RESULTS"
    )

    print(
        "======================================"
    )


    for item in result[
        "all_results"
    ]:

        print()

        print(
            "Variant:",
            item["variant"]
        )


        print(
            "OCR:",
            item["ocr_text"]
        )


        print(
            "Raw Candidate:",
            item[
                "raw_subject_candidate"
            ]
        )


        print(
            "Accepted Subject:",
            (
                item["subject"]
                if item["subject"]
                else "UNKNOWN"
            )
        )


        print(
            "Semester:",
            item["semester"]
        )


        print(
            "Score:",
            round(
                item["score"],
                2
            )
        )


        print(
            "Accepted:",
            item["accepted"]
        )


        print(
            "Debug Image:",
            item["debug_path"]
        )


    # ========================================================
    # BEST RESULT
    # ========================================================

    print()
    print(
        "======================================"
    )

    print(
        "BEST SUBJECT RESULT"
    )

    print(
        "======================================"
    )


    best = result[
        "best"
    ]


    if best:

        print(
            "Variant:",
            best["variant"]
        )


        print(
            "OCR:",
            best["ocr_text"]
        )


        print(
            "Candidate:",
            best[
                "raw_subject_candidate"
            ]
        )


        print(
            "Accepted Subject:",
            (
                best["subject"]
                if best["subject"]
                else "UNKNOWN"
            )
        )


        print(
            "Score:",
            round(
                best["score"],
                2
            )
        )


        print(
            "Accepted:",
            best["accepted"]
        )


    else:

        print(
            "No subject result found."
        )