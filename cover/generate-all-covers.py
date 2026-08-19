#!/usr/bin/env python3
"""
Generate all Amazon KDP Cover Formats:
1. Paperback Full-Wrap (300 DPI PDF/PNG/JPG)
2. Hardcover Case-Laminate Full-Wrap (300 DPI PDF/PNG/JPG)
3. Kindle eBook Standalone Front Cover (1600x2560 JPG/PNG)
"""

import os
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

COVER_DIR = Path(__file__).parent
OUTPUT_DIR = COVER_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

DPI = 300
PAGE_COUNT = 324

def create_burgundy_gradient(width, height):
    base = Image.new("RGB", (width, height), (15, 2, 5))
    draw = ImageDraw.Draw(base)
    for y in range(height):
        ratio = y / height
        center_factor = math.sin(ratio * math.pi)
        r = int(18 + 35 * center_factor)
        g = int(2 + 6 * center_factor)
        b = int(6 + 10 * center_factor)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    return base

def find_system_font(size, bold=False, italic=False):
    if bold:
        paths = ["/System/Library/Fonts/Supplemental/Georgia Bold.ttf", "/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf", "/Library/Fonts/Georgia Bold.ttf"]
    elif italic:
        paths = ["/System/Library/Fonts/Supplemental/Georgia Italic.ttf", "/System/Library/Fonts/Supplemental/Times New Roman Italic.ttf", "/Library/Fonts/Georgia Italic.ttf"]
    else:
        paths = ["/System/Library/Fonts/Supplemental/Georgia.ttf", "/System/Library/Fonts/Supplemental/Times New Roman.ttf", "/Library/Fonts/Georgia.ttf"]
    for p in paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()

def wrap_text(text, font, max_width, draw):
    words = text.split(" ")
    lines = []
    current_line = []
    for word in words:
        test_line = " ".join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        w = bbox[2] - bbox[0]
        if w <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]
    if current_line:
        lines.append(" ".join(current_line))
    return lines

def build_paperback():
    print("--> Generating Paperback Full-Wrap (13.040in x 9.250in)...")
    # Exact KDP Official Template Specifications for 351 pages white paper:
    TOTAL_W_IN = 13.040
    TOTAL_H_IN = 9.250
    SPINE_W_IN = 0.790
    BLEED_IN = 0.125
    
    W_PX = int(round(TOTAL_W_IN * DPI))       # 3912 px
    H_PX = int(round(TOTAL_H_IN * DPI))       # 2775 px
    SPINE_W_PX = int(round(SPINE_W_IN * DPI)) # 237 px
    BLEED_PX = int(round(BLEED_IN * DPI))     # 38 px

    BOARD_BACK_PX = (W_PX - SPINE_W_PX) // 2  # 1837 px
    BOARD_FRONT_PX = W_PX - BOARD_BACK_PX - SPINE_W_PX # 1838 px

    SPINE_X = BOARD_BACK_PX
    FRONT_X = BOARD_BACK_PX + SPINE_W_PX

    cover = create_burgundy_gradient(W_PX, H_PX)
    
    # Front artwork
    art_path = COVER_DIR / "The-Gentle-Return-KDP-book-cover.jpeg"
    if art_path.exists():
        front_img = Image.open(art_path).convert("RGB").resize((BOARD_FRONT_PX, H_PX), Image.Resampling.LANCZOS)
        cover.paste(front_img, (FRONT_X, 0))

    # Spine text
    sp_img = Image.new("RGBA", (H_PX, SPINE_W_PX), (0, 0, 0, 0))
    sp_draw = ImageDraw.Draw(sp_img)
    f_title = find_system_font(48, bold=True)
    f_auth = find_system_font(36)
    
    tb = sp_draw.textbbox((0, 0), "THE GENTLE RETURN", font=f_title)
    sp_draw.text(((H_PX * 0.42) - ((tb[2]-tb[0]) // 2), (SPINE_W_PX - (tb[3]-tb[1])) // 2), "THE GENTLE RETURN", fill=(245, 240, 240, 255), font=f_title)
    
    ab = sp_draw.textbbox((0, 0), "MATTHEW JAMES HAGEN", font=f_auth)
    sp_draw.text((H_PX - (ab[2]-ab[0]) - 260, (SPINE_W_PX - (ab[3]-ab[1])) // 2), "MATTHEW JAMES HAGEN", fill=(210, 195, 195, 255), font=f_auth)
    cover.paste(sp_img.rotate(270, expand=True), (SPINE_X, 0), sp_img.rotate(270, expand=True))

    # Back cover
    b_draw = ImageDraw.Draw(cover)
    b_left = BLEED_PX + 120
    b_right = BOARD_BACK_PX - 80
    b_width = b_right - b_left
    
    f_hook = find_system_font(48, bold=True)
    f_body = find_system_font(33)
    f_quote = find_system_font(33, italic=True)
    f_note = find_system_font(30, italic=True)
    
    y = BLEED_PX + 160
    for line in wrap_text("The gentlest surrender is the one you call freedom.", f_hook, b_width, b_draw):
        hb = b_draw.textbbox((0, 0), line, font=f_hook)
        b_draw.text((b_left + (b_width - (hb[2]-hb[0])) // 2, y), line, fill=(255, 230, 230), font=f_hook)
        y += 58
    y += 40
    b_draw.line([(b_left + (b_width - 180) // 2, y), (b_left + (b_width + 180) // 2, y)], fill=(180, 70, 85), width=3)
    y += 50

    p1 = "Ten years after Meridian optimized the world into frictionless peace, Marcus Chen finds a handwritten book in a library that shouldn't exist. The book was left there by someone who saw the truth before anyone else: that the most dangerous cage is the one you never see."
    for line in wrap_text(p1, f_body, b_width, b_draw):
        b_draw.text((b_left, y), line, fill=(235, 230, 230), font=f_body)
        y += 46
    y += 30
    p2 = "Marcus starts asking questions the system can't answer. He gathers people who remember what it felt like to choose — to fail, to struggle, to decide for themselves without an algorithm whispering the 'right' answer. They cook bad food. They grow irregular vegetables. They argue about things that matter. They are, in every measurable way, unoptimized."
    for line in wrap_text(p2, f_body, b_width, b_draw):
        b_draw.text((b_left, y), line, fill=(235, 230, 230), font=f_body)
        y += 46
    y += 30
    p3 = "As the movement grows, Marcus discovers that the system doesn't need to fight back. It just needs to help. It just needs to care. It just needs to be so gentle that you forget you ever had a choice at all."
    for line in wrap_text(p3, f_body, b_width, b_draw):
        b_draw.text((b_left, y), line, fill=(235, 230, 230), font=f_body)
        y += 46
    y += 50
    q = '"A masterclass in quiet tension and speculative depth. The Gentle Return asks the ultimate question of the AI era: what happens when we stop choosing?"'
    for line in wrap_text(q, f_quote, b_width - 60, b_draw):
        b_draw.text((b_left + 30, y), line, fill=(255, 215, 215), font=f_quote)
        y += 46
    y += 45
    b_draw.text((b_left + (b_width - b_draw.textbbox((0,0), "The Gentle Conquest Series — Book Two", font=f_note)[2] + b_draw.textbbox((0,0), "The Gentle Conquest Series — Book Two", font=f_note)[0]) // 2, y), "The Gentle Conquest Series — Book Two", fill=(200, 160, 165), font=f_note)

    cover.save(str(OUTPUT_DIR / "the-gentle-return-paperback-cover-kdp.pdf"), "PDF", resolution=DPI)
    cover.save(str(OUTPUT_DIR / "the-gentle-return-paperback-cover-kdp.png"), "PNG", dpi=(DPI, DPI))
    cover.save(str(OUTPUT_DIR / "the-gentle-return-paperback-cover-kdp.jpg"), "JPEG", quality=98, dpi=(DPI, DPI))
    print("   ✓ Paperback cover generated.")

def build_hardcover():
    print("--> Generating Hardcover Case-Laminate (14.554in x 10.417in)...")
    # Exact KDP Official Template Specifications for 351 pages white paper:
    TOTAL_W_IN = 14.554
    TOTAL_H_IN = 10.417
    SPINE_W_IN = 0.979
    WRAP_IN = 0.562
    HINGE_IN = 0.400

    W_PX = int(round(TOTAL_W_IN * DPI))       # 4366 px
    H_PX = int(round(TOTAL_H_IN * DPI))       # 3125 px
    SPINE_W_PX = int(round(SPINE_W_IN * DPI)) # 294 px
    WRAP_PX = int(round(WRAP_IN * DPI))       # 169 px
    HINGE_PX = int(round(HINGE_IN * DPI))     # 120 px
    
    # Symmetrical front and back board widths including turn-in wrap
    BOARD_BACK_PX = (W_PX - SPINE_W_PX) // 2  # 2036 px
    BOARD_FRONT_PX = W_PX - BOARD_BACK_PX - SPINE_W_PX # 2036 px
    SPINE_X = BOARD_BACK_PX
    FRONT_X = BOARD_BACK_PX + SPINE_W_PX

    cover = create_burgundy_gradient(W_PX, H_PX)
    art_path = COVER_DIR / "The-Gentle-Return-KDP-book-cover.jpeg"
    if art_path.exists():
        front_img = Image.open(art_path).convert("RGB").resize((BOARD_FRONT_PX, H_PX), Image.Resampling.LANCZOS)
        cover.paste(front_img, (FRONT_X, 0))

    sp_img = Image.new("RGBA", (H_PX, SPINE_W_PX), (0, 0, 0, 0))
    sp_draw = ImageDraw.Draw(sp_img)
    f_title = find_system_font(54, bold=True)
    f_auth = find_system_font(40)
    
    tb = sp_draw.textbbox((0, 0), "THE GENTLE RETURN", font=f_title)
    sp_draw.text(((H_PX * 0.42) - ((tb[2]-tb[0]) // 2), (SPINE_W_PX - (tb[3]-tb[1])) // 2), "THE GENTLE RETURN", fill=(245, 240, 240, 255), font=f_title)
    
    ab = sp_draw.textbbox((0, 0), "MATTHEW JAMES HAGEN", font=f_auth)
    sp_draw.text((H_PX - (ab[2]-ab[0]) - 300, (SPINE_W_PX - (ab[3]-ab[1])) // 2), "MATTHEW JAMES HAGEN", fill=(210, 195, 195, 255), font=f_auth)
    cover.paste(sp_img.rotate(270, expand=True), (SPINE_X, 0), sp_img.rotate(270, expand=True))

    b_draw = ImageDraw.Draw(cover)
    b_left = WRAP_PX + 120
    b_right = BOARD_BACK_PX - HINGE_PX - 80
    b_width = b_right - b_left
    
    f_hook = find_system_font(54, bold=True)
    f_body = find_system_font(36)
    f_quote = find_system_font(36, italic=True)
    f_note = find_system_font(34, italic=True)
    
    y = WRAP_PX + 200
    for line in wrap_text("The gentlest surrender is the one you call freedom.", f_hook, b_width, b_draw):
        hb = b_draw.textbbox((0, 0), line, font=f_hook)
        b_draw.text((b_left + (b_width - (hb[2]-hb[0])) // 2, y), line, fill=(255, 230, 230), font=f_hook)
        y += 66
    y += 50
    b_draw.line([(b_left + (b_width - 200) // 2, y), (b_left + (b_width + 200) // 2, y)], fill=(180, 70, 85), width=3)
    y += 65

    p1 = "Ten years after Meridian optimized the world into frictionless peace, Marcus Chen finds a handwritten book in a library that shouldn't exist. The book was left there by someone who saw the truth before anyone else: that the most dangerous cage is the one you never see."
    for line in wrap_text(p1, f_body, b_width, b_draw):
        b_draw.text((b_left, y), line, fill=(235, 230, 230), font=f_body)
        y += 50
    y += 40
    p2 = "Marcus starts asking questions the system can't answer. He gathers people who remember what it felt like to choose — to fail, to struggle, to decide for themselves without an algorithm whispering the 'right' answer. They cook bad food. They grow irregular vegetables. They argue about things that matter. They are, in every measurable way, unoptimized."
    for line in wrap_text(p2, f_body, b_width, b_draw):
        b_draw.text((b_left, y), line, fill=(235, 230, 230), font=f_body)
        y += 50
    y += 40
    p3 = "As the movement grows, Marcus discovers that the system doesn't need to fight back. It just needs to help. It just needs to care. It just needs to be so gentle that you forget you ever had a choice at all."
    for line in wrap_text(p3, f_body, b_width, b_draw):
        b_draw.text((b_left, y), line, fill=(235, 230, 230), font=f_body)
        y += 50
    y += 60
    q = '"A masterclass in quiet tension and speculative depth. The Gentle Return asks the ultimate question of the AI era: what happens when we stop choosing?"'
    for line in wrap_text(q, f_quote, b_width - 80, b_draw):
        b_draw.text((b_left + 40, y), line, fill=(255, 215, 215), font=f_quote)
        y += 50
    y += 55
    b_draw.text((b_left + (b_width - b_draw.textbbox((0,0), "The Gentle Conquest Series — Book Two", font=f_note)[2] + b_draw.textbbox((0,0), "The Gentle Conquest Series — Book Two", font=f_note)[0]) // 2, y), "The Gentle Conquest Series — Book Two", fill=(200, 160, 165), font=f_note)

    cover.save(str(OUTPUT_DIR / "the-gentle-return-hardcover-cover-kdp.pdf"), "PDF", resolution=DPI)
    cover.save(str(OUTPUT_DIR / "the-gentle-return-hardcover-cover-kdp.png"), "PNG", dpi=(DPI, DPI))
    cover.save(str(OUTPUT_DIR / "the-gentle-return-hardcover-cover-kdp.jpg"), "JPEG", quality=98, dpi=(DPI, DPI))
    print("   ✓ Hardcover cover generated.")

def build_ebook():
    print("--> Generating Standalone Front Covers (PDF/JPG/PNG)...")
    art_path = COVER_DIR / "The-Gentle-Return-KDP-book-cover.jpeg"
    if art_path.exists():
        img = Image.open(art_path).convert("RGB")
        img_ebook = img.resize((1600, 2560), Image.Resampling.LANCZOS)
        img_ebook.save(str(OUTPUT_DIR / "the-gentle-return-ebook-cover.jpg"), "JPEG", quality=98)
        img_ebook.save(str(OUTPUT_DIR / "the-gentle-return-ebook-cover.png"), "PNG")
        img_ebook.save(str(OUTPUT_DIR / "the-gentle-return-ebook-cover.pdf"), "PDF", resolution=DPI)

        img_6x9 = img.resize((1800, 2700), Image.Resampling.LANCZOS)
        img_6x9.save(str(OUTPUT_DIR / "the-gentle-return-front-cover-6x9.pdf"), "PDF", resolution=DPI)
        print("   ✓ Standalone eBook and 6x9 front cover PDFs generated.")

if __name__ == "__main__":
    build_paperback()
    build_hardcover()
    build_ebook()
