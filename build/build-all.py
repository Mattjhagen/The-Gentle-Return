#!/usr/bin/env python3
"""
Master Build Script for The Gentle Return
Compiles all Amazon KDP formats for all 3 editions:
1. Paperback (6x9 Interior PDF + Full-Wrap Cover PDF)
2. Hardcover (6x9 Interior PDF + Case-Laminate Wrap Cover PDF)
3. Kindle eBook (EPUB 3 + HTML + Standalone eBook Cover)
4. Word Interior (.docx)
"""

import subprocess
import sys
from pathlib import Path

BUILD_DIR = Path(__file__).parent
PROJECT_DIR = BUILD_DIR.parent

print("==========================================================")
print("     THE GENTLE RETURN — COMPLETE KDP BUILD PIPELINE      ")
print("          [Paperback • Hardcover • Kindle eBook]          ")
print("==========================================================\n")

# 1. Print Interior PDF (Paperback & Hardcover)
print("[1/4] Compiling 6x9 Print Interior PDF (324 Pages)...")
res = subprocess.run([sys.executable, str(BUILD_DIR / "build-print-pdf.py")])
if res.returncode != 0:
    print("Error building Print PDF")
    sys.exit(1)

# 2. Word Manuscript DOCX
print("\n[2/4] Compiling Amazon KDP Word Interior (.docx)...")
res = subprocess.run([sys.executable, str(BUILD_DIR / "build-docx.py")])
if res.returncode != 0:
    print("Error building DOCX")
    sys.exit(1)

# 3. EPUB & HTML eBook
print("\n[3/4] Compiling Kindle EPUB 3 & Standalone HTML eBook...")
res = subprocess.run([sys.executable, str(BUILD_DIR / "build-ebook.py")])
if res.returncode != 0:
    print("Error building eBook")
    sys.exit(1)

# 4. All Covers (Paperback, Hardcover, eBook)
print("\n[4/4] Generating All KDP Cover Assets (Paperback, Hardcover, eBook)...")
res = subprocess.run([sys.executable, str(PROJECT_DIR / "cover" / "generate-all-covers.py")])
if res.returncode != 0:
    print("Error building Covers")
    sys.exit(1)

print("\n==========================================================")
print("                  ALL BUILDS COMPLETE!                     ")
print("==========================================================")
print("\nManuscript Interior Files (build/output/):")
for f in sorted((BUILD_DIR / "output").glob("*.*")):
    print(f"  - {f.name} ({f.stat().st_size / (1024*1024):.2f} MB)")

print("\nCover Wrap Files (cover/output/):")
for f in sorted((PROJECT_DIR / "cover" / "output").glob("*.*")):
    print(f"  - {f.name} ({f.stat().st_size / (1024*1024):.2f} MB)")
