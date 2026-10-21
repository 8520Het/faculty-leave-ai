"""
Generate clean, publication-grade Black & White / Grayscale diagrams for DDU Project Report.
Specifically designed for high-contrast academic print and thesis binding.
Emphasizes the core workflow: Faculty uploads handwritten form -> Image processing -> TrOCR -> Review.
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Polygon
import numpy as np

OUTPUT_DIR = r"c:\Users\HP\Desktop\faculty-leave-ai\docs\figures"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# B&W / Grayscale Palette
C_BLACK = "#000000"
C_WHITE = "#FFFFFF"
C_GRAY_LIGHT = "#F8F9FA"
C_GRAY_MID = "#E9ECEF"
C_GRAY_DARK = "#495057"
C_LINE = "#212529"

def draw_bw_actor(ax, x, y, label, scale=1.0):
    """Draws a crisp black & white UML actor stick figure."""
    head = plt.Circle((x, y + 0.35 * scale), 0.13 * scale, color=C_BLACK, fill=False, lw=2.0)
    ax.add_patch(head)
    ax.plot([x, x], [y + 0.22 * scale, y - 0.15 * scale], color=C_BLACK, lw=2.0)
    ax.plot([x - 0.22 * scale, x + 0.22 * scale], [y + 0.08 * scale, y + 0.08 * scale], color=C_BLACK, lw=2.0)
    ax.plot([x, x - 0.18 * scale], [y - 0.15 * scale, y - 0.45 * scale], color=C_BLACK, lw=2.0)
    ax.plot([x, x + 0.18 * scale], [y - 0.15 * scale, y - 0.45 * scale], color=C_BLACK, lw=2.0)
    ax.text(x, y - 0.65 * scale, label, ha='center', va='top', fontsize=10, fontweight='bold', color=C_BLACK)

def draw_bw_use_case(ax, x, y, text, w=2.8, h=0.7, fill_gray=False, dashed=False):
    """Draws a black & white UML Use Case ellipse."""
    bg = C_GRAY_MID if fill_gray else C_WHITE
    ls = '--' if dashed else '-'
    ellipse = patches.Ellipse((x, y), w, h, facecolor=bg, edgecolor=C_BLACK, lw=1.8, linestyle=ls, zorder=3)
    ax.add_patch(ellipse)
    ax.text(x, y, text, ha='center', va='center', fontsize=9.2, fontweight='bold', color=C_BLACK, zorder=4)

def draw_bw_box(ax, x, y, w, h, title, subtitle="", fill_color=C_WHITE, lw=1.6, radius=0.06, dashed=False):
    """Draws a rounded rectangular box in black & white."""
    ls = '--' if dashed else '-'
    box = FancyBboxPatch((x - w/2, y - h/2), w, h,
                         boxstyle=f"round,pad={radius},rounding_size={radius}",
                         facecolor=fill_color, edgecolor=C_BLACK, lw=lw, linestyle=ls, zorder=2)
    ax.add_patch(box)
    if subtitle:
        ax.text(x, y + 0.16 * h, title, ha='center', va='center', fontsize=10, fontweight='bold', color=C_BLACK, zorder=3)
        ax.text(x, y - 0.20 * h, subtitle, ha='center', va='center', fontsize=8.5, color=C_GRAY_DARK, zorder=3)
    else:
        ax.text(x, y, title, ha='center', va='center', fontsize=9.5, fontweight='bold', color=C_BLACK, zorder=3)

# =============================================================================
# 1. Figure 4.1: UML Use Case Diagram (Black & White)
# =============================================================================
def generate_bw_fig_4_1():
    fig, ax = plt.subplots(figsize=(13, 9.5), dpi=300)
    ax.set_xlim(-1, 13)
    ax.set_ylim(-1, 10.5)
    ax.axis('off')

    # Boundary Box
    sys_box = FancyBboxPatch((2.2, 0.2), 7.6, 9.8, boxstyle="round,pad=0.1,rounding_size=0.15",
                            facecolor=C_WHITE, edgecolor=C_BLACK, lw=2.2)
    ax.add_patch(sys_box)
    ax.text(6.0, 9.6, "Faculty Leave AI Portal (System Boundary)", ha='center', va='center',
            fontsize=12.5, fontweight='bold', color=C_BLACK)

    # Actors
    draw_bw_actor(ax, 0.8, 7.8, "Faculty Applicant\n(Primary Actor)", scale=0.95)
    draw_bw_actor(ax, 0.8, 2.8, "Timetable\nAdministrator", scale=0.9)
    draw_bw_actor(ax, 11.2, 7.8, "Head of Department\n(HOD)", scale=0.9)
    draw_bw_actor(ax, 11.2, 2.8, "Substitute Faculty\nMember", scale=0.9)

    # Core Use Cases (Removed <<include>> as requested)
    use_cases = [
        (6.0, 8.6, "Upload Handwritten\nLeave Slip Photo", False),
        (6.0, 7.3, "Review Scanned Form &\nInline Error Correction", False),
        (6.0, 6.0, "Verify Timetable Constraints\n& Teaching Clashes", False),
        (6.0, 4.7, "Ingest Master Weekly\nDepartment Timetable", False),
        (6.0, 3.4, "Query Personal Weekly\nTeaching Commitments", False),
        (6.0, 2.1, "Dispatch Automated\nSubstitute Notifications", False),
        (6.0, 0.8, "Digital 1-Click Substitution\nAcknowledgment & HOD Signoff", False),
    ]

    for x, y, label, is_gray in use_cases:
        draw_bw_use_case(ax, x, y, label, w=3.4, h=0.85, fill_gray=is_gray, dashed=False)

    # Solid UML Actor-to-Use-Case Association Lines
    # Faculty Applicant associations
    for target_y in [8.6, 7.3, 3.4]:
        ax.plot([0.8, 6.0 - 1.7], [7.8, target_y], color=C_BLACK, lw=1.6, zorder=1)

    # Timetable Administrator associations
    for target_y in [4.7]:
        ax.plot([0.8, 6.0 - 1.7], [2.8, target_y], color=C_BLACK, lw=1.6, zorder=1)

    # Head of Department (HOD) associations
    for target_y in [7.3, 6.0, 0.8]:
        ax.plot([11.2, 6.0 + 1.7], [7.8, target_y], color=C_BLACK, lw=1.6, zorder=1)

    # Substitute Faculty Member associations
    for target_y in [3.4, 2.1, 0.8]:
        ax.plot([11.2, 6.0 + 1.7], [2.8, target_y], color=C_BLACK, lw=1.6, zorder=1)

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, "fig_4_1_use_case.png")
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print("Generated B&W:", out_path)

# =============================================================================
# 2. Figure 4.2: High-Level Layered Architecture (Black & White)
# =============================================================================
def generate_bw_fig_4_2():
    fig, ax = plt.subplots(figsize=(14, 10), dpi=300)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 11)
    ax.axis('off')

    ax.text(7.0, 10.6, "Faculty Leave AI: High-Level Layered System Architecture",
            ha='center', va='center', fontsize=13.5, fontweight='bold', color=C_BLACK)

    layers = [
        ("Layer 1: Presentation Tier (React 19 + TypeScript + Tailwind CSS)", 8.8, 1.6, False, [
            ("HOD Executive\nDashboard", 2.3),
            ("Faculty Leave Form\nUpload Dropzone", 4.7),
            ("AI Vision Progress\nStepper Indicator", 7.1),
            ("Scanned Leave Review\n& Error Desk", 9.5),
            ("Substitute Notification\n& Acknowledgment Desk", 11.9)
        ]),
        ("Layer 2: REST API Gateway & Application Controller (FastAPI)", 6.5, 1.4, True, [
            ("Uvicorn ASGI Server\n(Port 8000)", 2.8),
            ("Pydantic v2 Schema Validation\n& Multipart Ingestion", 7.0),
            ("Role Session Security\n& Error Handlers", 11.2)
        ]),
        ("Layer 3: Core AI Processing & Analytical Subsystem (Core Focus)", 3.8, 2.0, False, [
            ("Radon Deskew &\nBilateral Filtering", 2.5),
            ("OpenCV Morphological\nGrid Slicer (Kh & Kv)", 5.5),
            ("Microsoft TrOCR Base\nCursive Transformer HTR", 8.5),
            ("Multi-Factor Timetable\nVerification Engine", 11.5)
        ]),
        ("Layer 4: Data Persistence & Physical Storage Tier (SQLite 3.45 WAL)", 1.2, 1.4, True, [
            ("SQLite Relational DB\n(Write-Ahead Logging)", 3.5),
            ("SQLAlchemy 2.0 ORM\nEntity Models", 7.0),
            ("Local Disk Storage\n(Raw Leave Slips & Crops)", 10.5)
        ]),
    ]

    for title, y_c, h, fill_gray, boxes in layers:
        bg = C_GRAY_LIGHT if fill_gray else C_WHITE
        layer_box = FancyBboxPatch((0.6, y_c - h/2), 12.8, h, boxstyle="round,pad=0.08,rounding_size=0.12",
                                   facecolor=bg, edgecolor=C_BLACK, lw=2.0)
        ax.add_patch(layer_box)
        ax.text(1.0, y_c + h/2 - 0.22, title, fontsize=10.5, fontweight='bold', color=C_BLACK)

        for box_title, x_pos in boxes:
            bw = 2.15 if len(boxes) >= 4 else 3.2
            bh = h * 0.58
            by = y_c - 0.08
            box = FancyBboxPatch((x_pos - bw/2, by - bh/2), bw, bh,
                                 boxstyle="round,pad=0.05,rounding_size=0.08",
                                 facecolor=C_WHITE, edgecolor=C_BLACK, lw=1.4)
            ax.add_patch(box)
            ax.text(x_pos, by, box_title, ha='center', va='center', fontsize=8.8, fontweight='bold', color=C_BLACK)

    for y_arrow in [7.7, 5.4, 2.5]:
        for x_arr in [3.5, 7.0, 10.5]:
            ax.annotate("", xy=(x_arr, y_arrow - 0.3), xytext=(x_arr, y_arrow + 0.3),
                        arrowprops=dict(arrowstyle="<->", color=C_BLACK, lw=1.8))

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, "fig_4_2_system_architecture.png")
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print("Generated B&W:", out_path)

# =============================================================================
# 3. Figure 4.3: Document Processing Activity Flowchart (Black & White)
# =============================================================================
def generate_bw_fig_4_3():
    fig, ax = plt.subplots(figsize=(11, 13), dpi=300)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 13)
    ax.axis('off')

    ax.text(5.5, 12.6, "Document Ingestion & Processing Pipeline Activity Flow",
            ha='center', va='center', fontsize=13, fontweight='bold', color=C_BLACK)

    # Start
    start_c = plt.Circle((5.5, 12.0), 0.22, color=C_BLACK, zorder=4)
    ax.add_patch(start_c)
    ax.text(5.5, 12.0, "Start", ha='center', va='center', fontsize=8.5, color=C_WHITE, fontweight='bold', zorder=5)

    steps = [
        (5.5, 11.0, "box", "1. Faculty Takes Photo of Physical Leave Application Slip\n& Uploads via Web Dropzone (JPEG / PNG)"),
        (5.5, 9.9, "box", "2. Image Preprocessing & Geometric Normalization\n(Grayscale, Bilateral Noise Reduction, Radon Deskewing)"),
        (5.5, 8.8, "box", "3. Morphological Grid Line Extraction\n(Directional Kernels: Kh for Rows & Kv for Columns)"),
        (5.5, 7.7, "box", "4. Table Cell Segmentation & Bounding-Box Detection"),
        (5.5, 6.4, "diamond", "Ink Ratio > 0.015?\n(Blank Row Check)"),
        (2.4, 6.4, "box_skip", "Discard Blank Row\n(Prevent Hallucinations)"),
        (5.5, 5.0, "box", "5. CLAHE Contrast Normalization &\nLocal Tile Equalization (ClipLimit = 2.5)"),
        (5.5, 3.9, "box", "6. Microsoft TrOCR Vision Transformer HTR\n(Decode Division, Date, Time, Subject, Substitute)"),
        (5.5, 2.7, "diamond", "Timetable Verification:\nAny Clashes Flagged?"),
        (2.4, 2.7, "box_alert", "Render Red Alert Cards &\nProvide Inline Editable Fields"),
        (5.5, 1.4, "box_valid", "Mark Status: 'VALID' (Clean Verification) &\nDispatch Automated Substitute Notification"),
    ]

    for x, y, ntype, text in steps:
        if ntype == "box":
            draw_bw_box(ax, x, y, 4.8, 0.75, text, fill_color=C_WHITE)
        elif ntype == "box_skip":
            draw_bw_box(ax, x, y, 2.4, 0.7, text, fill_color=C_GRAY_MID, dashed=True)
        elif ntype == "box_alert":
            draw_bw_box(ax, x, y, 3.0, 0.75, text, fill_color=C_GRAY_MID, lw=2.0)
        elif ntype == "box_valid":
            draw_bw_box(ax, x, y, 4.8, 0.75, text, fill_color=C_GRAY_LIGHT, lw=2.0)
        elif ntype == "diamond":
            poly = Polygon([[x, y+0.5], [x+1.5, y], [x, y-0.5], [x-1.5, y]],
                           facecolor=C_WHITE, edgecolor=C_BLACK, lw=1.8, zorder=3)
            ax.add_patch(poly)
            ax.text(x, y, text, ha='center', va='center', fontsize=8.5, fontweight='bold', color=C_BLACK, zorder=4)

    # End
    end_c1 = plt.Circle((5.5, 0.4), 0.24, color=C_BLACK, fill=False, lw=2.2, zorder=4)
    end_c2 = plt.Circle((5.5, 0.4), 0.16, color=C_BLACK, zorder=4)
    ax.add_patch(end_c1)
    ax.add_patch(end_c2)
    ax.text(5.5, 0.05, "End", ha='center', va='center', fontsize=9, fontweight='bold', color=C_BLACK)

    # Connections
    conns = [
        ((5.5, 11.78), (5.5, 11.4)),
        ((5.5, 10.6), (5.5, 10.3)),
        ((5.5, 9.5), (5.5, 9.2)),
        ((5.5, 8.4), (5.5, 8.1)),
        ((5.5, 7.3), (5.5, 6.9)),
        ((5.5, 5.9), (5.5, 5.4)),
        ((5.5, 4.6), (5.5, 4.3)),
        ((5.5, 3.5), (5.5, 3.2)),
        ((5.5, 2.2), (5.5, 1.8)),
        ((5.5, 1.0), (5.5, 0.65)),
    ]
    for start, end in conns:
        ax.annotate("", xy=end, xytext=start, arrowprops=dict(arrowstyle="->", color=C_BLACK, lw=1.8))

    ax.annotate("", xy=(3.6, 6.4), xytext=(4.0, 6.4), arrowprops=dict(arrowstyle="->", color=C_BLACK, lw=1.8))
    ax.text(3.8, 6.55, "No", fontsize=8.5, fontweight='bold', color=C_BLACK)
    ax.text(5.65, 5.65, "Yes", fontsize=8.5, fontweight='bold', color=C_BLACK)

    ax.annotate("", xy=(3.9, 2.7), xytext=(4.0, 2.7), arrowprops=dict(arrowstyle="->", color=C_BLACK, lw=1.8))
    ax.text(3.7, 2.85, "Yes (Clash)", fontsize=8.5, fontweight='bold', color=C_BLACK)
    ax.text(5.65, 2.0, "No (Valid)", fontsize=8.5, fontweight='bold', color=C_BLACK)

    ax.annotate("", xy=(4.0, 1.6), xytext=(2.4, 2.3),
                arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=-0.2", color=C_BLACK, lw=1.8))
    ax.text(2.6, 1.7, "Inline Corrected", fontsize=8, fontweight='bold', color=C_BLACK)

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, "fig_4_3_document_activity_flow.png")
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print("Generated B&W:", out_path)

# =============================================================================
# 4. Figure 4.4: UML Sequence Diagram (Black & White)
# =============================================================================
def generate_bw_fig_4_4():
    fig, ax = plt.subplots(figsize=(14, 10.5), dpi=300)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 11)
    ax.axis('off')

    ax.text(7.0, 10.6, "UML Sequence Diagram: Form Upload, Ingestion, and Review Workflow",
            ha='center', va='center', fontsize=13.5, fontweight='bold', color=C_BLACK)

    lifelines = [
        ("Faculty\nApplicant", 1.2),
        ("React UI\n(Frontend)", 3.4),
        ("FastAPI\nController", 5.6),
        ("TrOCR Vision\nWorker", 7.8),
        ("Timetable Verification\nEngine", 10.0),
        ("Substitute\nFaculty", 12.2)
    ]

    for label, x in lifelines:
        draw_bw_box(ax, x, 9.8, 1.8, 0.7, label, fill_color=C_GRAY_LIGHT)
        ax.plot([x, x], [0.5, 9.45], color=C_BLACK, linestyle="--", lw=1.4, zorder=1)

    messages = [
        (9.0, 1.2, 3.4, "1. Upload handwritten leave form photo", False),
        (8.4, 3.4, 5.6, "2. POST /api/forms/upload (multipart image)", False),
        (7.8, 5.6, 7.8, "3. segment_grid_and_extract_rows(image)", False),
        (7.2, 7.8, 7.8, "4. trocr_infer_tokens() [CLAHE-enhanced]", False),
        (6.6, 7.8, 5.6, "5. return extracted_candidate_rows[]", True),
        (6.0, 5.6, 10.0, "6. verify_constraints(extracted_rows)", False),
        (5.4, 10.0, 10.0, "7. cross-reference timetable & substitute availability", False),
        (4.8, 10.0, 5.6, "8. return conflict_flags[] and warnings", True),
        (4.2, 5.6, 3.4, "9. 200 OK: payload with flagged discrepancies", True),
        (3.6, 3.4, 1.2, "10. Render review desk (scanned slip + red alert cards)", True),
        (3.0, 1.2, 3.4, "11. Save inline manual correction", False),
        (2.4, 3.4, 5.6, "12. PUT /api/forms/{id}/rows (persist valid rows)", False),
        (1.8, 5.6, 12.2, "13. Dispatch substitution email notification", False),
        (1.2, 12.2, 5.6, "14. Click 1-Click Digital Acknowledge button", False),
        (0.6, 5.6, 3.4, "15. SSE update: status = 'CONFIRMED'", True),
    ]

    for y, x1, x2, text, is_ret in messages:
        ls = "--" if is_ret else "-"
        if x1 == x2:
            loop_x = [x1, x1 + 0.6, x1 + 0.6, x1]
            loop_y = [y + 0.15, y + 0.15, y - 0.15, y - 0.15]
            ax.plot(loop_x, loop_y, color=C_BLACK, lw=1.6)
            ax.annotate("", xy=(x1, y - 0.15), xytext=(x1 + 0.2, y - 0.15),
                        arrowprops=dict(arrowstyle="->", color=C_BLACK, lw=1.6))
            ax.text(x1 + 0.7, y, text, ha='left', va='center', fontsize=8.5, color=C_BLACK, fontweight='bold')
        else:
            ax.annotate("", xy=(x2, y), xytext=(x1, y),
                        arrowprops=dict(arrowstyle="->", linestyle=ls, color=C_BLACK, lw=1.6))
            mid_x = (x1 + x2) / 2
            ax.text(mid_x, y + 0.14, text, ha='center', va='bottom', fontsize=8.5, color=C_BLACK, fontweight='semibold')

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, "fig_4_4_sequence_diagram.png")
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print("Generated B&W:", out_path)

# =============================================================================
# 5. Figure 4.5: Entity-Relationship Diagram (ERD) (Black & White)
# =============================================================================
def generate_bw_fig_4_5():
    fig, ax = plt.subplots(figsize=(14, 10.5), dpi=300)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 11)
    ax.axis('off')

    ax.text(7.0, 10.6, "Relational Database Schema & Entity-Relationship Diagram (SQLite / SQLAlchemy)",
            ha='center', va='center', fontsize=13.5, fontweight='bold', color=C_BLACK)

    def draw_bw_entity(x, y, w, h, table_name, columns):
        hdr_h = 0.55
        hdr = FancyBboxPatch((x - w/2, y + h/2 - hdr_h), w, hdr_h,
                             boxstyle="round,pad=0.04,rounding_size=0.08",
                             facecolor=C_GRAY_MID, edgecolor=C_BLACK, lw=1.6, zorder=3)
        ax.add_patch(hdr)
        ax.text(x, y + h/2 - hdr_h/2, table_name, ha='center', va='center',
                fontsize=10.5, fontweight='bold', color=C_BLACK, zorder=4)

        body = FancyBboxPatch((x - w/2, y - h/2), w, h - hdr_h,
                              boxstyle="round,pad=0.04,rounding_size=0.08",
                              facecolor=C_WHITE, edgecolor=C_BLACK, lw=1.6, zorder=2)
        ax.add_patch(body)

        col_y = y + h/2 - hdr_h - 0.25
        for col_def in columns:
            is_key = "PK" in col_def or "FK" in col_def
            font_wt = 'bold' if is_key else 'normal'
            ax.text(x - w/2 + 0.15, col_y, col_def, ha='left', va='center',
                    fontsize=8.5, color=C_BLACK, fontweight=font_wt, zorder=3)
            col_y -= 0.28

    draw_bw_entity(3.0, 7.8, 4.4, 3.4, "leave_forms", [
        "id: UUID [PK]",
        "applicant_name: VARCHAR(100)",
        "faculty_code: VARCHAR(10)",
        "leave_date: DATE",
        "reason: TEXT",
        "image_url: VARCHAR(255)",
        "status: ENUM [PENDING, REVIEWED, APPROVED]",
        "created_at: TIMESTAMP",
        "reviewed_at: TIMESTAMP"
    ])

    draw_bw_entity(3.0, 2.8, 4.8, 4.2, "leave_arrangements", [
        "id: INTEGER [PK, AUTOINCREMENT]",
        "form_id: UUID [FK -> leave_forms.id]",
        "original_row_idx: INTEGER",
        "class_division: VARCHAR(20)",
        "lecture_date: DATE",
        "start_time: TIME",
        "end_time: TIME",
        "subject_code: VARCHAR(20)",
        "room_no: VARCHAR(20)",
        "substitute_faculty_code: VARCHAR(20)",
        "substitute_status: ENUM [PENDING, ACCEPTED]",
        "has_conflict: BOOLEAN",
        "conflict_type: VARCHAR(50)"
    ])

    draw_bw_entity(10.5, 7.8, 4.8, 3.8, "timetable_entries", [
        "id: INTEGER [PK, AUTOINCREMENT]",
        "academic_year: VARCHAR(20)",
        "semester: INTEGER",
        "division: VARCHAR(5)",
        "day_of_week: INTEGER [1-6]",
        "start_time: TIME",
        "end_time: TIME",
        "subject_code: VARCHAR(20)",
        "subject_name: VARCHAR(100)",
        "room_no: VARCHAR(20)",
        "faculty_code: VARCHAR(20)",
        "is_lab: BOOLEAN"
    ])

    draw_bw_entity(10.5, 3.2, 4.4, 3.2, "faculty_profiles", [
        "id: INTEGER [PK, AUTOINCREMENT]",
        "faculty_code: VARCHAR(20) [UNIQUE]",
        "full_name: VARCHAR(100)",
        "email: VARCHAR(100) [UNIQUE]",
        "phone: VARCHAR(20)",
        "department: VARCHAR(50)",
        "designation: VARCHAR(50)",
        "is_active: BOOLEAN"
    ])

    ax.plot([3.0, 3.0], [6.1, 4.9], color=C_BLACK, lw=2.0)
    ax.text(3.15, 5.85, "1", fontsize=10, fontweight='bold', color=C_BLACK)
    ax.text(3.15, 5.15, "N", fontsize=10, fontweight='bold', color=C_BLACK)

    ax.plot([5.4, 8.3], [2.8, 3.2], color=C_BLACK, lw=2.0)
    ax.text(5.6, 2.95, "N", fontsize=10, fontweight='bold', color=C_BLACK)
    ax.text(8.0, 3.35, "1", fontsize=10, fontweight='bold', color=C_BLACK)

    ax.plot([10.5, 10.5], [5.9, 4.8], color=C_BLACK, lw=2.0)
    ax.text(10.65, 5.7, "N", fontsize=10, fontweight='bold', color=C_BLACK)
    ax.text(10.65, 5.0, "1", fontsize=10, fontweight='bold', color=C_BLACK)

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, "fig_4_5_database_erd.png")
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print("Generated B&W:", out_path)

# =============================================================================
# 6. Figure 5.1: Morphological Grid Filtering (Black & White)
# =============================================================================
def generate_bw_fig_5_1():
    fig, axes = plt.subplots(1, 4, figsize=(15, 4.5), dpi=300)
    fig.suptitle("Morphological Grid Kernel Filtering & Row Bounding-Box Slicing",
                 fontsize=13, fontweight='bold', color=C_BLACK, y=1.02)

    ax = axes[0]
    ax.set_title("(a) Raw Photographed Crop", fontsize=10, fontweight='bold')
    raw_img = np.ones((120, 240)) * 0.95
    raw_img[10:13, :] = 0.2
    raw_img[60:63, :] = 0.2
    raw_img[110:113, :] = 0.2
    raw_img[:, 10:13] = 0.2
    raw_img[:, 60:63] = 0.2
    raw_img[:, 150:153] = 0.2
    raw_img[:, 230:233] = 0.2
    raw_img[28:45, 20:55] = np.random.uniform(0.1, 0.4, (17, 35))
    raw_img[32:42, 70:140] = np.random.uniform(0.1, 0.4, (10, 70))
    raw_img += np.random.normal(0, 0.03, (120, 240))
    ax.imshow(raw_img, cmap='gray', vmin=0, vmax=1)
    ax.axis('off')

    ax = axes[1]
    ax.set_title(r"(b) Horizontal Kernel Opening ($I_h$)", fontsize=10, fontweight='bold')
    h_img = np.zeros((120, 240))
    h_img[10:13, 10:233] = 1.0
    h_img[60:63, 10:233] = 1.0
    h_img[110:113, 10:233] = 1.0
    ax.imshow(h_img, cmap='gray')
    ax.axis('off')

    ax = axes[2]
    ax.set_title(r"(c) Vertical Kernel Opening ($I_v$)", fontsize=10, fontweight='bold')
    v_img = np.zeros((120, 240))
    v_img[10:113, 10:13] = 1.0
    v_img[10:113, 60:63] = 1.0
    v_img[10:113, 150:153] = 1.0
    v_img[10:113, 230:233] = 1.0
    ax.imshow(v_img, cmap='gray')
    ax.axis('off')

    ax = axes[3]
    ax.set_title("(d) Grid Intersections & Bounding Boxes", fontsize=10, fontweight='bold')
    ax.imshow(raw_img, cmap='gray', vmin=0, vmax=1)
    rect1 = patches.Rectangle((12, 14), 218, 45, fill=False, edgecolor=C_BLACK, lw=2.2, linestyle='-')
    ax.add_patch(rect1)
    ax.text(120, 38, "Row 1: VALID (Ink Density = 0.082)", ha='center', va='center', fontsize=7.5,
            color=C_BLACK, fontweight='bold', bbox=dict(boxstyle="round,pad=0.2", facecolor=C_WHITE, edgecolor=C_BLACK))

    rect2 = patches.Rectangle((12, 64), 218, 45, fill=False, edgecolor=C_GRAY_DARK, lw=2.0, linestyle='--')
    ax.add_patch(rect2)
    ax.text(120, 88, "Row 2: EXCLUDED (Ink Density < 0.015)", ha='center', va='center', fontsize=7.5,
            color=C_GRAY_DARK, fontweight='bold', bbox=dict(boxstyle="round,pad=0.2", facecolor=C_WHITE, edgecolor=C_GRAY_DARK))
    ax.axis('off')

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, "fig_5_1_grid_morphology.png")
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print("Generated B&W:", out_path)

# =============================================================================
# 7. Figure 5.2: Two-Pass CLAHE & TrOCR Pipeline (Black & White)
# =============================================================================
def generate_bw_fig_5_2():
    fig, ax = plt.subplots(figsize=(13, 6.5), dpi=300)
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 6.5)
    ax.axis('off')

    ax.text(6.5, 6.0, "Two-Pass Contrast Enhancement Flow with CLAHE & TrOCR Transformer",
            ha='center', va='center', fontsize=13, fontweight='bold', color=C_BLACK)

    blocks = [
        (1.5, 3.2, 2.2, 1.8, "Raw Cell Crop\n\n• Mobile Photo\n• Non-Uniform Lighting\n• Cursive Pen Strokes", C_WHITE, False),
        (4.5, 3.2, 2.5, 2.2, "Pass 1: CLAHE Filtering\n\n• Clip Limit = 2.5\n• Tile Grid = (8, 8)\n• Bilinear Interpolation\n• Local Normalization", C_GRAY_LIGHT, False),
        (8.0, 3.2, 2.8, 2.2, "Pass 2: TrOCR Vision Encoder\n\n• 16x16 Patch Projection\n• Positional Embeddings\n• Visual Self-Attention\n• Contrast-Aware Features", C_GRAY_MID, False),
        (11.5, 3.2, 2.2, 1.8, "Autoregressive Decoder\n\n• Cursive Transcription\n• Levenshtein Distance\n• Extracted JSON Object", C_WHITE, False)
    ]

    for x, y, w, h, text, bg, dashed in blocks:
        draw_bw_box(ax, x, y, w, h, text, fill_color=bg, dashed=dashed)

    for x_arr in [2.7, 5.85, 9.5]:
        ax.annotate("", xy=(x_arr + 0.85, 3.2), xytext=(x_arr, 3.2),
                    arrowprops=dict(arrowstyle="->", color=C_BLACK, lw=2.0))

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, "fig_5_2_clahe_trocr_flow.png")
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print("Generated B&W:", out_path)

# =============================================================================
# 8. Figure 5.3: Conflict Decision Tree (Black & White)
# =============================================================================
def generate_bw_fig_5_3():
    fig, ax = plt.subplots(figsize=(13, 9), dpi=300)
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 9)
    ax.axis('off')

    ax.text(6.5, 8.5, "Multi-Factor Timetable Discrepancy Verification Decision Flow",
            ha='center', va='center', fontsize=13, fontweight='bold', color=C_BLACK)

    draw_bw_box(ax, 6.5, 7.6, 5.0, 0.65, "Input: Extracted Arrangement Row (Date, Div, Time, Subject, Substitute)",
                fill_color=C_GRAY_LIGHT)

    checks = [
        (6.5, 6.4, "Check 1: Period Duration Span valid? (1h lecture or 2h lab)", "Invalid Period Span"),
        (6.5, 5.0, "Check 2: Division exists in Active Curriculum Master?", "Division Discrepancy"),
        (6.5, 3.6, "Check 3: Subject acronym matches semester syllabus?", "Unrecognized Course"),
        (6.5, 2.2, "Check 4: Substitute Faculty free at specified slot?", "Substitute Clashed / Booked"),
    ]

    for y_idx, (x, y, text, err_label) in enumerate(checks):
        poly = Polygon([[x, y+0.4], [x+2.8, y], [x, y-0.4], [x-2.8, y]],
                       facecolor=C_WHITE, edgecolor=C_BLACK, lw=1.6, zorder=3)
        ax.add_patch(poly)
        ax.text(x, y, text, ha='center', va='center', fontsize=8.5, fontweight='bold', color=C_BLACK, zorder=4)

        ax.annotate("", xy=(11.0, y), xytext=(x + 2.8, y),
                    arrowprops=dict(arrowstyle="->", color=C_BLACK, lw=1.6))
        ax.text(9.6, y + 0.15, "Fail (No)", fontsize=8, fontweight='bold', color=C_BLACK)
        draw_bw_box(ax, 11.8, y, 1.8, 0.55, err_label, fill_color=C_GRAY_MID)

        if y_idx < len(checks) - 1:
            ax.annotate("", xy=(x, y - 0.95), xytext=(x, y - 0.4),
                        arrowprops=dict(arrowstyle="->", color=C_BLACK, lw=1.6))
            ax.text(x + 0.2, y - 0.65, "Pass (Yes)", fontsize=8, fontweight='bold', color=C_BLACK)

    ax.annotate("", xy=(6.5, 6.8), xytext=(6.5, 7.27),
                arrowprops=dict(arrowstyle="->", color=C_BLACK, lw=1.6))

    ax.annotate("", xy=(6.5, 0.9), xytext=(6.5, 1.8),
                arrowprops=dict(arrowstyle="->", color=C_BLACK, lw=1.8))
    ax.text(6.7, 1.35, "Pass (Yes)", fontsize=8.5, fontweight='bold', color=C_BLACK)

    draw_bw_box(ax, 6.5, 0.55, 5.0, 0.65, "SUCCESS: Mark Row 'VALID' -> Ready for HOD Endorsement",
                fill_color=C_GRAY_LIGHT, lw=2.0)

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, "fig_5_3_conflict_engine_tree.png")
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print("Generated B&W:", out_path)

if __name__ == "__main__":
    generate_bw_fig_4_1()
    generate_bw_fig_4_2()
    generate_bw_fig_4_3()
    generate_bw_fig_4_4()
    generate_bw_fig_4_5()
    generate_bw_fig_5_1()
    generate_bw_fig_5_2()
    generate_bw_fig_5_3()
    print("All B&W diagrams generated successfully in", OUTPUT_DIR)
