"""
Generate publication-quality diagram figures for DDU B.Tech. Project Report
using Matplotlib and Pillow. Renders at 300 DPI with professional academic styling.
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Arrow, ConnectionPatch, Polygon
import numpy as np

OUTPUT_DIR = r"c:\Users\HP\Desktop\faculty-leave-ai\docs\figures"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Theme Palette (Academic Navy / Slate / Emerald / Amber / Crimson)
C_NAVY_DARK = "#0F172A"
C_NAVY = "#1E3A8A"
C_BLUE = "#2563EB"
C_BLUE_LIGHT = "#EFF6FF"
C_SLATE = "#334155"
C_SLATE_LIGHT = "#F8FAFC"
C_BORDER = "#94A3B8"
C_GREEN = "#16A34A"
C_GREEN_BG = "#DCFCE7"
C_RED = "#DC2626"
C_RED_BG = "#FEE2E2"
C_AMBER = "#D97706"
C_AMBER_BG = "#FEF3C7"
C_PURPLE = "#7C3AED"
C_PURPLE_BG = "#F3E8FF"

def draw_actor(ax, x, y, label, scale=1.0):
    """Draws a crisp UML actor stick-figure with label."""
    # Head
    head = plt.Circle((x, y + 0.35 * scale), 0.12 * scale, color=C_NAVY, fill=False, lw=2.2)
    ax.add_patch(head)
    # Body
    ax.plot([x, x], [y + 0.23 * scale, y - 0.15 * scale], color=C_NAVY, lw=2.2)
    # Arms
    ax.plot([x - 0.22 * scale, x + 0.22 * scale], [y + 0.10 * scale, y + 0.10 * scale], color=C_NAVY, lw=2.2)
    # Legs
    ax.plot([x, x - 0.18 * scale], [y - 0.15 * scale, y - 0.45 * scale], color=C_NAVY, lw=2.2)
    ax.plot([x, x + 0.18 * scale], [y - 0.15 * scale, y - 0.45 * scale], color=C_NAVY, lw=2.2)
    # Label
    ax.text(x, y - 0.65 * scale, label, ha='center', va='top', fontsize=10.5, fontweight='bold', color=C_NAVY_DARK)

def draw_use_case(ax, x, y, text, w=2.8, h=0.7, bg_color=C_BLUE_LIGHT, border_color=C_BLUE):
    """Draws a UML Use Case Ellipse with text."""
    ellipse = patches.Ellipse((x, y), w, h, facecolor=bg_color, edgecolor=border_color, lw=1.8, zorder=3)
    ax.add_patch(ellipse)
    ax.text(x, y, text, ha='center', va='center', fontsize=9.5, fontweight='semibold', color=C_NAVY_DARK, zorder=4)

def draw_box(ax, x, y, w, h, title, subtitle="", bg=C_SLATE_LIGHT, border=C_BORDER, radius=0.08, lw=1.5):
    """Draws a rounded rectangular card."""
    box = FancyBboxPatch((x - w/2, y - h/2), w, h,
                         boxstyle=f"round,pad={radius},rounding_size={radius}",
                         facecolor=bg, edgecolor=border, lw=lw, zorder=2)
    ax.add_patch(box)
    if subtitle:
        ax.text(x, y + 0.15 * h, title, ha='center', va='center', fontsize=11, fontweight='bold', color=C_NAVY_DARK, zorder=3)
        ax.text(x, y - 0.2 * h, subtitle, ha='center', va='center', fontsize=9, color=C_SLATE, zorder=3)
    else:
        ax.text(x, y, title, ha='center', va='center', fontsize=10, fontweight='bold', color=C_NAVY_DARK, zorder=3)

# =============================================================================
# 1. Figure 4.1: UML Use Case Diagram
# =============================================================================
def generate_fig_4_1():
    fig, ax = plt.subplots(figsize=(13, 9.5), dpi=300)
    ax.set_xlim(-1, 13)
    ax.set_ylim(-1, 10.5)
    ax.axis('off')

    # System boundary box
    sys_box = FancyBboxPatch((2.2, 0.2), 7.6, 9.8, boxstyle="round,pad=0.1,rounding_size=0.15",
                            facecolor="#F8FAFC", edgecolor=C_NAVY, lw=2.2, linestyle='-')
    ax.add_patch(sys_box)
    ax.text(6.0, 9.6, "Faculty Leave AI — System Boundary", ha='center', va='center',
            fontsize=13, fontweight='bold', color=C_NAVY)

    # Actors
    draw_actor(ax, 0.8, 7.8, "Faculty Applicant", scale=0.9)
    draw_actor(ax, 0.8, 2.5, "Timetable\nAdministrator", scale=0.9)
    draw_actor(ax, 11.2, 7.8, "Head of Department\n(HOD)", scale=0.9)
    draw_actor(ax, 11.2, 2.5, "Substitute Faculty\nMember", scale=0.9)

    # Use Cases Inside Boundary (Removed <<include>> as requested)
    use_cases = [
        (6.0, 8.6, "Upload Handwritten\nLeave Slip Form", "UC1"),
        (6.0, 7.3, "Inline Error Resolution\n& Discrepancy Correction", "UC2"),
        (6.0, 6.0, "Verify Multi-Factor Timetable\nConstraints & Clashes", "UC3"),
        (6.0, 4.7, "Ingest Department\nMaster Timetable Images", "UC4"),
        (6.0, 3.4, "Query Personal Weekly\nTeaching Schedule", "UC5"),
        (6.0, 2.1, "Dispatch Personalized\nSubstitute Notifications", "UC6"),
        (6.0, 0.8, "Digital 1-Click Substitution\nAcknowledgment & HOD Signoff", "UC7"),
    ]

    for x, y, label, code in use_cases:
        bg = C_AMBER_BG if "Error" in label else C_BLUE_LIGHT
        border = C_AMBER if "Error" in label else C_BLUE
        draw_use_case(ax, x, y, label, w=3.4, h=0.85, bg_color=bg, border_color=border)

    # Associations
    for target_y in [8.6, 7.3, 3.4]:
        ax.plot([0.8, 6.0 - 1.7], [7.8, target_y], color=C_NAVY, lw=1.6, zorder=1)

    for target_y in [4.7]:
        ax.plot([0.8, 6.0 - 1.7], [2.5, target_y], color=C_NAVY, lw=1.6, zorder=1)

    for target_y in [7.3, 6.0, 0.8]:
        ax.plot([11.2, 6.0 + 1.7], [7.8, target_y], color=C_NAVY, lw=1.6, zorder=1)

    for target_y in [3.4, 2.1, 0.8]:
        ax.plot([11.2, 6.0 + 1.7], [2.5, target_y], color=C_NAVY, lw=1.6, zorder=1)
                arrowprops=dict(arrowstyle="->", color=C_BLUE, lw=1.8))
    ax.annotate("", xy=(6.0, 5.15), xytext=(6.0, 5.55),
                arrowprops=dict(arrowstyle="->", color=C_BLUE, lw=1.8))
    ax.annotate("", xy=(6.0, 2.45), xytext=(6.0, 4.25),
                arrowprops=dict(arrowstyle="->", color=C_BLUE, lw=1.8))
    ax.annotate("", xy=(6.0, 1.25), xytext=(6.0, 1.55),
                arrowprops=dict(arrowstyle="->", color=C_BLUE, lw=1.8))

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, "fig_4_1_use_case.png")
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print("Generated:", out_path)

# =============================================================================
# 2. Figure 4.2: High-Level Layered System Architecture
# =============================================================================
def generate_fig_4_2():
    fig, ax = plt.subplots(figsize=(14, 10), dpi=300)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 11)
    ax.axis('off')

    # Title
    ax.text(7.0, 10.6, "Faculty Leave AI — High-Level Layered Architecture",
            ha='center', va='center', fontsize=14, fontweight='bold', color=C_NAVY)

    # 4 Layers
    layers = [
        ("Layer 1: Client Presentation Tier (SPA)", 8.8, 1.6, C_BLUE_LIGHT, C_BLUE, [
            ("HOD Executive\nDashboard", 2.3),
            ("Timetable Preset\n& Ingestion Desk", 4.7),
            ("Document Upload\n& Progress Stepper", 7.1),
            ("Scanned Leave Review\n& Error Desk", 9.5),
            ("Substitute Notification\n& Acknowledgment Desk", 11.9)
        ]),
        ("Layer 2: REST API Gateway & Application Controller", 6.5, 1.4, C_PURPLE_BG, C_PURPLE, [
            ("FastAPI ASGI Server\n(Port 8000)", 2.8),
            ("Pydantic v2 Schema Validation\n& CORS Middleware", 7.0),
            ("Role-Based Session Security\n& Error Handlers", 11.2)
        ]),
        ("Layer 3: Core AI Processing & Analytical Engine", 3.8, 2.0, C_AMBER_BG, C_AMBER, [
            ("OpenCV Morphological\nGrid & Deskew Slicer", 2.5),
            ("Microsoft TrOCR Base\nCursive Transformer HTR", 5.5),
            ("Multi-Factor Timetable\nVerification Engine", 8.5),
            ("Notification Dispatcher\n& State Broker", 11.5)
        ]),
        ("Layer 4: Data Persistence & Physical Storage Tier", 1.2, 1.4, C_GREEN_BG, C_GREEN, [
            ("SQLite 3.45+ (WAL Mode)\nRelational Database", 3.5),
            ("SQLAlchemy 2.0 ORM\nData Models", 7.0),
            ("Local File Storage\n(Raw & Crop Images)", 10.5)
        ]),
    ]

    for title, y_c, h, bg, border, boxes in layers:
        # Layer backdrop
        layer_box = FancyBboxPatch((0.6, y_c - h/2), 12.8, h, boxstyle="round,pad=0.08,rounding_size=0.12",
                                   facecolor=bg, edgecolor=border, lw=2.0)
        ax.add_patch(layer_box)
        ax.text(1.0, y_c + h/2 - 0.22, title, fontsize=11, fontweight='bold', color=border)

        # Internal components
        for box_title, x_pos in boxes:
            bw = 2.1 if len(boxes) >= 4 else 3.2
            bh = h * 0.58
            by = y_c - 0.08
            box = FancyBboxPatch((x_pos - bw/2, by - bh/2), bw, bh,
                                 boxstyle="round,pad=0.05,rounding_size=0.08",
                                 facecolor="#FFFFFF", edgecolor=border, lw=1.4)
            ax.add_patch(box)
            ax.text(x_pos, by, box_title, ha='center', va='center', fontsize=9, fontweight='semibold', color=C_NAVY_DARK)

    # Inter-layer connector arrows
    for y_arrow in [7.7, 5.4, 2.5]:
        ax.annotate("", xy=(7.0, y_arrow - 0.3), xytext=(7.0, y_arrow + 0.3),
                    arrowprops=dict(arrowstyle="<->", color=C_SLATE, lw=2.2))
        ax.annotate("", xy=(3.5, y_arrow - 0.3), xytext=(3.5, y_arrow + 0.3),
                    arrowprops=dict(arrowstyle="<->", color=C_SLATE, lw=2.2))
        ax.annotate("", xy=(10.5, y_arrow - 0.3), xytext=(10.5, y_arrow + 0.3),
                    arrowprops=dict(arrowstyle="<->", color=C_SLATE, lw=2.2))

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, "fig_4_2_system_architecture.png")
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print("Generated:", out_path)

# =============================================================================
# 3. Figure 4.3: Document Processing Activity Flowchart
# =============================================================================
def generate_fig_4_3():
    fig, ax = plt.subplots(figsize=(11, 13), dpi=300)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 13)
    ax.axis('off')

    ax.text(5.5, 12.6, "Document Processing & Ingestion Pipeline Activity Flow",
            ha='center', va='center', fontsize=13, fontweight='bold', color=C_NAVY)

    # Nodes definition: (x, y, type, text)
    # Start
    start_c = plt.Circle((5.5, 12.0), 0.22, color=C_GREEN, zorder=4)
    ax.add_patch(start_c)
    ax.text(5.5, 12.0, "Start", ha='center', va='center', fontsize=8, color="#FFFFFF", fontweight='bold', zorder=5)

    steps = [
        (5.5, 11.0, "box", "1. Ingest Scanned / Captured Leave Slip Image\n(JPEG / PNG Format)"),
        (5.5, 9.9, "box", "2. Image Preprocessing & Orientation Normalization\n(Grayscale, Bilateral Filter, Deskew via Radon Transform)"),
        (5.5, 8.8, "box", "3. Morphological Grid Extraction\n(Horizontal & Vertical Kernels: Kh & Kv)"),
        (5.5, 7.7, "box", "4. Find Table Grid Contours & Extract Row RoIs"),
        (5.5, 6.4, "diamond", "Ink Ratio > 0.015?\n(Blank Row Check)"),
        (2.4, 6.4, "box_red", "Discard Blank Row\n(Skip Transcription)"),
        (5.5, 5.0, "box", "5. CLAHE Contrast Normalization &\nTile-Based Histogram Equalization"),
        (5.5, 3.9, "box", "6. Microsoft TrOCR Transformer OCR\n(Extract Division, Date, Time, Course, Room, Substitute)"),
        (5.5, 2.7, "diamond", "Cross-Reference Timetable:\nAny Discrepancies?"),
        (2.4, 2.7, "box_amber", "Display Red Warning Alerts &\nProvide Inline Editable Fields"),
        (5.5, 1.4, "box_green", "Mark Status: 'VALID' (Green Badges) &\nDispatch Substitute Notifications"),
    ]

    for x, y, ntype, text in steps:
        if ntype == "box":
            draw_box(ax, x, y, 4.8, 0.75, text, bg=C_BLUE_LIGHT, border=C_BLUE)
        elif ntype == "box_red":
            draw_box(ax, x, y, 2.4, 0.7, text, bg=C_RED_BG, border=C_RED)
        elif ntype == "box_amber":
            draw_box(ax, x, y, 3.0, 0.75, text, bg=C_AMBER_BG, border=C_AMBER)
        elif ntype == "box_green":
            draw_box(ax, x, y, 4.8, 0.75, text, bg=C_GREEN_BG, border=C_GREEN)
        elif ntype == "diamond":
            poly = Polygon([[x, y+0.5], [x+1.5, y], [x, y-0.5], [x-1.5, y]],
                           facecolor=C_PURPLE_BG, edgecolor=C_PURPLE, lw=1.8, zorder=3)
            ax.add_patch(poly)
            ax.text(x, y, text, ha='center', va='center', fontsize=8.5, fontweight='bold', color=C_NAVY_DARK, zorder=4)

    # End
    end_c1 = plt.Circle((5.5, 0.4), 0.24, color=C_NAVY, fill=False, lw=2.2, zorder=4)
    end_c2 = plt.Circle((5.5, 0.4), 0.16, color=C_NAVY, zorder=4)
    ax.add_patch(end_c1)
    ax.add_patch(end_c2)
    ax.text(5.5, 0.05, "End", ha='center', va='center', fontsize=9, fontweight='bold', color=C_NAVY_DARK)

    # Connections
    conns = [
        ((5.5, 11.78), (5.5, 11.4)),
        ((5.5, 10.6), (5.5, 10.3)),
        ((5.5, 9.5), (5.5, 9.2)),
        ((5.5, 8.4), (5.5, 8.1)),
        ((5.5, 7.3), (5.5, 6.9)),
        ((5.5, 5.9), (5.5, 5.4)),   # Yes from diamond 1
        ((5.5, 4.6), (5.5, 4.3)),
        ((5.5, 3.5), (5.5, 3.2)),
        ((5.5, 2.2), (5.5, 1.8)),   # No from diamond 2
        ((5.5, 1.0), (5.5, 0.65)),
    ]
    for start, end in conns:
        ax.annotate("", xy=end, xytext=start, arrowprops=dict(arrowstyle="->", color=C_SLATE, lw=1.8))

    # Diamond 1 - No branch (to discard)
    ax.annotate("", xy=(3.6, 6.4), xytext=(4.0, 6.4), arrowprops=dict(arrowstyle="->", color=C_RED, lw=1.8))
    ax.text(3.8, 6.55, "No", fontsize=8.5, fontweight='bold', color=C_RED)

    # Diamond 1 - Yes label
    ax.text(5.65, 5.65, "Yes", fontsize=8.5, fontweight='bold', color=C_GREEN)

    # Diamond 2 - Yes branch (to warnings)
    ax.annotate("", xy=(3.9, 2.7), xytext=(4.0, 2.7), arrowprops=dict(arrowstyle="->", color=C_AMBER, lw=1.8))
    ax.text(3.7, 2.85, "Yes (Clash)", fontsize=8.5, fontweight='bold', color=C_AMBER)

    # From Amber box down to Green box once resolved
    ax.annotate("", xy=(4.0, 1.6), xytext=(2.4, 2.3),
                arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=-0.2", color=C_GREEN, lw=1.8))
    ax.text(2.6, 1.7, "Inline Corrected", fontsize=8, fontweight='bold', color=C_GREEN)

    # Diamond 2 - No label
    ax.text(5.65, 2.0, "No (Valid)", fontsize=8.5, fontweight='bold', color=C_GREEN)

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, "fig_4_3_document_activity_flow.png")
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print("Generated:", out_path)

# =============================================================================
# 4. Figure 4.4: UML Sequence Diagram
# =============================================================================
def generate_fig_4_4():
    fig, ax = plt.subplots(figsize=(14, 10.5), dpi=300)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 11)
    ax.axis('off')

    ax.text(7.0, 10.6, "UML Sequence Diagram: End-to-End Leave Ingestion & Verification",
            ha='center', va='center', fontsize=13.5, fontweight='bold', color=C_NAVY)

    # Lifelines
    lifelines = [
        ("Faculty\nApplicant", 1.2),
        ("React UI\n(Frontend)", 3.4),
        ("FastAPI\nController", 5.6),
        ("TrOCR Vision\nWorker", 7.8),
        ("Timetable Verification\nEngine", 10.0),
        ("Substitute\nFaculty", 12.2)
    ]

    for label, x in lifelines:
        draw_box(ax, x, 9.8, 1.8, 0.7, label, bg=C_BLUE_LIGHT, border=C_BLUE)
        ax.plot([x, x], [0.5, 9.45], color=C_BORDER, linestyle="--", lw=1.4, zorder=1)

    # Messages definition: (y, x_from, x_to, text, return_line)
    messages = [
        (9.0, 1.2, 3.4, "1. Upload leave form image", False),
        (8.4, 3.4, 5.6, "2. POST /api/forms/upload (multipart)", False),
        (7.8, 5.6, 7.8, "3. segment_grid_and_extract_rows(image)", False),
        (7.2, 7.8, 7.8, "4. trocr_infer_tokens() [CLAHE]", False),
        (6.6, 7.8, 5.6, "5. return extracted_rows[]", True),
        (6.0, 5.6, 10.0, "6. check_conflicts(extracted_rows)", False),
        (5.4, 10.0, 10.0, "7. verify curriculum & slot collisions", False),
        (4.8, 10.0, 5.6, "8. return conflict_warnings[]", True),
        (4.2, 5.6, 3.4, "9. 200 OK: payload with warning flags", True),
        (3.6, 3.4, 1.2, "10. Render review desk (red alert cards)", True),
        (3.0, 1.2, 3.4, "11. Save inline correction", False),
        (2.4, 3.4, 5.6, "12. PUT /api/forms/{id}/rows (update)", False),
        (1.8, 5.6, 12.2, "13. Dispatch substitution email notification", False),
        (1.2, 12.2, 5.6, "14. Click 1-Click Acknowledge link", False),
        (0.6, 5.6, 3.4, "15. SSE update: status='CONFIRMED'", True),
    ]

    for y, x1, x2, text, is_ret in messages:
        ls = "--" if is_ret else "-"
        col = C_GREEN if "Acknowledge" in text or "CONFIRMED" in text else (C_AMBER if "warning" in text or "red" in text else C_NAVY)
        
        # Self call
        if x1 == x2:
            loop_x = [x1, x1 + 0.6, x1 + 0.6, x1]
            loop_y = [y + 0.15, y + 0.15, y - 0.15, y - 0.15]
            ax.plot(loop_x, loop_y, color=col, lw=1.6)
            ax.annotate("", xy=(x1, y - 0.15), xytext=(x1 + 0.2, y - 0.15),
                        arrowprops=dict(arrowstyle="->", color=col, lw=1.6))
            ax.text(x1 + 0.7, y, text, ha='left', va='center', fontsize=8.5, color=col, fontweight='semibold')
        else:
            ax.annotate("", xy=(x2, y), xytext=(x1, y),
                        arrowprops=dict(arrowstyle="->", linestyle=ls, color=col, lw=1.6))
            mid_x = (x1 + x2) / 2
            ax.text(mid_x, y + 0.14, text, ha='center', va='bottom', fontsize=8.5, color=col, fontweight='semibold')

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, "fig_4_4_sequence_diagram.png")
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print("Generated:", out_path)

# =============================================================================
# 5. Figure 4.5: Entity-Relationship Diagram (ERD)
# =============================================================================
def generate_fig_4_5():
    fig, ax = plt.subplots(figsize=(14, 10.5), dpi=300)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 11)
    ax.axis('off')

    ax.text(7.0, 10.6, "Relational Database Schema & Entity-Relationship Diagram (SQLite / SQLAlchemy)",
            ha='center', va='center', fontsize=13.5, fontweight='bold', color=C_NAVY)

    def draw_entity(x, y, w, h, table_name, columns):
        # Header
        hdr_h = 0.55
        hdr = FancyBboxPatch((x - w/2, y + h/2 - hdr_h), w, hdr_h,
                             boxstyle="round,pad=0.04,rounding_size=0.08",
                             facecolor=C_NAVY, edgecolor=C_NAVY, lw=1.5, zorder=3)
        ax.add_patch(hdr)
        ax.text(x, y + h/2 - hdr_h/2, table_name, ha='center', va='center',
                fontsize=10.5, fontweight='bold', color="#FFFFFF", zorder=4)

        # Body
        body = FancyBboxPatch((x - w/2, y - h/2), w, h - hdr_h,
                              boxstyle="round,pad=0.04,rounding_size=0.08",
                              facecolor="#FFFFFF", edgecolor=C_BORDER, lw=1.5, zorder=2)
        ax.add_patch(body)

        # Columns
        col_y = y + h/2 - hdr_h - 0.25
        for col_def in columns:
            is_pk = "PK" in col_def
            is_fk = "FK" in col_def
            col_color = C_PURPLE if is_pk else (C_AMBER if is_fk else C_SLATE)
            font_wt = 'bold' if (is_pk or is_fk) else 'normal'
            ax.text(x - w/2 + 0.15, col_y, col_def, ha='left', va='center',
                    fontsize=8.5, color=col_color, fontweight=font_wt, zorder=3)
            col_y -= 0.28

    # Tables
    # 1. leave_forms
    draw_entity(3.0, 7.8, 4.4, 3.4, "leave_forms", [
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

    # 2. leave_arrangements
    draw_entity(3.0, 2.8, 4.8, 4.2, "leave_arrangements", [
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

    # 3. timetable_entries
    draw_entity(10.5, 7.8, 4.8, 3.8, "timetable_entries", [
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

    # 4. faculty_profiles
    draw_entity(10.5, 3.2, 4.4, 3.2, "faculty_profiles", [
        "id: INTEGER [PK, AUTOINCREMENT]",
        "faculty_code: VARCHAR(20) [UNIQUE]",
        "full_name: VARCHAR(100)",
        "email: VARCHAR(100) [UNIQUE]",
        "phone: VARCHAR(20)",
        "department: VARCHAR(50)",
        "designation: VARCHAR(50)",
        "is_active: BOOLEAN"
    ])

    # Relationships Lines & Cardinality Notation
    # leave_forms (1) to leave_arrangements (N)
    ax.plot([3.0, 3.0], [6.1, 4.9], color=C_NAVY, lw=2.0)
    ax.text(3.15, 5.85, "1", fontsize=10, fontweight='bold', color=C_NAVY)
    ax.text(3.15, 5.15, "N", fontsize=10, fontweight='bold', color=C_NAVY)

    # leave_arrangements (N) to faculty_profiles (1)
    ax.plot([5.4, 8.3], [2.8, 3.2], color=C_NAVY, lw=2.0)
    ax.text(5.6, 2.95, "N", fontsize=10, fontweight='bold', color=C_NAVY)
    ax.text(8.0, 3.35, "1", fontsize=10, fontweight='bold', color=C_NAVY)

    # timetable_entries to faculty_profiles
    ax.plot([10.5, 10.5], [5.9, 4.8], color=C_NAVY, lw=2.0)
    ax.text(10.65, 5.7, "N", fontsize=10, fontweight='bold', color=C_NAVY)
    ax.text(10.65, 5.0, "1", fontsize=10, fontweight='bold', color=C_NAVY)

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, "fig_4_5_database_erd.png")
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print("Generated:", out_path)

# =============================================================================
# 6. Figure 5.1: Morphological Grid Kernel Filtering Visualization
# =============================================================================
def generate_fig_5_1():
    fig, axes = plt.subplots(1, 4, figsize=(15, 4.5), dpi=300)
    fig.suptitle("Mathematical Morphological Grid Kernel Filtering & Row Bounding-Box Slicing",
                 fontsize=13, fontweight='bold', color=C_NAVY, y=1.02)

    # 1. Raw Simulated Form Crop
    ax = axes[0]
    ax.set_title("(a) Raw Photographed Crop", fontsize=10, fontweight='bold')
    raw_img = np.ones((120, 240)) * 0.95
    # draw grid lines
    raw_img[10:13, :] = 0.2
    raw_img[60:63, :] = 0.2
    raw_img[110:113, :] = 0.2
    raw_img[:, 10:13] = 0.2
    raw_img[:, 60:63] = 0.2
    raw_img[:, 150:153] = 0.2
    raw_img[:, 230:233] = 0.2
    # draw handwriting in row 1
    raw_img[28:45, 20:55] = np.random.uniform(0.1, 0.4, (17, 35))
    raw_img[32:42, 70:140] = np.random.uniform(0.1, 0.4, (10, 70))
    # noise
    raw_img += np.random.normal(0, 0.03, (120, 240))
    ax.imshow(raw_img, cmap='gray', vmin=0, vmax=1)
    ax.axis('off')

    # 2. Horizontal Kernel Opening
    ax = axes[1]
    ax.set_title("(b) Horizontal Kernel Opening\n$I_{horiz} = (I \ominus K_h) \oplus K_h$", fontsize=10, fontweight='bold')
    h_img = np.zeros((120, 240))
    h_img[10:13, 10:233] = 1.0
    h_img[60:63, 10:233] = 1.0
    h_img[110:113, 10:233] = 1.0
    ax.imshow(h_img, cmap='hot')
    ax.axis('off')

    # 3. Vertical Kernel Opening
    ax = axes[2]
    ax.set_title("(c) Vertical Kernel Opening\n$I_{vert} = (I \ominus K_v) \oplus K_v$", fontsize=10, fontweight='bold')
    v_img = np.zeros((120, 240))
    v_img[10:113, 10:13] = 1.0
    v_img[10:113, 60:63] = 1.0
    v_img[10:113, 150:153] = 1.0
    v_img[10:113, 230:233] = 1.0
    ax.imshow(v_img, cmap='hot')
    ax.axis('off')

    # 4. Grid Mask & Extracted Bounding Box
    ax = axes[3]
    ax.set_title("(d) Grid Intersections &\nRow Cell Segmentation", fontsize=10, fontweight='bold')
    ax.imshow(raw_img, cmap='gray', vmin=0, vmax=1)
    # Draw green bounding box around valid row 1
    rect1 = patches.Rectangle((12, 14), 218, 45, fill=False, edgecolor=C_GREEN, lw=2.2, linestyle='-')
    ax.add_patch(rect1)
    ax.text(120, 38, "Row 1: VALID (Ink Density = 0.082)", ha='center', va='center', fontsize=7.5,
            color=C_GREEN, fontweight='bold', bbox=dict(boxstyle="round,pad=0.2", facecolor=C_GREEN_BG, edgecolor=C_GREEN))

    # Draw red dashed box around blank row 2
    rect2 = patches.Rectangle((12, 64), 218, 45, fill=False, edgecolor=C_RED, lw=2.0, linestyle='--')
    ax.add_patch(rect2)
    ax.text(120, 88, "Row 2: EXCLUDED (Ink Density < 0.015)", ha='center', va='center', fontsize=7.5,
            color=C_RED, fontweight='bold', bbox=dict(boxstyle="round,pad=0.2", facecolor=C_RED_BG, edgecolor=C_RED))
    ax.axis('off')

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, "fig_5_1_grid_morphology.png")
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print("Generated:", out_path)

# =============================================================================
# 7. Figure 5.2: Two-Pass CLAHE Contrast Flow
# =============================================================================
def generate_fig_5_2():
    fig, ax = plt.subplots(figsize=(13, 6.5), dpi=300)
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 6.5)
    ax.axis('off')

    ax.text(6.5, 6.0, "Two-Pass Contrast Enhancement Flow with CLAHE & TrOCR Transformer",
            ha='center', va='center', fontsize=13, fontweight='bold', color=C_NAVY)

    blocks = [
        (1.5, 3.2, 2.2, 1.8, "Raw Cell Crop\n\n• Ambient Shadow\n• Low Contrast\n• Variable Ink", C_SLATE_LIGHT, C_BORDER),
        (4.5, 3.2, 2.5, 2.2, "Pass 1: CLAHE Filtering\n\n• Clip Limit = 2.5\n• Tile Grid = (8, 8)\n• Bilinear Interpolation\n• Local Equalization", C_BLUE_LIGHT, C_BLUE),
        (8.0, 3.2, 2.8, 2.2, "Pass 2: TrOCR Vision Encoder\n\n• 16x16 Patch Projection\n• Positional Embeddings\n• Visual Self-Attention\n• Contrast-Aware Features", C_PURPLE_BG, C_PURPLE),
        (11.5, 3.2, 2.2, 1.8, "Autoregressive Decoder\n\n• Cursive Transcription\n• Levenshtein Distance\n• Clean JSON Object", C_GREEN_BG, C_GREEN)
    ]

    for x, y, w, h, text, bg, border in blocks:
        draw_box(ax, x, y, w, h, text, bg=bg, border=border)

    for x_arr in [2.7, 5.85, 9.5]:
        ax.annotate("", xy=(x_arr + 0.85, 3.2), xytext=(x_arr, 3.2),
                    arrowprops=dict(arrowstyle="->", color=C_NAVY, lw=2.2))

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, "fig_5_2_clahe_trocr_flow.png")
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print("Generated:", out_path)

# =============================================================================
# 8. Figure 5.3: Multi-Point Conflict Verification Engine Flowchart
# =============================================================================
def generate_fig_5_3():
    fig, ax = plt.subplots(figsize=(13, 9), dpi=300)
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 9)
    ax.axis('off')

    ax.text(6.5, 8.5, "Multi-Factor Timetable Discrepancy Verification Decision Flow",
            ha='center', va='center', fontsize=13, fontweight='bold', color=C_NAVY)

    # Input Box
    draw_box(ax, 6.5, 7.6, 5.0, 0.65, "Input: Extracted Arrangement Row (Date, Div, Time, Subject, Substitute)",
             bg=C_BLUE_LIGHT, border=C_BLUE)

    checks = [
        (6.5, 6.4, "Check 1: Period Duration Span valid? (1h lecture or 2h lab)", "Invalid Period Span"),
        (6.5, 5.0, "Check 2: Division exists in Active Curriculum Master?", "Division Discrepancy"),
        (6.5, 3.6, "Check 3: Subject acronym matches semester syllabus?", "Unrecognized Course"),
        (6.5, 2.2, "Check 4: Substitute Faculty free at specified slot?", "Substitute Clashed / Double-Booked"),
    ]

    for y_idx, (x, y, text, err_label) in enumerate(checks):
        poly = Polygon([[x, y+0.4], [x+2.8, y], [x, y-0.4], [x-2.8, y]],
                       facecolor=C_PURPLE_BG, edgecolor=C_PURPLE, lw=1.6, zorder=3)
        ax.add_patch(poly)
        ax.text(x, y, text, ha='center', va='center', fontsize=8.5, fontweight='bold', color=C_NAVY_DARK, zorder=4)

        # Failure red branch to right
        ax.annotate("", xy=(11.0, y), xytext=(x + 2.8, y),
                    arrowprops=dict(arrowstyle="->", color=C_RED, lw=1.6))
        ax.text(9.6, y + 0.15, "Fail (No)", fontsize=8, fontweight='bold', color=C_RED)
        draw_box(ax, 11.8, y, 1.8, 0.55, err_label, bg=C_RED_BG, border=C_RED)

        # Down arrow (Pass)
        if y_idx < len(checks) - 1:
            ax.annotate("", xy=(x, y - 0.95), xytext=(x, y - 0.4),
                        arrowprops=dict(arrowstyle="->", color=C_GREEN, lw=1.6))
            ax.text(x + 0.2, y - 0.65, "Pass (Yes)", fontsize=8, fontweight='bold', color=C_GREEN)

    # Connect input to Check 1
    ax.annotate("", xy=(6.5, 6.8), xytext=(6.5, 7.27),
                arrowprops=dict(arrowstyle="->", color=C_NAVY, lw=1.6))

    # Pass from Check 4 to Final Success Box
    ax.annotate("", xy=(6.5, 0.9), xytext=(6.5, 1.8),
                arrowprops=dict(arrowstyle="->", color=C_GREEN, lw=1.8))
    ax.text(6.7, 1.35, "Pass (Yes)", fontsize=8.5, fontweight='bold', color=C_GREEN)

    draw_box(ax, 6.5, 0.55, 5.0, 0.65, "SUCCESS: Mark Row 'VALID' (Green Badge) -> Ready for HOD Endorsement",
             bg=C_GREEN_BG, border=C_GREEN)

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, "fig_5_3_conflict_engine_tree.png")
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print("Generated:", out_path)

if __name__ == "__main__":
    generate_fig_4_1()
    generate_fig_4_2()
    generate_fig_4_3()
    generate_fig_4_4()
    generate_fig_4_5()
    generate_fig_5_1()
    generate_fig_5_2()
    generate_fig_5_3()
    print("All 8 diagram figures generated successfully in", OUTPUT_DIR)
