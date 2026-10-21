"""
Script to replace all ASCII text and simple line diagrams in docs/BTECH_PROJECT_REPORT.md
with clean, real image markdown embeddings matching docs/figures/*.png.
"""

import re

MD_PATH = r"c:\Users\HP\Desktop\faculty-leave-ai\docs\BTECH_PROJECT_REPORT.md"

with open(MD_PATH, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Replace ASCII Use Case Diagram (Figure 4.1)
ascii_use_case = r'```\s*\+-\+-\+\s*\| Applicant \|[\s\S]*?```\s*\*Figure 4\.1: Comprehensive Use Case Diagram of the Faculty Leave AI Portal\.\*'
rep_use_case = """![Figure 4.1: Comprehensive Use Case Diagram of the Faculty Leave AI Portal](figures/fig_4_1_use_case.png)

*Figure 4.1: Comprehensive Use Case Diagram of the Faculty Leave AI Portal.*"""
text = re.sub(ascii_use_case, rep_use_case, text)

# 2. Replace ASCII Architecture Diagram (Figure 4.2)
ascii_arch = r'```\s*\[ CLIENT PRESENTATION LAYER \]─*[\s\S]*?```\s*\*Figure 4\.2: High-Level Layered System Architecture\.\*'
rep_arch = """![Figure 4.2: High-Level Layered System Architecture](figures/fig_4_2_system_architecture.png)

*Figure 4.2: High-Level Layered System Architecture.*"""
text = re.sub(ascii_arch, rep_arch, text)

# 3. Replace ASCII Activity Flow (Figure 4.3)
ascii_act = r'```\s*\[User Uploads JPG/PNG Form Image\][\s\S]*?```\s*\*Figure 4\.3: Document Processing Activity Flowchart\.\*'
rep_act = """![Figure 4.3: Document Processing Activity Flowchart](figures/fig_4_3_document_activity_flow.png)

*Figure 4.3: Document Processing Activity Flowchart.*"""
text = re.sub(ascii_act, rep_act, text)

# 4. Replace ASCII Sequence Diagram (Figure 4.4)
ascii_seq = r'```\s*Applicant\s+React SPA\s+FastAPI Gateway[\s\S]*?```\s*\*Figure 4\.4: UML Sequence Diagram for Form Submission, Ingestion, and Review\.\*'
rep_seq = """![Figure 4.4: UML Sequence Diagram for Form Submission, Ingestion, and Review](figures/fig_4_4_sequence_diagram.png)

*Figure 4.4: UML Sequence Diagram for Form Submission, Ingestion, and Review.*"""
text = re.sub(ascii_seq, rep_seq, text)

# 5. Replace ASCII ERD Diagram (Figure 4.5)
ascii_erd = r'```\s*\+---------------------------------\+[\s\S]*?```\s*\*Figure 4\.5: Entity-Relationship Diagram \(ERD\)\.\*'
rep_erd = """![Figure 4.5: Entity-Relationship Diagram (ERD)](figures/fig_4_5_database_erd.png)

*Figure 4.5: Entity-Relationship Diagram (ERD) with SQLAlchemy Constraints.*"""
text = re.sub(ascii_erd, rep_erd, text)

# 6. Add Real UI Screenshot Figures 4.6 - 4.11 in Section 4.7 / 4.8
ui_section_pattern = r'(## 4\.7 API Endpoints and Interface Modules[\s\S]*?)(## 4\.8 Deployment Architecture)'
def insert_ui_figures(match):
    prefix = match.group(1)
    suffix = match.group(2)
    ui_figures_md = """
### 4.7.1 User Interface Modules and Visual Interaction Flow

The frontend client is engineered as a responsive Single Page Application (SPA) leveraging React 19, TypeScript, Vite, and Tailwind CSS. The primary operational desk interfaces are illustrated below:

![Figure 4.6: Head of Department (HOD) Overview Dashboard](figures/fig_4_6_hod_dashboard.png)

*Figure 4.6: Head of Department (HOD) Overview Dashboard.*

![Figure 4.7: Master Timetable Ingestion Panel with Image-Wise Division Cards](figures/fig_4_7_timetable_panel.png)

*Figure 4.7: Master Timetable Ingestion Panel with Image-Wise Division Cards.*

![Figure 4.8: Personalized Faculty Teaching Commitment Desk (/my-schedule)](figures/fig_4_8_faculty_schedule.png)

*Figure 4.8: Personalized Faculty Teaching Commitment Desk (/my-schedule).*

![Figure 4.9: AI Vision Document Upload & 5-Step Pipeline Progress Indicator](figures/fig_4_9_upload_pipeline.png)

*Figure 4.9: AI Vision Document Upload & 5-Step Pipeline Progress Indicator.*

![Figure 4.10: Scanned Leave Review Desk Displaying Red Warning Alert Boxes](figures/fig_4_10_leave_review_red_alerts.png)

*Figure 4.10: Scanned Leave Review Desk Displaying Red Warning Alert Boxes.*

![Figure 4.11: Substitute Faculty Notification Desk and One-Click Acknowledgment](figures/fig_4_11_substitute_notification.png)

*Figure 4.11: Substitute Faculty Notification Desk and One-Click Acknowledgment.*

"""
    return prefix + ui_figures_md + suffix

text = re.sub(ui_section_pattern, insert_ui_figures, text)

# 7. Add Figure 5.1 in 5.1.1
if "fig_5_1_grid_morphology.png" not in text:
    text = text.replace(
        "### 5.1.1 Morphological Grid Detection and Mathematical Slicing",
        """### 5.1.1 Morphological Grid Detection and Mathematical Slicing

![Figure 5.1: Mathematical Morphological Grid Kernel Filtering and Cell Cropping Visualization](figures/fig_5_1_grid_morphology.png)

*Figure 5.1: Mathematical Morphological Grid Kernel Filtering and Cell Cropping Visualization.*
"""
    )

# 8. Add Figure 5.2 in 5.1.3
if "fig_5_2_clahe_trocr_flow.png" not in text:
    text = text.replace(
        "### 5.1.3 Two-Pass Vision OCR with Adaptive CLAHE",
        """### 5.1.3 Two-Pass Vision OCR with Adaptive CLAHE

![Figure 5.2: Two-Pass Contrast Enhancement Flow with CLAHE Filtering](figures/fig_5_2_clahe_trocr_flow.png)

*Figure 5.2: Two-Pass Contrast Enhancement Flow with CLAHE Filtering.*
"""
    )

# 9. Add Figure 5.3 in 5.1.4
if "fig_5_3_conflict_engine_tree.png" not in text:
    text = text.replace(
        "### 5.1.4 Multi-Factor Timetable Discrepancy Engine Formulation",
        """### 5.1.4 Multi-Factor Timetable Discrepancy Engine Formulation

![Figure 5.3: Multi-Point Conflict Verification Engine Flowchart](figures/fig_5_3_conflict_engine_tree.png)

*Figure 5.3: Multi-Point Conflict Verification Engine Flowchart.*
"""
    )

with open(MD_PATH, 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated docs/BTECH_PROJECT_REPORT.md with all 14 real diagram image links!")
