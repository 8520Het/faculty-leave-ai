from pathlib import Path
from typing import Optional, Dict, Any
import cv2
import torch
from PIL import Image

import ocr_fields
from staff_matcher import match_staff_member, similarity
from table_detect import detect_table_from_grid


def extract_applicant_name_crop(image) -> Optional[Any]:
    if image is None:
        return None
    H, W = image.shape[:2]
    try:
        (x, y, w, h), _ = detect_table_from_grid(image)
        header_h = y
    except Exception:
        header_h = int(H * 0.38)

    if header_h < 150 or header_h > int(H * 0.65):
        header_h = int(H * 0.38)

    # In standard DDU leave sheets, the handwritten Name in Full is between 46% and 57% of table y
    # and roughly between 22% and 68% across width
    y1 = int(header_h * 0.46)
    y2 = int(header_h * 0.57)
    x1 = int(W * 0.22)
    x2 = int(W * 0.68)
    name_crop = image[y1:y2, x1:x2]
    if name_crop.size == 0 or name_crop.shape[0] < 15 or name_crop.shape[1] < 40:
        return None
    return name_crop


def verify_applicant_identity(
    image_path: str | Path,
    logged_in_applicant: str,
) -> Dict[str, Any]:
    """
    Validates that the handwritten name written in the 'Name in Full'
    header section of the uploaded leave application matches the logged-in faculty.
    Prevents cross-account uploads (e.g. Prof. Harshad uploading Prof. Anand's sheet).
    """
    img = cv2.imread(str(image_path))
    if img is None:
        return {"valid": True, "detected_name": None, "reason": "Unreadable image"}

    name_crop = extract_applicant_name_crop(img)
    if name_crop is None:
        return {"valid": True, "detected_name": None, "reason": "No header crop"}

    try:
        ocr_fields._load_trocr()
        rgb = cv2.cvtColor(name_crop, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb)
        pixel_values = ocr_fields.PROCESSOR(pil_img, return_tensors="pt").pixel_values.to(
            ocr_fields.DEVICE
        )
        with torch.no_grad():
            generated_ids = ocr_fields.MODEL.generate(pixel_values, max_new_tokens=40)
        raw_ocr = (
            ocr_fields.PROCESSOR.batch_decode(generated_ids, skip_special_tokens=True)[0]
            .strip(" \"':\t\n")
        )
    except Exception as exc:
        print(f"Warning: Failed to OCR header Name in Full: {exc}")
        return {"valid": True, "detected_name": None, "reason": str(exc)}

    # Clean prefix like "Name in Full :" if caught in crop
    for prefix in ["name in full", "name", "full name", "applicant"]:
        if raw_ocr.lower().startswith(prefix):
            raw_ocr = raw_ocr[len(prefix):].strip(" :-\"'")

    detected_match = match_staff_member(raw_ocr)
    logged_in_match = match_staff_member(logged_in_applicant)

    detected_staff = detected_match.matched_staff
    logged_in_staff = logged_in_match.matched_staff

    # If we confidently detected a faculty name from the roster:
    if detected_staff and logged_in_staff:
        # Check if they are distinct faculty members
        if detected_staff.staff_id != logged_in_staff.staff_id and detected_match.score >= 0.70:
            return {
                "valid": False,
                "detected_name": detected_staff.name,
                "logged_in_name": logged_in_staff.name,
                "raw_ocr": raw_ocr,
                "score": detected_match.score,
                "error": (
                    f"Identity Mismatch: The uploaded leave application form belongs to "
                    f"'{detected_staff.name}' (from the 'Name in Full' section), "
                    f"but you are logged in as '{logged_in_staff.name}'. "
                    f"You can only upload leave applications for your own account."
                ),
            }

    # Also check direct string similarity if not in staff roster
    if detected_staff and not logged_in_staff:
        if similarity(detected_staff.name, logged_in_applicant) < 0.60:
            return {
                "valid": False,
                "detected_name": detected_staff.name,
                "logged_in_name": logged_in_applicant,
                "raw_ocr": raw_ocr,
                "error": (
                    f"Identity Mismatch: Uploaded form contains applicant name '{detected_staff.name}', "
                    f"which does not match your logged-in name '{logged_in_applicant}'."
                ),
            }

    return {
        "valid": True,
        "detected_name": detected_staff.name if detected_staff else raw_ocr,
        "logged_in_name": logged_in_staff.name if logged_in_staff else logged_in_applicant,
        "raw_ocr": raw_ocr,
    }
