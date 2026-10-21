import os
import shutil
from pathlib import Path
import csv
import cv2
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATASET_DIR = PROJECT_ROOT / "trocr_dataset"
IMAGES_DIR = DATASET_DIR / "images"

IMAGES_DIR.mkdir(parents=True, exist_ok=True)

# 1. Base Real Handwritten Crops already extracted by the system
SEEDS = [
    {
        "src": PROJECT_ROOT / "data/forms/test_abea_eval/crops/ocr_debug/assignment_row_1_subject.jpg",
        "text": "AI",
        "tag": "subject_ai",
    },
    {
        "src": PROJECT_ROOT / "data/forms/test_abea_eval/crops/ocr_debug/assignment_row_2_subject.jpg",
        "text": "AJT",
        "tag": "subject_ajt",
    },
    {
        "src": PROJECT_ROOT / "data/forms/test_abea_eval/crops/ocr_debug/assignment_row_1_room.jpg",
        "text": "25",
        "tag": "room_25",
    },
    {
        "src": PROJECT_ROOT / "data/forms/test_abea_eval/crops/ocr_debug/assignment_row_2_room.jpg",
        "text": "26",
        "tag": "room_26",
    },
    {
        "src": PROJECT_ROOT / "data/forms/test_abea_eval/crops/ocr_debug/assignment_row_1_staff_name.jpg",
        "text": "Sandeep R. Suthar",
        "tag": "staff_suthar",
    },
    {
        "src": PROJECT_ROOT / "data/forms/test_abea_eval/crops/ocr_debug/assignment_row_2_staff_name.jpg",
        "text": "Anand K. Patel",
        "tag": "staff_anand",
    },
    {
        "src": PROJECT_ROOT / "data/forms/test_abea_eval/crops/ocr_debug/assignment_row_1_class.jpg",
        "text": "Sem 7-F 3 Aug 2:30-3:30",
        "tag": "class_row1",
    },
    {
        "src": PROJECT_ROOT / "data/forms/test_abea_eval/crops/ocr_debug/assignment_row_2_class.jpg",
        "text": "Sem 5-D 4 Aug 10:30-11:30",
        "tag": "class_row2",
    },
    {
        "src": PROJECT_ROOT / "data/forms/test_abea_eval/crops/subject_second_pass/assignment_row_1_clahe.jpg",
        "text": "AI",
        "tag": "subject_ai_clahe",
    },
    {
        "src": PROJECT_ROOT / "data/forms/test_abea_eval/crops/subject_second_pass/assignment_row_2_clahe.jpg",
        "text": "AJT",
        "tag": "subject_ajt_clahe",
    },
    {
        "src": PROJECT_ROOT / "data/forms/test_abea_eval/crops/subject_second_pass/assignment_row_1_adaptive.jpg",
        "text": "AI",
        "tag": "subject_ai_adaptive",
    },
    {
        "src": PROJECT_ROOT / "data/forms/test_abea_eval/crops/subject_second_pass/assignment_row_2_adaptive.jpg",
        "text": "AJT",
        "tag": "subject_ajt_adaptive",
    },
]

dataset_rows = []
img_counter = 1

def augment_and_save(img, text, prefix):
    global img_counter
    # Original
    filename = f"crop_{img_counter:03d}_{prefix}.jpg"
    cv2.imwrite(str(IMAGES_DIR / filename), img)
    dataset_rows.append({"file_name": filename, "text": text})
    img_counter += 1

    # Contrast Boost (Alpha = 1.3, Beta = 10)
    contrast = cv2.convertScaleAbs(img, alpha=1.3, beta=10)
    filename = f"crop_{img_counter:03d}_{prefix}_contrast.jpg"
    cv2.imwrite(str(IMAGES_DIR / filename), contrast)
    dataset_rows.append({"file_name": filename, "text": text})
    img_counter += 1

    # CLAHE
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    clahe_img = clahe.apply(gray)
    filename = f"crop_{img_counter:03d}_{prefix}_clahe.jpg"
    cv2.imwrite(str(IMAGES_DIR / filename), clahe_img)
    dataset_rows.append({"file_name": filename, "text": text})
    img_counter += 1

    # Slight Gaussian Blur (simulates camera focus blur)
    blurred = cv2.GaussianBlur(img, (3, 3), 0)
    filename = f"crop_{img_counter:03d}_{prefix}_blur.jpg"
    cv2.imwrite(str(IMAGES_DIR / filename), blurred)
    dataset_rows.append({"file_name": filename, "text": text})
    img_counter += 1


for item in SEEDS:
    src_path = item["src"]
    if src_path.exists():
        img = cv2.imread(str(src_path))
        if img is not None:
            augment_and_save(img, item["text"], item["tag"])

csv_path = DATASET_DIR / "metadata.csv"
with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["file_name", "text"])
    writer.writeheader()
    writer.writerows(dataset_rows)

print(f"Dataset generated: {len(dataset_rows)} samples saved in {IMAGES_DIR} and {csv_path}")
