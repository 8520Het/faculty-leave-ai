"""
Generate Overleaf / TeX Live compile-ready main.tex matching DDU academic report formatting.
"""

import os
import re

MD_PATH = r"c:\Users\HP\Desktop\faculty-leave-ai\docs\BTECH_PROJECT_REPORT.md"
TEX_PATH = r"c:\Users\HP\Desktop\faculty-leave-ai\docs\main.tex"

def escape_latex(s):
    # Do not escape if already a command
    if s.startswith('\\'):
        return s
    replacements = [
        ('&', r'\&'),
        ('%', r'\%'),
        ('$', r'\$'),
        ('#', r'\#'),
        ('_', r'\_'),
        ('{', r'\{'),
        ('}', r'\}'),
        ('~', r'\textasciitilde{}'),
        ('^', r'\textasciicircum{}'),
    ]
    for old, new in replacements:
        s = s.replace(old, new)
    return s

def md_to_tex_inline(text):
    # Bold
    text = re.sub(r'\*\*(.*?)\*\*', r'\\textbf{\1}', text)
    # Italic
    text = re.sub(r'\*(.*?)\*', r'\\textit{\1}', text)
    # Code
    text = re.sub(r'`(.*?)`', r'\\texttt{\1}', text)
    return text

def build_latex():
    with open(MD_PATH, 'r', encoding='utf-8') as f:
        md = f.read()

    tex_lines = [
        r"\documentclass[12pt,letterpaper]{report}",
        r"\usepackage[utf8]{inputenc}",
        r"\usepackage[top=1.0in,bottom=1.0in,left=1.5in,right=1.0in]{geometry}",
        r"\usepackage{graphicx}",
        r"\usepackage{amsmath,amssymb}",
        r"\usepackage{booktabs,tabularx,longtable,array}",
        r"\usepackage{xcolor}",
        r"\usepackage{fancyhdr}",
        r"\usepackage{setspace}",
        r"\usepackage{hyperref}",
        r"\usepackage{caption}",
        r"\usepackage{titlesec}",
        "",
        r"\definecolor{dduNavy}{RGB}{26, 54, 93}",
        r"\definecolor{dduBlue}{RGB}{44, 82, 130}",
        r"\definecolor{dduGray}{RGB}{74, 85, 104}",
        r"\definecolor{codeBg}{RGB}{248, 250, 252}",
        "",
        r"\setstretch{1.5}",
        r"\pagestyle{fancy}",
        r"\fancyhf{}",
        r"\fancyhead[R]{\textit{\footnotesize Department of Information Technology, Dharmsinh Desai University | Faculty Leave AI}}",
        r"\fancyfoot[C]{\thepage}",
        r"\renewcommand{\headrulewidth}{0.4pt}",
        "",
        r"\hypersetup{",
        r"    colorlinks=true,",
        r"    linkcolor=dduNavy,",
        r"    citecolor=dduBlue,",
        r"    urlcolor=dduBlue",
        r"}",
        "",
        r"\titleformat{\chapter}[display]",
        r"    {\normalfont\huge\bfseries\color{dduNavy}}{\chaptertitlename\ \thechapter}{20pt}{\Huge}",
        r"\titleformat{\section}",
        r"    {\normalfont\Large\bfseries\color{dduBlue}}{\thesection}{1em}{}",
        r"\titleformat{\subsection}",
        r"    {\normalfont\large\bfseries\color{dduGray}}{\thesubsection}{1em}{}",
        "",
        r"\begin{document}",
        "",
        r"% =============================================================================",
        r"% TITLE PAGE",
        r"% =============================================================================",
        r"\begin{titlepage}",
        r"\begin{center}",
        r"    \vspace*{0.5cm}",
        r"    {\LARGE \textbf{\color{dduNavy} FACULTY LEAVE AI: AUTOMATED HANDWRITTEN LEAVE ARRANGEMENT AND NOTIFICATION SYSTEM WITH MULTI-FACTOR TIMETABLE VERIFICATION}}\\[1.0cm]",
        r"    {\Large \textbf{(B. Tech. Project--II)}}\\[1.2cm]",
        r"    {\large \textbf{A REPORT}}\\[0.8cm]",
        r"    {\normalsize Submitted in partial fulfillment of the requirements for Semester VII of}\\[0.3cm]",
        r"    {\large \textbf{BACHELOR OF TECHNOLOGY}}\\[0.2cm]",
        r"    {\large \textbf{(INFORMATION TECHNOLOGY)}}\\[1.2cm]",
        r"    {\normalsize \textbf{Submitted by:}}\\[0.4cm]",
        r"    {\large \textbf{Het Patel}} \quad (Roll No.: IT155, ID: 24ITUOS910)\\[0.2cm]",
        r"    {\large \textbf{Riya Ajit Trivedi}} \quad (Roll No.: IT081, ID: 23ECUOG183)\\[1.2cm]",
        r"    {\normalsize \textbf{Under the guidance of:}}\\[0.3cm]",
        r"    {\large \textbf{Prof. Dr. Harshadkumar B. Prajapati}}\\[0.1cm]",
        r"    {\normalsize Professor, Department of Information Technology}\\[1.5cm]",
        r"    \includegraphics[width=2.5cm]{figures/fig_4_1_use_case.png}\\[0.8cm]",
        r"    {\large \textbf{Department of Information Technology}}\\[0.1cm]",
        r"    {\large \textbf{Faculty of Technology}}\\[0.1cm]",
        r"    {\Large \textbf{\color{dduNavy} DHARMSINH DESAI UNIVERSITY}}\\[0.1cm]",
        r"    {\normalsize Nadiad--387001, Gujarat, INDIA}\\[0.3cm]",
        r"    {\normalsize \textit{October 2026}}",
        r"\end{center}",
        r"\end{titlepage}",
        "",
        r"\pagenumbering{roman}",
        "",
        r"% =============================================================================",
        r"% PRELIMINARY PAGES",
        r"% =============================================================================",
        r"\chapter*{Candidate Disclosure on the Use of AI Tools}",
        r"\addcontentsline{toc}{chapter}{Candidate Disclosure on the Use of AI Tools}",
        r"In the process of developing the software prototype and compiling this project report, the authors utilized modern generative AI utilities, computer vision toolchains, and assistive writing software strictly in compliance with Dharmsinh Desai University academic integrity guidelines. The specific tools and their respective roles were as follows:",
        r"\begin{enumerate}",
        r"    \item \textbf{GitHub Copilot \& DeepMind Antigravity Pair-Programming Agent}: Utilized for syntactic code completion, boiler-plate FastAPI route drafting, Playwright automated testing harness generation, and writing unit test cases.",
        r"    \item \textbf{Microsoft TrOCR (\texttt{microsoft/trocr-base-handwritten})}: Deployed as the foundational deep transformer vision-encoder-decoder model for decoding cursive handwriting from cropped cell segments of academic leave sheets.",
        r"    \item \textbf{OpenCV \& PyTorch}: Utilized for custom morphological kernel filtering, page deskewing, contour line detection, and inference orchestration.",
        r"    \item \textbf{Grammarly (Academic Edition)}: Utilized to audit technical grammar, verify academic writing tone, eliminate passive-voice inconsistencies, and verify spelling mechanics.",
        r"    \item \textbf{Zotero (Open Source)}: Employed as the bibliographic citation management software to catalog academic literature, IEEE transaction papers, and format reference styles.",
        r"\end{enumerate}",
        r"All architectural solutions, algorithm formulations, database schema designs, timetable discrepancy logic implementations, and final conclusions were conceived, verified, and benchmarked by the authors.",
        "",
        r"\newpage",
        r"\chapter*{Candidate's Declaration}",
        r"\addcontentsline{toc}{chapter}{Candidate's Declaration}",
        r"We hereby declare that this Semester VII B.Tech. Project--II report, entitled \textbf{“FACULTY LEAVE AI: AUTOMATED HANDWRITTEN LEAVE ARRANGEMENT AND NOTIFICATION SYSTEM WITH MULTI-FACTOR TIMETABLE VERIFICATION”}, is our own authentic project work conducted under the guidance and supervision of \textbf{Prof. Dr. Harshadkumar B. Prajapati}, Professor, Department of Information Technology, Dharmsinh Desai University, Nadiad.",
        "",
        r"We further declare that to the best of our knowledge and belief, this report does not contain any part of any work that has been submitted for the award of any degree or diploma either in this University or in any other institution of higher learning without formal academic citation and acknowledgment.",
        r"\vspace{2.0cm}",
        "",
        r"\noindent",
        r"\begin{tabularx}{\textwidth}{XrX}",
        r"\textbf{Het Patel} & & \textbf{Riya Ajit Trivedi} \\",
        r"Roll No.: IT155 & & Roll No.: IT081 \\",
        r"Student ID: 24ITUOS910 & & Student ID: 23ECUOG183 \\",
        r"B. Tech. Semester--VII (IT) & & B. Tech. Semester--VII (IT) \\",
        r"Department of Information Technology & & Department of Information Technology \\",
        r"Dharmsinh Desai University, Nadiad & & Dharmsinh Desai University, Nadiad \\",
        r"\end{tabularx}",
        "",
        r"\vspace{1.0cm}",
        r"\noindent Date: 20th October, 2026 \hfill Place: Nadiad, Gujarat, India",
        "",
        r"\newpage",
        r"\chapter*{CERTIFICATE}",
        r"\addcontentsline{toc}{chapter}{Certificate}",
        r"\begin{center}",
        r"    \textbf{\large DHARMSINH DESAI UNIVERSITY}\\",
        r"    \textbf{FACULTY OF TECHNOLOGY}\\",
        r"    \textbf{DEPARTMENT OF INFORMATION TECHNOLOGY}\\",
        r"    \textit{College Road, Nadiad--387001, Gujarat, INDIA}\\[1.0cm]",
        r"\end{center}",
        r"This is to certify that the project report entitled \textbf{“FACULTY LEAVE AI: AUTOMATED HANDWRITTEN LEAVE ARRANGEMENT AND NOTIFICATION SYSTEM WITH MULTI-FACTOR TIMETABLE VERIFICATION”} submitted for the partial fulfillment of the requirements for the degree of \textbf{Bachelor of Technology in Information Technology} (Semester--VII) is a bona fide record of the research and development work carried out by:",
        r"\begin{center}",
        r"    \textbf{Het Patel} (Roll No.: IT155, ID No.: 24ITUOS910)\\",
        r"    \textbf{Riya Ajit Trivedi} (Roll No.: IT081, ID No.: 23ECUOG183)",
        r"\end{center}",
        r"during the academic year 2026--2027 in the Department of Information Technology, Faculty of Technology, Dharmsinh Desai University, Nadiad. The project has been examined and approved.",
        r"\vspace{2.5cm}",
        "",
        r"\noindent",
        r"\begin{tabularx}{\textwidth}{Xp{2cm}X}",
        r"\textbf{Project Guide:} & & \textbf{Head of Department:} \\[1.5cm]",
        r"\textbf{Prof. Dr. Harshadkumar B. Prajapati} & & \textbf{Prof. Dr. Vipul K. Dabhi} \\",
        r"Professor, & & Professor \& Head, \\",
        r"Department of Information Technology, & & Department of Information Technology, \\",
        r"Faculty of Technology, & & Faculty of Technology, \\",
        r"Dharmsinh Desai University, & & Dharmsinh Desai University, \\",
        r"Nadiad--387001, Gujarat, INDIA & & Nadiad--387001, Gujarat, INDIA",
        r"\end{tabularx}",
        "",
        r"\newpage",
        r"\chapter*{Acknowledgment}",
        r"\addcontentsline{toc}{chapter}{Acknowledgment}",
        r"We express our deepest sense of gratitude to our respected project guide, \textbf{Prof. Dr. Harshadkumar B. Prajapati}, Professor in the Department of Information Technology, Faculty of Technology, Dharmsinh Desai University, for his invaluable supervision, insightful suggestions, constant encouragement, and intellectual guidance throughout the inception, design, and execution of this project.",
        "",
        r"We extend our sincere and heartfelt thanks to \textbf{Prof. Dr. Vipul K. Dabhi}, Head of the Department of Information Technology, for providing the state-of-the-art computational infrastructure, departmental timetable repositories, laboratory facilities, and supportive academic environment necessary to bring this project to fruition.",
        "",
        r"We also convey our profound appreciation to all faculty members, technical laboratory assistants, and administrative staff of the Department of Information Technology for their generous cooperation, testing feedback, and departmental dataset contributions.",
        "",
        r"Finally, we express our warmest thanks to our families, peers, and fellow researchers whose unwavering moral encouragement and patient support sustained our efforts throughout this endeavor.",
        r"\vspace{1.5cm}",
        "",
        r"\noindent \textbf{Het Patel} (\texttt{24ITUOS910}) \hfill \textbf{Riya Ajit Trivedi} (\texttt{23ECUOG183})\\",
        r"\noindent Department of Information Technology \hfill Department of Information Technology\\",
        r"\noindent Dharmsinh Desai University, Nadiad \hfill Dharmsinh Desai University, Nadiad",
        "",
        r"\newpage",
        r"\chapter*{Abstract}",
        r"\addcontentsline{toc}{chapter}{Abstract}",
        r"In higher educational institutions, administrative workflows governing faculty leave and lecture substitutions continue to rely heavily on physical paper application forms filled out with cursive handwriting. In departments running multiple concurrent undergraduate divisions, specialized elective tracks, and multi-batch laboratory sessions, this paper-driven modality introduces severe operational vulnerabilities: scheduling overlaps where substitute teachers are already engaged in lectures elsewhere, classroom double-bookings, non-existent division codes, unrecognized subjects, and delayed notifications that lead to unmonitored classrooms.",
        "",
        r"This project presents \textbf{Faculty Leave AI}, an intelligent, end-to-end vision-driven arrangement and notification system engineered specifically for university academic departments. The platform integrates a modern computer vision pipeline with a multi-factor academic timetable verification engine and an automated notification broker. The ingestion pipeline applies morphological page deskewing, horizontal and vertical grid projection filtering to isolate handwritten lecture assignment rows, ink-ratio density thresholding to eliminate blank form rows, and Microsoft’s TrOCR model enhanced with Contrast Limited Adaptive Histogram Equalization (CLAHE) to transcribe cursive handwriting.",
        "",
        r"Extracted rows are dynamically cross-referenced against a multi-point Academic Curriculum Master and the official Department Timetable. The discrepancy engine detects five distinct classes of anomalies in real time: (i) \textit{Invalid Lecture Spans}, (ii) \textit{Division Discrepancies}, (iii) \textit{Unrecognized Courses}, (iv) \textit{Subject Mismatches}, and (v) \textit{Room and Instructor Discrepancies}. Built on FastAPI, SQLite WAL persistence, and React, the system eliminates administrative latency, guarantees timetable integrity, and ensures academic continuity.",
        "",
        r"\vspace{0.8cm}",
        r"\noindent \textbf{Keywords}: \textit{Handwritten Text Recognition (HTR), Transformer OCR (TrOCR), Timetable Conflict Detection, Academic Workflow Automation, Morphological Cell Segmentation, Higher Education Management.}",
        "",
        r"\newpage",
        r"\tableofcontents",
        r"\listoftables",
        r"\listoffigures",
        "",
        r"\newpage",
        r"\chapter*{Abbreviations}",
        r"\addcontentsline{toc}{chapter}{Abbreviations}",
        r"\begin{longtable}{ll}",
        r"\toprule",
        r"\textbf{Abbreviation} & \textbf{Expanded Form} \\",
        r"\midrule",
        r"\endhead",
        r"\textbf{AI} & Artificial Intelligence \\",
        r"\textbf{API} & Application Programming Interface \\",
        r"\textbf{B.Tech.} & Bachelor of Technology \\",
        r"\textbf{CER} & Character Error Rate \\",
        r"\textbf{CLAHE} & Contrast Limited Adaptive Histogram Equalization \\",
        r"\textbf{CRUD} & Create, Read, Update, Delete \\",
        r"\textbf{CSRF} & Cross-Site Request Forgery \\",
        r"\textbf{CORS} & Cross-Origin Resource Sharing \\",
        r"\textbf{CV} & Computer Vision / Curriculum Vitae \\",
        r"\textbf{DDU} & Dharmsinh Desai University \\",
        r"\textbf{ERD} & Entity-Relationship Diagram \\",
        r"\textbf{HOD} & Head of Department \\",
        r"\textbf{HTML} & HyperText Markup Language \\",
        r"\textbf{HTR} & Handwritten Text Recognition \\",
        r"\textbf{HTTP} & HyperText Transfer Protocol \\",
        r"\textbf{IEEE} & Institute of Electrical and Electronics Engineers \\",
        r"\textbf{IT} & Information Technology \\",
        r"\textbf{JSON} & JavaScript Object Notation \\",
        r"\textbf{ML} & Machine Learning \\",
        r"\textbf{NLP} & Natural Language Processing \\",
        r"\textbf{OCR} & Optical Character Recognition \\",
        r"\textbf{ORM} & Object-Relational Mapping \\",
        r"\textbf{REST} & Representational State Transfer \\",
        r"\textbf{RoI} & Region of Interest \\",
        r"\textbf{SPA} & Single Page Application \\",
        r"\textbf{SQL} & Structured Query Language \\",
        r"\textbf{TrOCR} & Transformer Optical Character Recognition \\",
        r"\textbf{UI} & User Interface \\",
        r"\textbf{UML} & Unified Modeling Language \\",
        r"\textbf{URI} & Uniform Resource Identifier \\",
        r"\textbf{UUID} & Universally Unique Identifier \\",
        r"\textbf{WAL} & Write-Ahead Logging \\",
        r"\textbf{WER} & Word Error Rate \\",
        r"\bottomrule",
        r"\end{longtable}",
        "",
        r"\newpage",
        r"\pagenumbering{arabic}",
        r"\setcounter{page}{1}",
        "",
    ]

    # Map markdown content
    # Process from Chapter 1 onwards
    ch1_idx = md.find("# Chapter 1: Introduction")
    body_md = md[ch1_idx:] if ch1_idx != -1 else md

    # Simple processor for body
    lines = body_md.splitlines()
    for line in lines:
        stripped = line.strip()
        if not stripped:
            tex_lines.append("")
            continue
        if stripped == r"\newpage" or stripped == "---":
            tex_lines.append(r"\newpage")
            continue
        if stripped.startswith("# Chapter "):
            ch_title = stripped.split(":", 1)[1].strip() if ":" in stripped else stripped[10:].strip()
            tex_lines.append(f"\\chapter{{{ch_title}}}")
            continue
        if stripped.startswith("## "):
            sec_title = stripped[3:].strip()
            # Remove numbering if already present
            sec_title = re.sub(r'^\d+\.\d+\s+', '', sec_title)
            tex_lines.append(f"\\section{{{sec_title}}}")
            continue
        if stripped.startswith("### "):
            subsec_title = stripped[4:].strip()
            subsec_title = re.sub(r'^\d+\.\d+\.\d+\s+', '', subsec_title)
            tex_lines.append(f"\\subsection{{{subsec_title}}}")
            continue
        if stripped.startswith("#### "):
            subsubsec_title = stripped[5:].strip()
            tex_lines.append(f"\\subsubsection{{{subsubsec_title}}}")
            continue

        # Image inclusion
        img_match = re.search(r'!\[(.*?)\]\((.*?)\)', stripped)
        if img_match:
            cap = img_match.group(1)
            pth = img_match.group(2)
            fig_num = re.search(r'Figure\s+(\d+\.\d+)', cap)
            lbl = f"fig:{fig_num.group(1).replace('.', '_')}" if fig_num else "fig:unknown"
            tex_lines.append(r"\begin{figure}[htbp]")
            tex_lines.append(r"    \centering")
            tex_lines.append(f"    \\includegraphics[width=0.92\\textwidth]{{{pth}}}")
            tex_lines.append(f"    \\caption{{{cap}}}")
            tex_lines.append(f"    \\label{{{lbl}}}")
            tex_lines.append(r"\end{figure}")
            continue

        # Skip duplicate caption lines after images
        if stripped.startswith("*Figure") and stripped.endswith(".*"):
            continue

        # Bullet items
        bullet_match = re.match(r'^[-*]\s+(.*)', stripped)
        if bullet_match:
            b_txt = md_to_tex_inline(bullet_match.group(1))
            tex_lines.append(f"\\begin{{itemize}}\\item {b_txt}\\end{{itemize}}")
            continue

        # Numbered items
        num_match = re.match(r'^(\d+)\.\s+(.*)', stripped)
        if num_match:
            n_txt = md_to_tex_inline(num_match.group(2))
            tex_lines.append(f"\\begin{{enumerate}}\\item {n_txt}\\end{{enumerate}}")
            continue

        # Regular paragraph
        p_txt = md_to_tex_inline(stripped)
        tex_lines.append(p_txt)

    tex_lines.append(r"\end{document}")

    with open(TEX_PATH, 'w', encoding='utf-8') as f:
        f.write("\n".join(tex_lines))
    print(f"Generated Overleaf-ready LaTeX file: {TEX_PATH} ({os.path.getsize(TEX_PATH)} bytes)")

if __name__ == "__main__":
    build_latex()
