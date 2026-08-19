#!/usr/bin/env python3
"""
Build Camera-Ready KDP Paperback & Hardcover PDF (6x9) for The Gentle Return
Adheres strictly to Amazon KDP interior specifications (G202145060)
Guarantees compliant gutter (>0.625\") and safety margins (>0.375\") on all pages.
"""

import os
import re
from pathlib import Path

from reportlab.lib.pagesizes import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

PROJECT_DIR = Path(__file__).parent.parent
MANUSCRIPT_DIR = PROJECT_DIR / "manuscript"
CHAPTERS_DIR = MANUSCRIPT_DIR / "chapters"
OUTPUT_DIR = PROJECT_DIR / "build" / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 6x9 inch page dimensions
PAGE_WIDTH = 6.0 * inch
PAGE_HEIGHT = 9.0 * inch

# Margins strictly conforming to KDP specifications for 300+ pages
# Gutter requirement >= 0.625\", Outside >= 0.250\", Top/Bottom >= 0.375\" for headers/footers
MARGIN_LEFT = 0.80 * inch    # 20.3 mm (exceeds 15.875 mm gutter rule)
MARGIN_RIGHT = 0.80 * inch   # 20.3 mm (exceeds 6.35 mm outside rule)
MARGIN_TOP = 0.875 * inch    # 22.2 mm (leaves safe zone for running headers)
MARGIN_BOTTOM = 0.875 * inch # 22.2 mm (leaves safe zone for page numbers)

USABLE_WIDTH = PAGE_WIDTH - MARGIN_LEFT - MARGIN_RIGHT # 4.40 inch
USABLE_HEIGHT = PAGE_HEIGHT - MARGIN_TOP - MARGIN_BOTTOM # 7.25 inch


class KDPBookCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        page_num = self._pageNumber
        
        # Suppress on front matter pages (Half title, Title, Copyright, Dedication, Epigraph, TOC)
        if page_num <= 6:
            return

        is_odd = (page_num % 2 == 1)
        
        # Position headers and footers safely within KDP printable margin bounds
        header_y = PAGE_HEIGHT - 0.58 * inch  # 0.58 in from top (safe zone is 0.375 to 0.875)
        footer_y = 0.52 * inch                # 0.52 in from bottom (safe zone is 0.375 to 0.875)
        center_x = PAGE_WIDTH / 2.0

        # Running header (small caps / italic)
        self.saveState()
        self.setFont("Times-Italic", 8.5)
        self.setFillColorRGB(0.25, 0.25, 0.25)
        
        if is_odd:
            self.drawCentredString(center_x, header_y, "THE GENTLE RETURN")
        else:
            self.drawCentredString(center_x, header_y, "MATTHEW JAMES HAGEN")
        
        # Bottom page number
        self.setFont("Times-Roman", 9.5)
        self.setFillColorRGB(0.1, 0.1, 0.1)
        self.drawCentredString(center_x, footer_y, str(page_num))
        self.restoreState()


def format_inline(text):
    text = text.replace("&", "&amp;")
    text = re.sub(r"&amp;([a-zA-Z0-9#]+;)", r"&\1", text)
    
    text = re.sub(r"\*\*\*(.+?)\*\*\*", r"<b><i>\1</i></b>", text)
    text = re.sub(r"___(.+?)___", r"<b><i>\1</i></b>", text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"__(.+?)__", r"<b>\1</b>", text)
    text = re.sub(r"\*(.+?)\*", r"<i>\1</i>", text)
    text = re.sub(r"_(.+?)_", r"<i>\1</i>", text)
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
    return text


def parse_markdown(text, styles):
    flowables = []
    lines = text.strip().splitlines()
    i = 0
    first_p = False

    while i < len(lines):
        line = lines[i].rstrip()
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        if stripped == "---":
            flowables.append(Spacer(1, 10))
            flowables.append(Paragraph("*   *   *", styles["SceneDivider"]))
            flowables.append(Spacer(1, 10))
            first_p = True
            i += 1
            continue

        if stripped.startswith("# "):
            h_text = stripped[2:].strip()
            flowables.append(PageBreak())
            flowables.append(Spacer(1, 0.5 * inch))
            
            if ":" in h_text and ("Chapter" in h_text or "Prologue" in h_text or "Epilogue" in h_text):
                parts = h_text.split(":", 1)
                num_part = parts[0].strip().upper()
                title_part = parts[1].strip()
                flowables.append(Paragraph(num_part, styles["ChapterLabel"]))
                flowables.append(Spacer(1, 6))
                flowables.append(Paragraph(title_part, styles["ChapterTitle"]))
            else:
                flowables.append(Paragraph(h_text, styles["MajorHeading"]))
            
            flowables.append(Spacer(1, 22))
            first_p = True
            i += 1
            continue

        if stripped.startswith("## "):
            h2_text = stripped[3:].strip()
            flowables.append(Spacer(1, 14))
            flowables.append(Paragraph(h2_text, styles["SectionHeading"]))
            flowables.append(Spacer(1, 8))
            first_p = True
            i += 1
            continue

        if stripped.startswith("### "):
            h3_text = stripped[4:].strip()
            flowables.append(Spacer(1, 10))
            flowables.append(Paragraph(h3_text, styles["SubSectionHeading"]))
            flowables.append(Spacer(1, 6))
            first_p = True
            i += 1
            continue

        if stripped.startswith("- ") or stripped.startswith("* "):
            item_text = format_inline(stripped[2:].strip())
            flowables.append(Paragraph(f"• {item_text}", styles["BulletText"]))
            i += 1
            continue

        num_match = re.match(r"^(\d+)\.\s+(.+)$", stripped)
        if num_match:
            num = num_match.group(1)
            item_text = format_inline(num_match.group(2))
            flowables.append(Paragraph(f"{num}. {item_text}", styles["NumberedText"]))
            i += 1
            continue

        if stripped.startswith("> "):
            bq_text = format_inline(stripped[2:].strip())
            flowables.append(Spacer(1, 6))
            flowables.append(Paragraph(bq_text, styles["BlockQuote"]))
            flowables.append(Spacer(1, 6))
            i += 1
            continue

        # Accumulate paragraph
        para_lines = [stripped]
        while i + 1 < len(lines):
            next_line = lines[i + 1].rstrip()
            next_stripped = next_line.strip()
            if not next_stripped or next_stripped.startswith("#") or next_stripped == "---" or next_stripped.startswith("- ") or next_stripped.startswith("> ") or re.match(r"^\d+\.\s+", next_stripped):
                break
            para_lines.append(next_stripped)
            i += 1

        para_text = " ".join(para_lines)
        para_text = format_inline(para_text)

        if first_p:
            flowables.append(Paragraph(para_text, styles["BodyFirst"]))
            first_p = False
        else:
            flowables.append(Paragraph(para_text, styles["BodyIndent"]))

        i += 1

    return flowables


def build_pdf():
    pdf_path = OUTPUT_DIR / "the-gentle-return-print-6x9.pdf"
    print(f"Building KDP 6x9 Print PDF: {pdf_path}")

    doc = BaseDocTemplate(
        str(pdf_path),
        pagesize=(PAGE_WIDTH, PAGE_HEIGHT),
        leftMargin=MARGIN_LEFT,
        rightMargin=MARGIN_RIGHT,
        topMargin=MARGIN_TOP,
        bottomMargin=MARGIN_BOTTOM
    )

    page_frame = Frame(
        MARGIN_LEFT, MARGIN_BOTTOM, USABLE_WIDTH, USABLE_HEIGHT,
        id="book_frame", topPadding=0, bottomPadding=0, leftPadding=0, rightPadding=0
    )

    doc.addPageTemplates([
        PageTemplate(id="BookPage", frames=[page_frame]),
    ])

    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        "BodyIndent",
        fontName="Times-Roman",
        fontSize=10.5,
        leading=14.5,
        alignment=TA_JUSTIFY,
        firstLineIndent=18,
        spaceBefore=0,
        spaceAfter=0
    ))
    styles.add(ParagraphStyle(
        "BodyFirst",
        fontName="Times-Roman",
        fontSize=10.5,
        leading=14.5,
        alignment=TA_JUSTIFY,
        firstLineIndent=0,
        spaceBefore=0,
        spaceAfter=0
    ))
    styles.add(ParagraphStyle(
        "ChapterLabel",
        fontName="Times-Roman",
        fontSize=11,
        leading=15,
        alignment=TA_CENTER,
        textColor="#444444"
    ))
    styles.add(ParagraphStyle(
        "ChapterTitle",
        fontName="Times-Bold",
        fontSize=18,
        leading=22,
        alignment=TA_CENTER,
        textColor="#111111"
    ))
    styles.add(ParagraphStyle(
        "MajorHeading",
        fontName="Times-Bold",
        fontSize=17,
        leading=21,
        alignment=TA_CENTER,
        textColor="#111111"
    ))
    styles.add(ParagraphStyle(
        "SectionHeading",
        fontName="Times-Bold",
        fontSize=11.5,
        leading=15,
        alignment=TA_CENTER,
        textColor="#222222"
    ))
    styles.add(ParagraphStyle(
        "SubSectionHeading",
        fontName="Times-Bold",
        fontSize=10.5,
        leading=14,
        alignment=TA_LEFT,
        textColor="#222222"
    ))
    styles.add(ParagraphStyle(
        "SceneDivider",
        fontName="Times-Roman",
        fontSize=9,
        leading=12,
        alignment=TA_CENTER,
        textColor="#555555"
    ))
    styles.add(ParagraphStyle(
        "BlockQuote",
        fontName="Times-Italic",
        fontSize=10,
        leading=14,
        alignment=TA_JUSTIFY,
        leftIndent=24,
        rightIndent=24
    ))
    styles.add(ParagraphStyle(
        "BulletText",
        fontName="Times-Roman",
        fontSize=10,
        leading=14,
        leftIndent=14,
        firstLineIndent=-10,
        alignment=TA_LEFT
    ))
    styles.add(ParagraphStyle(
        "NumberedText",
        fontName="Times-Roman",
        fontSize=10,
        leading=14,
        leftIndent=16,
        firstLineIndent=-12,
        alignment=TA_LEFT,
        spaceBefore=3,
        spaceAfter=3
    ))

    story = []

    # Front Matter
    front_file = MANUSCRIPT_DIR / "front-matter.md"
    if front_file.exists():
        story.extend(parse_markdown(front_file.read_text(encoding="utf-8"), styles))

    # Chapters
    chapter_files = sorted(CHAPTERS_DIR.glob("*.md"))
    for ch_path in chapter_files:
        story.extend(parse_markdown(ch_path.read_text(encoding="utf-8"), styles))

    # Back Matter
    back_file = MANUSCRIPT_DIR / "back-matter.md"
    if back_file.exists():
        story.extend(parse_markdown(back_file.read_text(encoding="utf-8"), styles))

    doc.build(story, canvasmaker=KDPBookCanvas)
    
    file_size_mb = pdf_path.stat().st_size / (1024 * 1024)
    print(f"Successfully generated: {pdf_path} ({file_size_mb:.2f} MB)")


if __name__ == "__main__":
    build_pdf()
