"""Repository-relative paths and per-form working directories."""

from __future__ import annotations

import sys
from pathlib import Path


APP_DIR = Path(__file__).resolve().parent
BACKEND_DIR = APP_DIR.parent
PROJECT_ROOT = BACKEND_DIR.parent

if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
CROPS_DIR = DATA_DIR / "crops"
FORMS_DIR = DATA_DIR / "forms"
DB_PATH = DATA_DIR / "faculty_leave.db"


def ensure_base_dirs() -> None:
    for directory in (
        DATA_DIR,
        RAW_DIR,
        PROCESSED_DIR,
        CROPS_DIR,
        FORMS_DIR,
        CROPS_DIR / "detected_rows",
        CROPS_DIR / "ocr_debug",
        CROPS_DIR / "class_second_pass",
        CROPS_DIR / "subject_second_pass",
        CROPS_DIR / "clean_rows",
    ):
        directory.mkdir(parents=True, exist_ok=True)


def form_dir(form_id: str) -> Path:
    return FORMS_DIR / form_id


def form_paths(form_id: str) -> dict[str, Path]:
    root = form_dir(form_id)
    paths = {
        "root": root,
        "processed": root / "processed",
        "crops": root / "crops",
        "rows": root / "crops" / "rows",
        "ocr_debug": root / "crops" / "ocr_debug",
        "class_second_pass": root / "crops" / "class_second_pass",
        "subject_second_pass": root / "crops" / "subject_second_pass",
    }
    for directory in paths.values():
        directory.mkdir(parents=True, exist_ok=True)
    return paths


ensure_base_dirs()
