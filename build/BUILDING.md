# Building The Gentle Return

## Prerequisites

Python 3.9+ with the following packages:
```bash
pip install reportlab python-docx pillow markdown
```

## Quick Build Commands

### Build Everything (Print PDF, DOCX, EPUB, HTML, Full-Wrap Cover)
```bash
python3 build/build-all.py
```

### Build Individual Formats
```bash
# Print PDF (6" x 9" camera-ready for paperback)
python3 build/build-print-pdf.py

# Word Manuscript (.docx for KDP interior upload)
python3 build/build-docx.py

# eBook (EPUB 3 & HTML)
python3 build/build-ebook.py

# Paperback Cover (300 DPI Full-Wrap PDF for KDP)
python3 cover/generate-kdp-cover.py
```

## Output Directory Structure

```
The-Gentle-Return/
├── build/output/
│   ├── the-gentle-return-print-6x9.pdf   # KDP Paperback Interior PDF (324 pages)
│   ├── the-gentle-return-kdp.docx        # KDP Word Manuscript
│   ├── the-gentle-return.epub            # Kindle eBook EPUB
│   └── the-gentle-return-interior.html   # Standalone HTML Interior
└── cover/output/
    ├── the-gentle-return-paperback-cover-kdp.pdf # Full-Wrap Cover PDF (300 DPI)
    ├── the-gentle-return-paperback-cover-kdp.png # Full-Wrap PNG (3918 x 2775 px)
    └── the-gentle-return-paperback-cover-kdp.jpg # Full-Wrap JPEG
```
