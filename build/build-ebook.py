#!/usr/bin/env python3
import os
import re
import zipfile
import shutil
from pathlib import Path
import markdown

PROJECT_DIR = Path(__file__).parent.parent
MANUSCRIPT_DIR = PROJECT_DIR / 'manuscript'
CHAPTERS_DIR = MANUSCRIPT_DIR / 'chapters'
COVER_DIR = PROJECT_DIR / 'cover'
OUTPUT_DIR = PROJECT_DIR / 'build' / 'output'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

BOOK_TITLE = "The Gentle Return"
BOOK_SUBTITLE = "A Novel"
BOOK_AUTHOR = "Matthew James Hagen"
BOOK_IDENTIFIER = "urn:uuid:gentle-return-2026-v2"
BOOK_LANGUAGE = "en-US"
BOOK_DESCRIPTION = "The Return Begins where the Comfort Ends. Ten years after Meridian optimized the world into frictionless peace, Marcus Chen finds a handwritten book in a library that should not exist."

def convert_md_to_html(md_text):
    html = markdown.markdown(md_text, extensions=['extra', 'smarty'])
    html = re.sub(r'<hr\s*/?>', '<div class="scene-break">* &nbsp; * &nbsp; *</div>', html)
    return html

def build_standalone_html():
    html_out = OUTPUT_DIR / 'the-gentle-return-interior.html'
    print(f'Building Standalone HTML: {html_out}')
    css_path = PROJECT_DIR / 'build' / 'style.css'
    css_content = css_path.read_text(encoding='utf-8') if css_path.exists() else ''
    sections_html = []

    front_file = MANUSCRIPT_DIR / 'front-matter.md'
    if front_file.exists():
        sections_html.append(f'<section class="front-matter">' + convert_md_to_html(front_file.read_text(encoding='utf-8')) + '</section>')

    for ch_path in sorted(CHAPTERS_DIR.glob('*.md')):
        sections_html.append(f'<section class="chapter">' + convert_md_to_html(ch_path.read_text(encoding='utf-8')) + '</section>')

    back_file = MANUSCRIPT_DIR / 'back-matter.md'
    if back_file.exists():
        sections_html.append(f'<section class="back-matter">' + convert_md_to_html(back_file.read_text(encoding='utf-8')) + '</section>')

    sep = "\n<div class=\"page-break\"></div>\n"
    body_content = sep.join(sections_html)
    full_page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{BOOK_TITLE} — {BOOK_AUTHOR}</title>
<style>
{css_content}
.scene-break {{
    text-align: center;
    margin: 1.8em 0;
    color: #555;
    letter-spacing: 0.3em;
    font-size: 0.9em;
}}
</style>
</head>
<body>
{body_content}
</body>
</html>"""
    html_out.write_text(full_page, encoding='utf-8')
    print(f'Successfully generated HTML: {html_out}')

def build_epub():
    epub_out = OUTPUT_DIR / 'the-gentle-return.epub'
    print(f'Building EPUB: {epub_out}')
    temp_dir = OUTPUT_DIR / '_epub_temp'
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir(parents=True)
    
    meta_inf = temp_dir / 'META-INF'
    meta_inf.mkdir()
    oebps = temp_dir / 'OEBPS'
    oebps.mkdir()

    (temp_dir / 'mimetype').write_text('application/epub+zip', encoding='ascii')

    container_xml = '<?xml version="1.0" encoding="UTF-8"?><container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>'
    (meta_inf / 'container.xml').write_text(container_xml, encoding='utf-8')

    css_content = 'body { font-family: Georgia, serif; font-size: 1em; line-height: 1.45; margin: 5%; text-align: justify; } h1 { font-size: 1.6em; text-align: center; margin-top: 1.5em; margin-bottom: 1em; page-break-before: always; } h2 { font-size: 1.2em; text-align: center; margin-top: 1.2em; margin-bottom: 0.8em; } p { text-indent: 1.5em; margin: 0; } h1 + p, h2 + p, h3 + p, .no-indent, .scene-break + p { text-indent: 0; } .scene-break { text-align: center; margin: 1.5em 0; color: #666; letter-spacing: 0.3em; } .cover-img { width: 100%; height: auto; max-width: 100%; }'
    (oebps / 'style.css').write_text(css_content, encoding='utf-8')

    has_cover = False
    cover_src = COVER_DIR / 'The-Gentle-Return-KDP-book-cover.jpeg'
    if not cover_src.exists():
        cover_src = COVER_DIR / 'cover-ebook.jpg'
    if cover_src.exists():
        shutil.copy(cover_src, oebps / 'cover.jpg')
        has_cover = True

    items = []
    itemrefs = []

    if has_cover:
        cover_xhtml = '<?xml version="1.0" encoding="utf-8"?><!DOCTYPE html><html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops"><head><title>Cover</title><link rel="stylesheet" type="text/css" href="style.css"/></head><body style="margin:0;padding:0;text-align:center;"><img src="cover.jpg" alt="Book Cover" class="cover-img" style="max-height:100vh;"/></body></html>'
        (oebps / 'cover.xhtml').write_text(cover_xhtml, encoding='utf-8')
        items.append(('cover-page', 'cover.xhtml', 'application/xhtml+xml', 'Cover'))
        itemrefs.append('cover-page')

    front_file = MANUSCRIPT_DIR / 'front-matter.md'
    if front_file.exists():
        f_html = convert_md_to_html(front_file.read_text(encoding='utf-8'))
        f_xhtml = '<?xml version="1.0" encoding="utf-8"?><!DOCTYPE html><html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops"><head><title>Front Matter</title><link rel="stylesheet" type="text/css" href="style.css"/></head><body>' + f_html + '</body></html>'
        (oebps / 'frontmatter.xhtml').write_text(f_xhtml, encoding='utf-8')
        items.append(('frontmatter', 'frontmatter.xhtml', 'application/xhtml+xml', 'Front Matter'))
        itemrefs.append('frontmatter')

    for i, ch_path in enumerate(sorted(CHAPTERS_DIR.glob('*.md'))):
        ch_text = ch_path.read_text(encoding='utf-8')
        ch_first_line = ch_text.splitlines()[0].replace('#', '').strip() if ch_text.splitlines() else f'Chapter {i+1}'
        ch_html = convert_md_to_html(ch_text)
        fname = f'chapter_{i:02d}.xhtml'
        cid = f'chapter_{i:02d}'
        
        c_xhtml = '<?xml version="1.0" encoding="utf-8"?><!DOCTYPE html><html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops"><head><title>' + ch_first_line + '</title><link rel="stylesheet" type="text/css" href="style.css"/></head><body>' + ch_html + '</body></html>'
        (oebps / fname).write_text(c_xhtml, encoding='utf-8')
        items.append((cid, fname, 'application/xhtml+xml', ch_first_line))
        itemrefs.append(cid)

    back_file = MANUSCRIPT_DIR / 'back-matter.md'
    if back_file.exists():
        b_html = convert_md_to_html(back_file.read_text(encoding='utf-8'))
        b_xhtml = '<?xml version="1.0" encoding="utf-8"?><!DOCTYPE html><html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops"><head><title>Back Matter</title><link rel="stylesheet" type="text/css" href="style.css"/></head><body>' + b_html + '</body></html>'
        (oebps / 'backmatter.xhtml').write_text(b_xhtml, encoding='utf-8')
        items.append(('backmatter', 'backmatter.xhtml', 'application/xhtml+xml', 'Back Matter'))
        itemrefs.append('backmatter')

    navpoints = []
    play_order = 1
    nl = "\n"
    for item in items:
        cid, fname, mtype, title = item
        if mtype == 'application/xhtml+xml':
            navpoints.append(f'<navPoint id="navPoint-{play_order}" playOrder="{play_order}"><navLabel><text>{title}</text></navLabel><content src="{fname}"/></navPoint>')
            play_order += 1

    toc_ncx = '<?xml version="1.0" encoding="UTF-8"?><ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1"><head><meta name="dtb:uid" content="' + BOOK_IDENTIFIER + '"/><meta name="dtb:depth" content="1"/><meta name="dtb:totalPageCount" content="0"/><meta name="dtb:maxPageNumber" content="0"/></head><docTitle><text>' + BOOK_TITLE + '</text></docTitle><navMap>' + nl.join(navpoints) + '</navMap></ncx>'
    (oebps / 'toc.ncx').write_text(toc_ncx, encoding='utf-8')

    nav_links = []
    for item in items:
        cid, fname, mtype, title = item
        if mtype == 'application/xhtml+xml' and cid != 'cover-page':
            nav_links.append(f'<li><a href="{fname}">{title}</a></li>')

    nav_xhtml = '<?xml version="1.0" encoding="utf-8"?><!DOCTYPE html><html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops"><head><title>Table of Contents</title><link rel="stylesheet" type="text/css" href="style.css"/></head><body><nav epub:type="toc" id="toc"><h1>Table of Contents</h1><ol>' + nl.join(nav_links) + '</ol></nav></body></html>'
    (oebps / 'nav.xhtml').write_text(nav_xhtml, encoding='utf-8')

    manifest_entries = [
        '<item id="style" href="style.css" media-type="text/css"/>',
        '<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>',
        '<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>'
    ]
    if has_cover:
        manifest_entries.append('<item id="cover-image" href="cover.jpg" media-type="image/jpeg" properties="cover-image"/>')

    for item in items:
        cid, fname, mtype, title = item
        manifest_entries.append(f'<item id="{cid}" href="{fname}" media-type="{mtype}"/>')

    spine_entries = ['<itemref idref="nav"/>']
    for idref in itemrefs:
        spine_entries.append(f'<itemref idref="{idref}"/>')

    content_opf = '<?xml version="1.0" encoding="UTF-8"?><package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="BookId"><metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf"><dc:identifier id="BookId">' + BOOK_IDENTIFIER + '</dc:identifier><dc:title>' + BOOK_TITLE + '</dc:title><dc:creator>' + BOOK_AUTHOR + '</dc:creator><dc:language>' + BOOK_LANGUAGE + '</dc:language><dc:description>' + BOOK_DESCRIPTION + '</dc:description><dc:publisher>Independent</dc:publisher><dc:rights>© 2026 Matthew James Hagen. All rights reserved.</dc:rights><meta property="dcterms:modified">2026-08-18T12:00:00Z</meta></metadata><manifest>' + nl.join(manifest_entries) + '</manifest><spine toc="ncx">' + nl.join(spine_entries) + '</spine></package>'
    (oebps / 'content.opf').write_text(content_opf, encoding='utf-8')

    with zipfile.ZipFile(epub_out, 'w') as z:
        z.write(temp_dir / 'mimetype', 'mimetype', compress_type=zipfile.ZIP_STORED)
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                full_path = Path(root) / file
                rel_path = full_path.relative_to(temp_dir)
                if str(rel_path) == 'mimetype':
                    continue
                z.write(full_path, str(rel_path), compress_type=zipfile.ZIP_DEFLATED)

    shutil.rmtree(temp_dir)
    file_size_mb = epub_out.stat().st_size / (1024 * 1024)
    print(f'Successfully generated EPUB: {epub_out} ({file_size_mb:.2f} MB)')

if __name__ == '__main__':
    build_standalone_html()
    build_epub()
