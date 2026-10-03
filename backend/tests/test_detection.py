import numpy as np

from detect_filled_rows import choose_row_boundaries, calculate_ink_ratio
from page_normalize import normalize_page
from table_detect import detect_arrangement_table


def test_normalize_and_table_fallback():
    image = np.full((800, 1200, 3), 240, dtype=np.uint8)
    image[430:720, 40:1160] = 255
    image[430:720, 40:1160][::20] = 0
    result = normalize_page(image)
    crop, box, strategy = detect_arrangement_table(result["image"])
    assert crop.size > 0
    assert box[2] > 100
    assert strategy in {
        "grid_contour",
        "lower_page_fallback",
        "full_image_fallback",
    }


def test_row_boundary_fallback_and_ink():
    table = np.full((260, 640, 3), 250, dtype=np.uint8)
    table[130:155, 20:600] = 20
    bounds, strategy = choose_row_boundaries(table)
    assert len(bounds) >= 4
    assert strategy in {
        "horizontal_lines",
        "relative_layout_fallback",
        "equal_split_fallback",
    }
    filled = calculate_ink_ratio(table[130:155])
    empty = calculate_ink_ratio(table[20:50])
    assert filled > empty
