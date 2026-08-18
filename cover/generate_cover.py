#!/usr/bin/env python3
"""Generate KDP ebook cover for The Gentle Return - red theme."""
from PIL import Image, ImageDraw, ImageFont
import math

WIDTH = 1600
HEIGHT = 2560

img = Image.new('RGB', (WIDTH, HEIGHT))
draw = ImageDraw.Draw(img)

# --- Background: dark red gradient with radial glow ---
for y in range(HEIGHT):
    t = y / HEIGHT
    r = int(140 * (1 - t) + 15 * t)
    g = int(15 * (1 - t) + 5 * t)
    b = int(30 * (1 - t) + 10 * t)
    draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

# Radial glow overlay
glow = Image.new('RGB', (WIDTH, HEIGHT), (0, 0, 0))
glow_draw = ImageDraw.Draw(glow)
cx, cy = WIDTH // 2, int(HEIGHT * 0.38)
max_r = 900
for i in range(max_r, 0, -3):
    alpha = int(55 * (1 - i / max_r))
    glow_draw.ellipse(
        [cx - i, cy - i, cx + i, cy + i],
        fill=(alpha, int(alpha * 0.15), int(alpha * 0.25))
    )
img = Image.blend(img, glow, 0.5)
draw = ImageDraw.Draw(img)

# --- Decorative lines ---
line_y_top = 750
line_y_bottom = 1850
line_color = (180, 40, 50)
line_width = 2
margin = 200

draw.line([(margin, line_y_top), (WIDTH - margin, line_y_top)], fill=line_color, width=line_width)
draw.line([(margin, line_y_bottom), (WIDTH - margin, line_y_bottom)], fill=line_color, width=line_width)

# Small diamond decorations on lines
for lx in [margin + 40, WIDTH - margin - 40]:
    for ly in [line_y_top, line_y_bottom]:
        sz = 6
        draw.polygon([(lx, ly - sz), (lx + sz, ly), (lx, ly + sz), (lx - sz, ly)], fill=line_color)

# --- Fonts ---
def get_font(size, bold=False):
    paths = [
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
        '/usr/share/fonts/truetype/freefont/FreeSansBold.ttf' if bold else '/usr/share/fonts/truetype/freefont/FreeSans.ttf',
    ]
    for p in paths:
        try:
            return ImageFont.truetype(p, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()

# --- Title: "THE GENTLE RETURN" ---
title_font = get_font(130, bold=True)
subtitle_font = get_font(48, bold=False)
author_font = get_font(56, bold=True)
by_font = get_font(36, bold=False)

title_lines = ["THE GENTLE", "RETURN"]
title_color = (255, 255, 255)

# Draw title centered
title_y = 850
for line in title_lines:
    bbox = draw.textbbox((0, 0), line, font=title_font)
    tw = bbox[2] - bbox[0]
    x = (WIDTH - tw) // 2
    # Subtle shadow
    draw.text((x + 3, title_y + 3), line, font=title_font, fill=(60, 10, 15))
    draw.text((x, title_y), line, font=title_font, fill=title_color)
    title_y += 160

# --- "A Novel" subtitle ---
novel_text = "A Novel"
bbox = draw.textbbox((0, 0), novel_text, font=subtitle_font)
nw = bbox[2] - bbox[0]
nx = (WIDTH - nw) // 2
novel_y = title_y + 30
draw.text((nx, novel_y), novel_text, font=subtitle_font, fill=(200, 160, 165))

# --- Epigraph ---
epi_font = get_font(34, bold=False)
epi_text = '"The return is not the opposite of the journey.'
epi_text2 = 'It is the journey\'s completion."'
bbox1 = draw.textbbox((0, 0), epi_text, font=epi_font)
bbox2 = draw.textbbox((0, 0), epi_text2, font=epi_font)
epi_y = novel_y + 100
draw.text(((WIDTH - (bbox1[2] - bbox1[0])) // 2, epi_y), epi_text, font=epi_font, fill=(170, 130, 135))
draw.text(((WIDTH - (bbox2[2] - bbox2[0])) // 2, epi_y + 50), epi_text2, font=epi_font, fill=(170, 130, 135))

# --- Author name at bottom ---
author_name = "MATTHEW JAMES HAGEN"
bbox = draw.textbbox((0, 0), author_name, font=author_font)
aw = bbox[2] - bbox[0]
ax = (WIDTH - aw) // 2
author_y = HEIGHT - 280
draw.text((ax + 2, author_y + 2), author_name, font=author_font, fill=(60, 10, 15))
draw.text((ax, author_y), author_name, font=author_font, fill=(255, 255, 255))

# --- "A Gentle Conquest Novel" series tag ---
series_font = get_font(30, bold=False)
series_text = "A Gentle Conquest Novel"
bbox = draw.textbbox((0, 0), series_text, font=series_font)
sw = bbox[2] - bbox[0]
sx = (WIDTH - sw) // 2
series_y = author_y + 80
draw.text((sx, series_y), series_text, font=series_font, fill=(170, 130, 135))

# --- Thin separator line above author ---
sep_y = author_y - 40
draw.line([(margin + 200, sep_y), (WIDTH - margin - 200, sep_y)], fill=line_color, width=1)

# --- Save ---
out_path = '/tmp/The-Gentle-Return/cover/cover-ebook-red.png'
img.save(out_path, 'PNG', dpi=(300, 300))
print(f"Saved: {out_path}")

# Also save a JPEG version
jpg_path = '/tmp/The-Gentle-Return/cover/cover-ebook-red.jpg'
img.save(jpg_path, 'JPEG', quality=95, dpi=(300, 300))
print(f"Saved: {jpg_path}")
