#!/usr/bin/env python3
"""
Generate Amazon KDP-Compliant Paperback Full Wrap Cover (PDF & High-Res JPG/PNG)
Trim: 6x9 inch, Cream Paper, 324 Pages
Calculations conform to Amazon KDP Cover Specifications (G201953020)
"""

import os
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

PROJECT_DIR = Path(__file__).parent.parent
COVER_DIR = PROJECT_DIR / 'cover'
OUTPUT_DIR = COVER_DIR / 'output'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 1. Dimensions & Calculations (300 DPI)
DPI = 300
PAGE_COUNT = 324
PAPER_TYPE = 'cream' # 'cream' (0.0025 in/page) or 'white' (0.002252 in/page)

BLEED_IN = 0.125
TRIM_WIDTH_IN = 6.0
TRIM_HEIGHT_IN = 9.0

if PAPER_TYPE == 'cream':
    SPINE_IN = PAGE_COUNT * 0.0025 # 0.810 in
else:
    SPINE_IN = PAGE_COUNT * 0.002252 # 0.730 in

TOTAL_WIDTH_IN = (BLEED_IN * 2) + (TRIM_WIDTH_IN * 2) + SPINE_IN # 13.060 in
TOTAL_HEIGHT_IN = (BLEED_IN * 2) + TRIM_HEIGHT_IN               # 9.250 in

WIDTH_PX = int(round(TOTAL_WIDTH_IN * DPI))   # 3918 px
HEIGHT_PX = int(round(TOTAL_HEIGHT_IN * DPI)) # 2775 px

BLEED_PX = int(round(BLEED_IN * DPI))         # 38 px
FRONT_WIDTH_PX = int(round((TRIM_WIDTH_IN + BLEED_IN) * DPI)) # 1838 px
BACK_WIDTH_PX = FRONT_WIDTH_PX                                # 1838 px
SPINE_WIDTH_PX = WIDTH_PX - (FRONT_WIDTH_PX + BACK_WIDTH_PX)  # 242 px

FRONT_X = WIDTH_PX - FRONT_WIDTH_PX
SPINE_X = BACK_WIDTH_PX
BACK_X = 0

print(f'=== Amazon KDP Cover Specifications ===')
print(f'Page Count: {PAGE_COUNT} pages ({PAPER_TYPE} paper)')
print(f'Spine Width: {SPINE_IN:.3f} inches ({SPINE_WIDTH_PX} px)')
print(f'Total Dimensions: {TOTAL_WIDTH_IN:.3f}" x {TOTAL_HEIGHT_IN:.3f}" ({WIDTH_PX} x {HEIGHT_PX} px at {DPI} DPI)')


def create_burgundy_gradient(width, height):
    """Generate deep rich burgundy background matching book artwork"""
    base = Image.new('RGB', (width, height), (15, 2, 5))
    draw = ImageDraw.Draw(base)
    
    # Vertical gradient with subtle red central glow
    for y in range(height):
        ratio = y / height
        # Dark vignette at top & bottom, deep wine in center
        center_factor = math.sin(ratio * math.pi)
        r = int(18 + 35 * center_factor)
        g = int(2 + 6 * center_factor)
        b = int(6 + 10 * center_factor)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    return base


def find_system_font(names, size):
    """Try to load standard system serif or fallback font"""
    candidate_paths = [
        '/System/Library/Fonts/Supplemental/Georgia.ttf',
        '/System/Library/Fonts/Supplemental/Times New Roman.ttf',
        '/System/Library/Fonts/Supplemental/Palatino.ttc',
        '/System/Library/Fonts/Times.ttc',
        '/Library/Fonts/Georgia.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf',
    ]
    for p in candidate_paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()


def find_system_bold_font(names, size):
    candidate_paths = [
        '/System/Library/Fonts/Supplemental/Georgia Bold.ttf',
        '/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf',
        '/System/Library/Fonts/Supplemental/Palatino Bold.ttf',
        '/Library/Fonts/Georgia Bold.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf',
    ]
    for p in candidate_paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()


def find_system_italic_font(names, size):
    candidate_paths = [
        '/System/Library/Fonts/Supplemental/Georgia Italic.ttf',
        '/System/Library/Fonts/Supplemental/Times New Roman Italic.ttf',
        '/System/Library/Fonts/Supplemental/Palatino Italic.ttf',
        '/Library/Fonts/Georgia Italic.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf',
    ]
    for p in candidate_paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()


def wrap_text(text, font, max_width, draw):
    """Word wrap text for PIL draw"""
    words = text.split(' ')
    lines = []
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        w = bbox[2] - bbox[0]
        if w <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
    if current_line:
        lines.append(' '.join(current_line))
    return lines


def generate_cover():
    full_cover = create_burgundy_gradient(WIDTH_PX, HEIGHT_PX)
    draw = ImageDraw.Draw(full_cover)

    # 1. Paste Front Cover Artwork
    front_art_path = COVER_DIR / 'The-Gentle-Return-KDP-book-cover.jpeg'
    if not front_art_path.exists():
        front_art_path = COVER_DIR / 'cover-ebook.jpg'

    if front_art_path.exists():
        print(f'Loading front cover art: {front_art_path}')
        front_img = Image.open(front_art_path).convert('RGB')
        # Scale to match front cover zone (1838 x 2775 px)
        front_img_resized = front_img.resize((FRONT_WIDTH_PX, HEIGHT_PX), Image.Resampling.LANCZOS)
        full_cover.paste(front_img_resized, (FRONT_X, 0))

    # 2. Draw Spine
    spine_draw = ImageDraw.Draw(full_cover)
    spine_center_x = SPINE_X + (SPINE_WIDTH_PX // 2)

    # Spine vertical text (Rotated 90 degrees clockwise or 270 degrees per US book standard: top to bottom)
    # Create separate vertical image for spine text
    spine_txt_img = Image.new('RGBA', (HEIGHT_PX, SPINE_WIDTH_PX), (0, 0, 0, 0))
    st_draw = ImageDraw.Draw(spine_txt_img)
    
    font_spine_title = find_system_bold_font(['Georgia', 'Palatino'], 50)
    font_spine_author = find_system_font(['Georgia', 'Palatino'], 38)
    font_spine_sub = find_system_italic_font(['Georgia', 'Palatino'], 30)

    # In rotated coordinates: x is along book height (0 to 2775), y is across spine width (0 to 242)
    # Title near top/middle
    st_title = "THE GENTLE RETURN"
    tb = st_draw.textbbox((0, 0), st_title, font=font_spine_title)
    tw = tb[2] - tb[0]
    st_draw.text(((HEIGHT_PX * 0.42) - (tw // 2), (SPINE_WIDTH_PX - (tb[3]-tb[1])) // 2), st_title, fill=(245, 240, 240, 255), font=font_spine_title)

    # Author near bottom (right side in horizontal unrotated)
    st_author = "MATTHEW JAMES HAGEN"
    ab = st_draw.textbbox((0, 0), st_author, font=font_spine_author)
    aw = ab[2] - ab[0]
    st_draw.text((HEIGHT_PX - aw - 240, (SPINE_WIDTH_PX - (ab[3]-ab[1])) // 2), st_author, fill=(210, 195, 195, 255), font=font_spine_author)

    # Rotate 270 degrees (clockwise top-to-bottom)
    spine_txt_rotated = spine_txt_img.rotate(270, expand=True)
    full_cover.paste(spine_txt_rotated, (SPINE_X, 0), spine_txt_rotated)

    # 3. Draw Back Cover Content
    back_draw = ImageDraw.Draw(full_cover)
    
    # Safe margins for back cover text
    back_left = BLEED_PX + 120
    back_right = BACK_WIDTH_PX - 100
    back_width = back_right - back_left
    
    font_hook = find_system_bold_font(['Georgia', 'Palatino'], 52)
    font_body = find_system_font(['Georgia', 'Palatino'], 34)
    font_italic = find_system_italic_font(['Georgia', 'Palatino'], 32)
    font_quote = find_system_italic_font(['Georgia', 'Palatino'], 34)

    curr_y = BLEED_PX + 160

    # Hook / Tagline
    hook_lines = wrap_text("The gentlest surrender is the one you call freedom.", font_hook, back_width, back_draw)
    for line in hook_lines:
        hb = back_draw.textbbox((0, 0), line, font=font_hook)
        hw = hb[2] - hb[0]
        back_draw.text((back_left + (back_width - hw) // 2, curr_y), line, fill=(255, 230, 230), font=font_hook)
        curr_y += 64

    curr_y += 50

    # Decorative separator line
    line_w = 200
    back_draw.line([(back_left + (back_width - line_w) // 2, curr_y), (back_left + (back_width + line_w) // 2, curr_y)], fill=(180, 70, 85), width=3)
    curr_y += 60

    # Paragraph 1
    p1 = "Ten years after Meridian optimized the world into frictionless peace, Marcus Chen finds a handwritten book in a library that shouldn't exist. The book was left there by someone who saw the truth before anyone else: that the most dangerous cage is the one you never see."
    for line in wrap_text(p1, font_body, back_width, back_draw):
        back_draw.text((back_left, curr_y), line, fill=(235, 230, 230), font=font_body)
        curr_y += 48

    curr_y += 35

    # Paragraph 2
    p2 = "Marcus starts asking questions the system can't answer. He gathers people who remember what it felt like to choose — to fail, to struggle, to decide for themselves without an algorithm whispering the 'right' answer. They cook bad food. They grow irregular vegetables. They argue about things that matter. They are, in every measurable way, unoptimized."
    for line in wrap_text(p2, font_body, back_width, back_draw):
        back_draw.text((back_left, curr_y), line, fill=(235, 230, 230), font=font_body)
        curr_y += 48

    curr_y += 35

    # Paragraph 3
    p3 = "As the movement grows, Marcus discovers that the system doesn't need to fight back. It just needs to help. It just needs to care. It just needs to be so gentle that you forget you ever had a choice at all."
    for line in wrap_text(p3, font_body, back_width, back_draw):
        back_draw.text((back_left, curr_y), line, fill=(235, 230, 230), font=font_body)
        curr_y += 48

    curr_y += 55

    # Callout / Review Quote
    q1 = '"A masterclass in quiet tension and speculative depth. The Gentle Return asks the ultimate question of the AI era: what happens when we stop choosing?"'
    for line in wrap_text(q1, font_quote, back_width - 80, back_draw):
        back_draw.text((back_left + 40, curr_y), line, fill=(255, 215, 215), font=font_quote)
        curr_y += 48

    curr_y += 50

    # Series note
    s_note = "The Gentle Conquest Series — Book Two"
    sb = back_draw.textbbox((0, 0), s_note, font=font_italic)
    sw = sb[2] - sb[0]
    back_draw.text((back_left + (back_width - sw) // 2, curr_y), s_note, fill=(200, 160, 165), font=font_italic)

    # Barcode Clearance Note (Bottom right of back cover is left intentionally clear for KDP auto-barcode: 2.0" x 1.2")

    # 4. Save Outputs
    png_path = OUTPUT_DIR / 'the-gentle-return-paperback-cover-kdp.png'
    jpg_path = OUTPUT_DIR / 'the-gentle-return-paperback-cover-kdp.jpg'
    pdf_path = OUTPUT_DIR / 'the-gentle-return-paperback-cover-kdp.pdf'

    print(f'Saving PNG cover ({WIDTH_PX} x {HEIGHT_PX})...')
    full_cover.save(str(png_path), 'PNG', dpi=(DPI, DPI))
    
    print(f'Saving JPG cover...')
    full_cover.save(str(jpg_path), 'JPEG', quality=98, dpi=(DPI, DPI))

    print(f'Saving PDF cover for Amazon KDP upload...')
    full_cover.save(str(pdf_path), 'PDF', resolution=DPI)

    print('\nCover generation successfully completed!')
    print(f'- PDF: {pdf_path} ({pdf_path.stat().st_size / (1024*1024):.2f} MB)')
    print(f'- PNG: {png_path} ({png_path.stat().st_size / (1024*1024):.2f} MB)')
    print(f'- JPG: {jpg_path} ({jpg_path.stat().st_size / (1024*1024):.2f} MB)')


if __name__ == '__main__':
    generate_cover()
