from pathlib import Path

import cv2
import numpy as np


def _largest_content_contour(gray):
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    edges = cv2.dilate(edges, np.ones((3, 3), np.uint8), iterations=1)
    contours, _ = cv2.findContours(
        edges,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE,
    )
    if not contours:
        return None
    return max(contours, key=cv2.contourArea)


def deskew_image(image):
    if image is None or image.size == 0:
        raise ValueError("Empty page image")

    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image

    contour = _largest_content_contour(gray)
    if contour is None:
        return image, 0.0

    angle = cv2.minAreaRect(contour)[-1]
    if angle < -45:
        angle = 90 + angle
    if abs(angle) < 0.4 or abs(angle) > 15:
        return image, 0.0

    height, width = image.shape[:2]
    matrix = cv2.getRotationMatrix2D((width / 2, height / 2), angle, 1.0)
    rotated = cv2.warpAffine(
        image,
        matrix,
        (width, height),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REPLICATE,
    )
    return rotated, float(angle)


def normalize_page(image, max_width=1800):
    if image is None or image.size == 0:
        raise ValueError("Could not read uploaded form image")

    deskewed, angle = deskew_image(image)
    height, width = deskewed.shape[:2]
    if width > max_width:
        scale = max_width / width
        deskewed = cv2.resize(
            deskewed,
            None,
            fx=scale,
            fy=scale,
            interpolation=cv2.INTER_AREA,
        )

    if len(deskewed.shape) == 3:
        gray = cv2.cvtColor(deskewed, cv2.COLOR_BGR2GRAY)
    else:
        gray = deskewed
        deskewed = cv2.cvtColor(deskewed, cv2.COLOR_GRAY2BGR)

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    normalized = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)

    return {
        "image": normalized,
        "color": deskewed,
        "angle": angle,
        "width": normalized.shape[1],
        "height": normalized.shape[0],
    }
