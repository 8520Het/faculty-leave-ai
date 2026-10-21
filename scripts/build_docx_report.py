"""
Build official Dharmsinh Desai University (DDU) B.Tech. Project-II Report
strictly following the format, indentations, fonts, layout of the official docx
template and sample PDF, embedding all 14 publication-grade diagrams and UI screenshots.
"""

import os
import re
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls

FIGURES_DIR = r"c:\Users\HP\Desktop\faculty-leave-ai\docs\figures"
DOCX_OUT = r"c:\Users\HP\Desktop\faculty-leave-ai\docs\BTECH_PROJECT_REPORT_DDU.docx"

FIGURE_MAP = {
    "Figure 4.1": ("fig_4_1_use_case.png", "Figure 4.1: Comprehensive Use Case Diagram of the Faculty Leave AI Portal"),
    "Figure 4.2": ("fig_4_2_system_architecture.png", "Figure 4.2: High-Level Layered System Architecture"),
    "Figure 4.3": ("fig_4_3_document_activity_flow.png", "Figure 4.3: Document Processing Activity Flowchart"),
    "Figure 4.4": ("fig_4_4_sequence_diagram.png", "Figure 4.4: UML Sequence Diagram for Form Submission, Ingestion, and Review"),
    "Figure 4.5": ("fig_4_5_database_erd.png", "Figure 4.5: Entity-Relationship Diagram (ERD) with SQLAlchemy Constraints"),
    "Figure 4.6": ("fig_4_6_hod_dashboard.png", "Figure 4.6: Head of Department (HOD) Overview Dashboard"),
    "Figure 4.7": ("fig_4_7_timetable_panel.png", "Figure 4.7: Master Timetable Ingestion Panel with Image-Wise Division Cards"),
    "Figure 4.8": ("fig_4_8_faculty_schedule.png", "Figure 4.8: Personalized Faculty Teaching Commitment Desk (/my-schedule)"),
    "Figure 4.9": ("fig_4_9_upload_pipeline.png", "Figure 4.9: AI Vision Document Upload & 5-Step Pipeline Progress Indicator"),
    "Figure 4.10": ("fig_4_10_leave_review_red_alerts.png", "Figure 4.10: Scanned Leave Review Desk Displaying Red Warning Alert Boxes"),
    "Figure 4.11": ("fig_4_11_substitute_notification.png", "Figure 4.11: Substitute Faculty Notification Desk and One-Click Acknowledgment"),
    "Figure 5.1": ("fig_5_1_grid_morphology.png", "Figure 5.1: Mathematical Morphological Grid Kernel Filtering and Cell Cropping Visualization"),
    "Figure 5.2": ("fig_5_2_clahe_trocr_flow.png", "Figure 5.2: Two-Pass Contrast Enhancement Flow with CLAHE Filtering"),
    "Figure 5.3": ("fig_5_3_conflict_engine_tree.png", "Figure 5.3: Multi-Point Conflict Verification Engine Flowchart"),
}

def set_cell_background(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=120, bottom=120, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)

def set_table_borders(table, color="B0BEC5", sz="4", val="single"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideV w:val="none"/>'
        f'<w:left w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

def remove_table_borders(table):
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="none"/>'
        f'<w:bottom w:val="none"/>'
        f'<w:insideH w:val="none"/>'
        f'<w:insideV w:val="none"/>'
        f'<w:left w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

def add_formatted_runs(p, text, base_font_size=12, is_bold_base=False, is_italic_base=False, color_rgb=(40,40,40)):
    token_pattern = re.compile(r'(\*\*.*?\*\*|\*.*?\*|`.*?`)')
    parts = token_pattern.split(text)
    
    for part in parts:
        if not part:
            continue
        run = p.add_run()
        run.font.name = 'Times New Roman'
        run.font.size = Pt(base_font_size)
        run.font.color.rgb = RGBColor(*color_rgb)
        run.bold = is_bold_base
        run.italic = is_italic_base
        
        if part.startswith('**') and part.endswith('**') and len(part) >= 4:
            run.text = part[2:-2]
            run.bold = True
        elif part.startswith('*') and part.endswith('*') and len(part) >= 2:
            run.text = part[1:-1]
            run.italic = True
        elif part.startswith('`') and part.endswith('`') and len(part) >= 2:
            run.text = part[1:-1]
            run.font.name = 'Consolas'
            run.font.size = Pt(base_font_size - 1.5)
            run.font.color.rgb = RGBColor(160, 30, 30)
        else:
            run.text = part

def build_report():
    doc = docx.Document()

    # Section & Page Setup (Letter: 8.5 x 11.0 in, Left Margin 1.5 in as per DDU thesis specs)
    for section in doc.sections:
        section.page_width = Inches(8.5)
        section.page_height = Inches(11.0)
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.5)   # 1.5 inch binding margin strictly as in template
        section.right_margin = Inches(1.0)

        # Header Setup
        header = section.header
        hp = header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hrun = hp.add_run("Department of Information Technology, Dharmsinh Desai University | Faculty Leave AI")
        hrun.font.name = "Times New Roman"
        hrun.font.size = Pt(8.5)
        hrun.italic = True
        hrun.font.color.rgb = RGBColor(128, 128, 128)

    # Styles Setup
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Times New Roman'
    normal_style.font.size = Pt(12)
    normal_style.font.color.rgb = RGBColor(40, 40, 40)

    # Read Markdown Source
    md_path = r"c:\Users\HP\Desktop\faculty-leave-ai\docs\BTECH_PROJECT_REPORT.md"
    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    lines = md_text.splitlines()
    total_lines = len(lines)
    idx = 0

    in_code_block = False
    code_lines = []
    in_table = False
    table_lines = []

    def flush_table():
        nonlocal table_lines
        if not table_lines:
            return
        
        rows = []
        for line in table_lines:
            line_str = line.strip()
            if not line_str.startswith('|'):
                continue
            cells = [c.strip() for c in line_str.split('|')[1:-1]]
            if all(re.match(r'^:?-+:?$', c) for c in cells):
                continue
            rows.append(cells)
            
        if rows:
            num_cols = max(len(r) for r in rows)
            tbl = doc.add_table(rows=len(rows), cols=num_cols)
            tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
            set_table_borders(tbl, color="B0BEC5", sz="4")
            
            for row_idx, row_data in enumerate(rows):
                is_header = (row_idx == 0)
                row_elem = tbl.rows[row_idx]
                
                trPr = row_elem._tr.get_or_add_trPr()
                trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
                if is_header:
                    trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))
                
                for col_idx in range(num_cols):
                    cell_text = row_data[col_idx] if col_idx < len(row_data) else ""
                    cell = row_elem.cells[col_idx]
                    cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
                    set_cell_margins(cell, top=140, bottom=140, left=160, right=160)
                    
                    if is_header:
                        set_cell_background(cell, "1A365D")
                    elif row_idx % 2 == 1:
                        set_cell_background(cell, "F8FAFC")
                    else:
                        set_cell_background(cell, "FFFFFF")
                        
                    p = cell.paragraphs[0]
                    p.paragraph_format.space_before = Pt(2)
                    p.paragraph_format.space_after = Pt(2)
                    p.paragraph_format.line_spacing = 1.15
                    
                    if is_header:
                        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                        add_formatted_runs(p, cell_text, base_font_size=10.5, is_bold_base=True, color_rgb=(255, 255, 255))
                    else:
                        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                        add_formatted_runs(p, cell_text, base_font_size=9.5, is_bold_base=False, color_rgb=(40, 40, 40))
                        
            p_after = doc.add_paragraph()
            p_after.paragraph_format.space_before = Pt(2)
            p_after.paragraph_format.space_after = Pt(6)
            
        table_lines = []

    def flush_code():
        nonlocal code_lines
        if not code_lines:
            return
        code_text = "\n".join(code_lines)
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.4)
        p.paragraph_format.right_indent = Inches(0.4)
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(8)
        p.paragraph_format.line_spacing = 1.05
        
        pPr = p._p.get_or_add_pPr()
        pBdr = parse_xml(
            f'<w:pBdr {nsdecls("w")}>'
            f'<w:left w:val="single" w:sz="18" w:space="10" w:color="1A365D"/>'
            f'</w:pBdr>'
        )
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="EDF2F7"/>')
        pPr.append(pBdr)
        pPr.append(shd)
        
        run = p.add_run(code_text)
        run.font.name = 'Consolas'
        run.font.size = Pt(9.0)
        run.font.color.rgb = RGBColor(45, 55, 72)
        code_lines = []

    def insert_image_and_caption(fig_key):
        filename, caption_text = FIGURE_MAP[fig_key]
        img_path = os.path.join(FIGURES_DIR, filename)
        if os.path.exists(img_path):
            p_img = doc.add_paragraph()
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img.paragraph_format.space_before = Pt(10)
            p_img.paragraph_format.space_after = Pt(3)
            run = p_img.add_run()
            # Scale image width to fit nicely (5.6 inches)
            run.add_picture(img_path, width=Inches(5.6))

            p_cap = doc.add_paragraph()
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_cap.paragraph_format.space_before = Pt(2)
            p_cap.paragraph_format.space_after = Pt(10)
            p_cap.paragraph_format.keep_with_next = True
            r_cap = p_cap.add_run(caption_text)
            r_cap.font.name = "Times New Roman"
            r_cap.font.size = Pt(10)
            r_cap.italic = True
            r_cap.font.color.rgb = RGBColor(60, 60, 60)
            return True
        return False

    inserted_figures = set()

    while idx < total_lines:
        line = lines[idx]
        stripped = line.strip()

        # Handle Code Fences
        if stripped.startswith("```"):
            if in_code_block:
                in_code_block = False
                flush_code()
            else:
                if in_table:
                    in_table = False
                    flush_table()
                in_code_block = True
                code_lines = []
            idx += 1
            continue

        if in_code_block:
            code_lines.append(line)
            idx += 1
            continue

        # Handle Markdown Tables
        if stripped.startswith("|") and stripped.endswith("|"):
            in_table = True
            table_lines.append(stripped)
            idx += 1
            continue
        elif in_table:
            in_table = False
            flush_table()

        # Handle Page Breaks
        if stripped == r"\newpage" or stripped == "---":
            doc.add_page_break()
            idx += 1
            continue

        # Skip raw LaTeX commands
        if stripped.startswith(r"\vspace") or stripped.startswith(r"\noindent") or \
           stripped.startswith(r"\begin{") or stripped.startswith(r"\end{") or \
           stripped.startswith(r"\textbf{") or stripped.startswith(r"\end"):
            idx += 1
            continue

        if not stripped:
            idx += 1
            continue

        # Check for Figure References to Insert Real Images!
        # If line mentions "*Figure X.Y: ...*" or is a figure header in text
        fig_match = re.search(r'\*(Figure\s+\d+\.\d+):', stripped)
        if fig_match:
            fig_key = fig_match.group(1)
            if fig_key in FIGURE_MAP and fig_key not in inserted_figures:
                insert_image_and_caption(fig_key)
                inserted_figures.add(fig_key)
                idx += 1
                continue

        # Chapter Headings (# Chapter ...)
        if stripped.startswith("# "):
            title_text = stripped[2:].strip()
            p = doc.add_paragraph()
            is_center = any(kw in title_text for kw in ["FACULTY LEAVE AI", "REPORT", "CERTIFICATE", "Candidate"])
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if is_center else WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(18)
            p.paragraph_format.space_after = Pt(8)
            p.paragraph_format.keep_with_next = True
            run = p.add_run(title_text)
            run.font.name = "Times New Roman"
            run.font.size = Pt(17)
            run.bold = True
            run.font.color.rgb = RGBColor(26, 54, 93)  # #1A365D
            idx += 1
            continue

        # Section Headings (## ...)
        if stripped.startswith("## "):
            sec_text = stripped[3:].strip()
            p = doc.add_paragraph()
            is_center = sec_text in ["A REPORT", "CERTIFICATE", "Candidate’s Declaration", "Acknowledgment", "Abstract", "Candidate Disclosure on the Use of AI Tools"]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if is_center else WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(14)
            p.paragraph_format.space_after = Pt(6)
            p.paragraph_format.keep_with_next = True
            run = p.add_run(sec_text)
            run.font.name = "Times New Roman"
            run.font.size = Pt(14)
            run.bold = True
            run.font.color.rgb = RGBColor(44, 82, 130)  # #2C5282
            idx += 1
            continue

        # Subsection Headings (### ...)
        if stripped.startswith("### "):
            subsec_text = stripped[4:].strip()
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(10)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.keep_with_next = True
            run = p.add_run(subsec_text)
            run.font.name = "Times New Roman"
            run.font.size = Pt(12.5)
            run.bold = True
            run.font.color.rgb = RGBColor(45, 55, 72)
            idx += 1

            # Check if this subsection corresponds to a figure that wasn't placed
            if "4.7 Master Timetable Ingestion" in subsec_text and "Figure 4.7" not in inserted_figures:
                pass
            continue

        # Sub-subsections (#### ...)
        if stripped.startswith("#### "):
            subsec_text = stripped[5:].strip()
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(8)
            p.paragraph_format.space_after = Pt(3)
            p.paragraph_format.keep_with_next = True
            run = p.add_run(subsec_text)
            run.font.name = "Times New Roman"
            run.font.size = Pt(11.5)
            run.bold = True
            run.italic = True
            run.font.color.rgb = RGBColor(74, 85, 104)
            idx += 1
            continue

        # Bullet items
        bullet_match = re.match(r'^[-*]\s+(.*)', stripped)
        if bullet_match:
            b_text = bullet_match.group(1)
            p = doc.add_paragraph(style='List Bullet')
            p.paragraph_format.left_indent = Inches(0.25)
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(3)
            p.paragraph_format.line_spacing = 1.35
            add_formatted_runs(p, b_text, base_font_size=11.5)
            idx += 1
            continue

        # Numbered items
        num_match = re.match(r'^(\d+)\.\s+(.*)', stripped)
        if num_match:
            n_num = num_match.group(1)
            n_text = num_match.group(2)
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.35)
            p.paragraph_format.first_line_indent = Inches(-0.35)
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(3)
            p.paragraph_format.line_spacing = 1.35
            r_num = p.add_run(f"{n_num}.  ")
            r_num.font.name = "Times New Roman"
            r_num.font.size = Pt(11.5)
            r_num.bold = True
            add_formatted_runs(p, n_text, base_font_size=11.5)
            idx += 1
            continue

        # Blockquote
        if stripped.startswith("> "):
            q_text = stripped[2:].strip()
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.4)
            p.paragraph_format.right_indent = Inches(0.4)
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.line_spacing = 1.25
            add_formatted_runs(p, q_text, base_font_size=11, is_italic_base=True, color_rgb=(70, 70, 70))
            idx += 1
            continue

        # Special Signature Table for Certificate & Declaration
        if "Project Guide:" in stripped and "Head of Department:" in stripped:
            # Create a 2-column borderless table
            sig_tbl = doc.add_table(rows=1, cols=2)
            sig_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
            remove_table_borders(sig_tbl)
            cell_left = sig_tbl.rows[0].cells[0]
            cell_right = sig_tbl.rows[0].cells[1]
            
            p_l = cell_left.paragraphs[0]
            p_l.paragraph_format.line_spacing = 1.2
            add_formatted_runs(p_l, "**Project Guide:**\n\n\n\n**Prof. Dr. Harshadkumar B. Prajapati**\nProfessor,\nDepartment of Information Technology,\nFaculty of Technology,\nDharmsinh Desai University,\nNadiad–387001, Gujarat, INDIA", base_font_size=10.5)

            p_r = cell_right.paragraphs[0]
            p_r.paragraph_format.line_spacing = 1.2
            add_formatted_runs(p_r, "**Head of Department:**\n\n\n\n**Prof. Dr. Vipul K. Dabhi**\nProfessor & Head,\nDepartment of Information Technology,\nFaculty of Technology,\nDharmsinh Desai University,\nNadiad–387001, Gujarat, INDIA", base_font_size=10.5)
            idx += 1
            continue

        # Regular Paragraph
        is_center = any(kw in stripped for kw in [
            "DHARMSINH DESAI UNIVERSITY", "FACULTY OF TECHNOLOGY", "DEPARTMENT OF INFORMATION TECHNOLOGY",
            "Nadiad–387001", "October 2026", "Submitted in partial fulfillment"
        ])
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if is_center else WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.line_spacing = 1.5   # 1.5 line spacing strictly as required by DDU
        add_formatted_runs(p, stripped, base_font_size=12)

        # Check if UI screenshots should be inserted after specific paragraphs in Chapter 4
        if "Section 4.7" in stripped or "interface modules" in stripped:
            for ui_fig in ["Figure 4.6", "Figure 4.7", "Figure 4.8", "Figure 4.9", "Figure 4.10", "Figure 4.11"]:
                if ui_fig not in inserted_figures:
                    insert_image_and_caption(ui_fig)
                    inserted_figures.add(ui_fig)

        # Check for Chapter 5 figures
        if "Section 5.1.1" in stripped or "morphological kernels" in stripped:
            if "Figure 5.1" not in inserted_figures:
                insert_image_and_caption("Figure 5.1")
                inserted_figures.add("Figure 5.1")

        if "Section 5.1.3" in stripped or "Adaptive CLAHE" in stripped:
            if "Figure 5.2" not in inserted_figures:
                insert_image_and_caption("Figure 5.2")
                inserted_figures.add("Figure 5.2")

        if "Section 5.1.4" in stripped or "Discrepancy Engine Formulation" in stripped:
            if "Figure 5.3" not in inserted_figures:
                insert_image_and_caption("Figure 5.3")
                inserted_figures.add("Figure 5.3")

        idx += 1

    if in_table:
        flush_table()
    if in_code_block:
        flush_code()

    # Ensure all remaining figures are appended if missed
    for fig_key in sorted(FIGURE_MAP.keys()):
        if fig_key not in inserted_figures:
            insert_image_and_caption(fig_key)
            inserted_figures.add(fig_key)

    doc.save(DOCX_OUT)
    size_kb = os.path.getsize(DOCX_OUT) / 1024
    print(f"Successfully generated DDU report DOCX: {DOCX_OUT} ({size_kb:.1f} KB)")
    print(f"Total Figures embedded: {len(inserted_figures)} / {len(FIGURE_MAP)}")

if __name__ == "__main__":
    build_report()
