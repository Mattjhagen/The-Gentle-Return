#!/usr/bin/env python3
"""
Build Camera-Ready KDP Print PDF (6x9) for The Gentle Return
100% Embedded TrueType Fonts (Georgia) & Strict KDP Margin/Gutter Compliance
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
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import reportlab.rl_config
reportlab.rl_config.canvas_base_font = "Georgia"

PROJECT_DIR = Path(__file__).parent.parent
MANUSCRIPT_DIR = PROJECT_DIR / "manuscript"
CHAPTERS_DIR = MANUSCRIPT_DIR / "chapters"
OUTPUT_DIR = PROJECT_DIR / "build" / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Register 100% Embedded TrueType Fonts (Resolves KDP font embedding error)
FONT_DIR = "/System/Library/Fonts/Supplemental"
pdfmetrics.registerFont(TTFont("Georgia", f"{FONT_DIR}/Georgia.ttf"))
pdfmetrics.registerFont(TTFont("Georgia-Bold", f"{FONT_DIR}/Georgia Bold.ttf"))
pdfmetrics.registerFont(TTFont("Georgia-Italic", f"{FONT_DIR}/Georgia Italic.ttf"))
pdfmetrics.registerFont(TTFont("Georgia-BoldItalic", f"{FONT_DIR}/Georgia Bold Italic.ttf"))

pdfmetrics.registerFontFamily(
    "Georgia",
    normal="Georgia",
    bold="Georgia-Bold",
    italic="Georgia-Italic",
    boldItalic="Georgia-BoldItalic"
)

# 6x9 inch page dimensions
PAGE_WIDTH = 6.0 * inch
PAGE_HEIGHT = 9.0 * inch

# Strict KDP Margins (Guarantees gutter >= 0.625\" and outside/top/bottom >= 0.250\" on ALL pages)
MARGIN_LEFT = 0.85 * inch    # 21.59 mm (well exceeds 15.875 mm gutter)
MARGIN_RIGHT = 0.85 * inch   # 21.59 mm (well exceeds 6.35 mm outside)
MARGIN_TOP = 0.875 * inch    # 22.2 mm (safe top margin)
MARGIN_BOTTOM = 0.875 * inch # 22.2 mm (safe bottom margin)

USABLE_WIDTH = PAGE_WIDTH - MARGIN_LEFT - MARGIN_RIGHT # 4.30 inch
USABLE_HEIGHT = PAGE_HEIGHT - MARGIN_TOP - MARGIN_BOTTOM # 7.25 inch


class EmbeddedKDPCanvas(canvas.Canvas):
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

        # Running header with embedded Georgia-Italic
        self.saveState()
        self.setFont("Georgia-Italic", 8.0)
        self.setFillColorRGB(0.25, 0.25, 0.25)
        
        if is_odd:
            self.drawCentredString(center_x, header_y, "THE GENTLE RETURN")
        else:
            self.drawCentredString(center_x, header_y, "MATTHEW JAMES HAGEN")
        
        # Bottom page number with embedded Georgia
        self.setFont("Georgia", 9.0)
        self.setFillColorRGB(0.15, 0.15, 0.15)
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
            
            flowables.append(Spacer(1, 20))
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
    print(f"Building KDP 6x9 Print PDF with 100% Embedded TrueType Fonts: {pdf_path}")

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
    for s in styles.byName.values():
        s.fontName = "Georgia"

    styles.add(ParagraphStyle(
        "BodyIndent",
        fontName="Georgia",
        fontSize=10.0,
        leading=14.0,
        alignment=TA_JUSTIFY,
        firstLineIndent=16,
        spaceBefore=0,
        spaceAfter=0
    ))
    styles.add(ParagraphStyle(
        "BodyFirst",
        fontName="Georgia",
        fontSize=10.0,
        leading=14.0,
        alignment=TA_JUSTIFY,
        firstLineIndent=0,
        spaceBefore=0,
        spaceAfter=0
    ))
    styles.add(ParagraphStyle(
        "ChapterLabel",
        fontName="Georgia",
        fontSize=10.5,
        leading=14,
        alignment=TA_CENTER,
        textColor="#444444"
    ))
    styles.add(ParagraphStyle(
        "ChapterTitle",
        fontName="Georgia-Bold",
        fontSize=17,
        leading=21,
        alignment=TA_CENTER,
        textColor="#111111"
    ))
    styles.add(ParagraphStyle(
        "MajorHeading",
        fontName="Georgia-Bold",
        fontSize=16,
        leading=20,
        alignment=TA_CENTER,
        textColor="#111111"
    ))
    styles.add(ParagraphStyle(
        "SectionHeading",
        fontName="Georgia-Bold",
        fontSize=11,
        leading=15,
        alignment=TA_CENTER,
        textColor="#222222"
    ))
    styles.add(ParagraphStyle(
        "SubSectionHeading",
        fontName="Georgia-Bold",
        fontSize=10,
        leading=13,
        alignment=TA_LEFT,
        textColor="#222222"
    ))
    styles.add(ParagraphStyle(
        "SceneDivider",
        fontName="Georgia",
        fontSize=9,
        leading=12,
        alignment=TA_CENTER,
        textColor="#555555"
    ))
    styles.add(ParagraphStyle(
        "BlockQuote",
        fontName="Georgia-Italic",
        fontSize=9.5,
        leading=13.5,
        alignment=TA_JUSTIFY,
        leftIndent=20,
        rightIndent=20
    ))
    styles.add(ParagraphStyle(
        "BulletText",
        fontName="Georgia",
        fontSize=9.5,
        leading=13.5,
        leftIndent=14,
        firstLineIndent=-10,
        alignment=TA_LEFT
    ))
    styles.add(ParagraphStyle(
        "NumberedText",
        fontName="Georgia",
        fontSize=9.5,
        leading=13.5,
        leftIndent=16,
        firstLineIndent=-12,
        alignment=TA_LEFT,
        spaceBefore=2,
        spaceAfter=2
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

    doc.build(story, canvasmaker=EmbeddedKDPCanvas)
    
    file_size_mb = pdf_path.stat().st_size / (1024 * 1024)
    print(f"Successfully generated: {pdf_path} ({file_size_mb:.2f} MB)")


if __name__ == "__main__":
    build_pdf()
