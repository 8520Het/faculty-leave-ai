from pathlib import Path

import cv2
import numpy as np

from paths import PROCESSED_DIR, CROPS_DIR


TABLE_PATH = PROCESSED_DIR / "table_without_grid.jpg"
OUTPUT_DIR = CROPS_DIR / "detected_rows"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Relative layout fallback derived from the original template
# y-positions on a ~258px table crop.
RELATIVE_Y_RATIOS = [
    88 / 258,
    122 / 258,
    156 / 258,
    190 / 258,
    224 / 258,
    258 / 258,
]


def calculate_ink_ratio(row_image):
    if row_image is None or row_image.size == 0:
        return 0.0

    if len(row_image.shape) == 3:
        gray = cv2.cvtColor(row_image, cv2.COLOR_BGR2GRAY)
    else:
        gray = row_image

    height, width = gray.shape
    margin_x = 8
    margin_y = 4

    if width > margin_x * 2 and height > margin_y * 2:
        gray = gray[
            margin_y:height - margin_y,
            margin_x:width - margin_x,
        ]

    dark_pixels = gray < 180
    ink_pixels = np.count_nonzero(dark_pixels)
    total_pixels = gray.size
    if total_pixels == 0:
        return 0.0
    return ink_pixels / total_pixels


def _cluster_positions(values, min_gap):
    if not values:
        return []
    values = sorted(values)
    clusters = [[values[0]]]
    for value in values[1:]:
        if value - clusters[-1][-1] <= min_gap:
            clusters[-1].append(value)
        else:
            clusters.append([value])
    return [int(sum(cluster) / len(cluster)) for cluster in clusters]


def detect_row_boundaries_from_lines(table):
    if len(table.shape) == 3:
        gray = cv2.cvtColor(table, cv2.COLOR_BGR2GRAY)
    else:
        gray = table

    height, width = gray.shape
    binary = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        15,
        8,
    )
    kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT,
        (max(width // 8, 20), 1),
    )
    horizontal = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
    horizontal = cv2.dilate(horizontal, np.ones((2, 2), np.uint8), iterations=1)

    projection = np.sum(horizontal > 0, axis=1)
    threshold = max(width * 0.35, 20)
    candidates = [
        index for index, value in enumerate(projection) if value >= threshold
    ]
    clustered = _cluster_positions(candidates, min_gap=max(height // 40, 6))

    usable = [
        y for y in clustered
        if 4 <= y <= height - 4
    ]
    if height - 1 not in usable:
        usable.append(height - 1)
    if 0 not in usable and usable and usable[0] > height * 0.08:
        usable.insert(0, 0)

    usable = sorted(set(usable))
    if len(usable) < 4:
        return None, "line_detection_insufficient"
    return usable, "horizontal_lines"


def fallback_relative_boundaries(height):
    positions = [
        max(0, min(height - 1, int(round(ratio * height))))
        for ratio in RELATIVE_Y_RATIOS
    ]
    positions[0] = min(positions[0], int(height * 0.38))
    positions[-1] = height - 1
    cleaned = []
    for value in positions:
        if not cleaned or value - cleaned[-1] >= max(8, height // 30):
            cleaned.append(value)
    if cleaned[-1] != height - 1:
        cleaned.append(height - 1)
    return cleaned, "relative_layout_fallback"


def equal_split_boundaries(height, row_count=5, header_ratio=0.32):
    start = int(height * header_ratio)
    remaining = height - start
    positions = [start]
    for index in range(1, row_count + 1):
        positions.append(start + int(remaining * index / row_count))
    positions[-1] = height - 1
    return positions, "equal_split_fallback"


def choose_row_boundaries(table):
    line_bounds, strategy = detect_row_boundaries_from_lines(table)
    height = table.shape[0]

    if line_bounds and 4 <= len(line_bounds) <= 12:
        return line_bounds, strategy

    relative_bounds, relative_strategy = fallback_relative_boundaries(height)
    if len(relative_bounds) >= 4:
        return relative_bounds, relative_strategy

    return equal_split_boundaries(height)


def detect_filled_rows(
    table_path,
    ink_threshold=0.05,
    output_dir=None,
):
    table_path = Path(table_path)
    table = cv2.imread(str(table_path))
    if table is None:
        raise FileNotFoundError(
            f"Could not read cleaned table: {table_path}"
        )

    if output_dir is None:
        output_dir = OUTPUT_DIR
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    y_positions, strategy = choose_row_boundaries(table)

    detected_rows = []
    print()
    print("====================================")
    print("ROW DETECTION")
    print("====================================")
    print("Strategy:", strategy)
    print("Boundaries:", y_positions)

    for index in range(len(y_positions) - 1):
        y1 = y_positions[index]
        y2 = y_positions[index + 1]
        if y2 - y1 < 8:
            continue

        row = table[y1:y2, :]
        ink_ratio = calculate_ink_ratio(row)
        row_number = index + 1

        print(f"Row {row_number}: ink ratio = {ink_ratio:.4f}")

        debug_path = output_dir / f"row_{row_number}_debug.jpg"
        cv2.imwrite(str(debug_path), row)

        if ink_ratio >= ink_threshold:
            detected_path = output_dir / f"assignment_row_{row_number}.jpg"
            cv2.imwrite(str(detected_path), row)
            detected_rows.append(
                {
                    "row_number": row_number,
                    "image_path": detected_path,
                    "ink_ratio": ink_ratio,
                    "y1": y1,
                    "y2": y2,
                    "strategy": strategy,
                }
            )
            print("   -> FILLED")
        else:
            print("   -> EMPTY")

    print()
    print("Detected filled rows:", len(detected_rows))
    return detected_rows


if __name__ == "__main__":
    rows = detect_filled_rows(TABLE_PATH)
    print()
    print("====================================")
    print("FILLED ROWS")
    print("====================================")
    for row in rows:
        print("Row:", row["row_number"])
        print("Ink ratio:", round(row["ink_ratio"], 4))
        print("Image:", row["image_path"])
        print()
