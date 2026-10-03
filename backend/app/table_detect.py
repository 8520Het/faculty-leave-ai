from pathlib import Path

import cv2
import numpy as np


def _line_masks(gray):
    binary = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        21,
        8,
    )
    height, width = gray.shape
    horizontal_kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT,
        (max(width // 15, 25), 1),
    )
    vertical_kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT,
        (1, max(height // 20, 15)),
    )
    horizontal = cv2.morphologyEx(binary, cv2.MORPH_OPEN, horizontal_kernel)
    vertical = cv2.morphologyEx(binary, cv2.MORPH_OPEN, vertical_kernel)
    grid = cv2.bitwise_or(horizontal, vertical)
    grid = cv2.dilate(grid, np.ones((3, 3), np.uint8), iterations=2)
    return binary, horizontal, vertical, grid


def detect_table_from_grid(image):
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image

    _, _, _, grid = _line_masks(gray)
    contours, _ = cv2.findContours(
        grid,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE,
    )
    height, width = gray.shape
    best = None
    best_area = 0

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        area = w * h
        if w < width * 0.55:
            continue
        if h < height * 0.12:
            continue
        if h > height * 0.85:
            continue
        if area > best_area:
            best_area = area
            best = (x, y, w, h)

    if best is None:
        return None, "grid_not_found"
    return best, "grid_contour"


def fallback_lower_region(image):
    height, width = image.shape[:2]
    y1 = int(height * 0.52)
    box = (int(width * 0.03), y1, int(width * 0.94), int(height * 0.45))
    return box, "lower_page_fallback"


def crop_box(image, box, padding=8):
    x, y, w, h = box
    height, width = image.shape[:2]
    x1 = max(0, x - padding)
    y1 = max(0, y - padding)
    x2 = min(width, x + w + padding)
    y2 = min(height, y + h + padding)
    return image[y1:y2, x1:x2], (x1, y1, x2 - x1, y2 - y1)


def detect_arrangement_table(image):
    box, strategy = detect_table_from_grid(image)
    if box is None:
        box, strategy = fallback_lower_region(image)

    crop, used_box = crop_box(image, box)
    if crop is None or crop.size == 0:
        return image, (0, 0, image.shape[1], image.shape[0]), "full_image_fallback"

    if crop.shape[0] < 80 or crop.shape[1] < 120:
        return image, (0, 0, image.shape[1], image.shape[0]), "full_image_fallback"

    return crop, used_box, strategy
