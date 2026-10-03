from __future__ import annotations

import os


def env_flag(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


DEMO_MODE = env_flag("DEMO_MODE", default=False)
SKIP_OCR = env_flag("SKIP_OCR", default=False)

TIMETABLE_ACCEPT_THRESHOLD = float(os.getenv("TIMETABLE_ACCEPT_THRESHOLD", "0.65"))
STAFF_ACCEPT_THRESHOLD = float(os.getenv("STAFF_ACCEPT_THRESHOLD", "0.80"))
ACADEMIC_ACCEPT_THRESHOLD = float(os.getenv("ACADEMIC_ACCEPT_THRESHOLD", "0.65"))
SUBJECT_ACCEPT_THRESHOLD = float(os.getenv("SUBJECT_ACCEPT_THRESHOLD", "0.60"))
INK_THRESHOLD = float(os.getenv("INK_THRESHOLD", "0.05"))
