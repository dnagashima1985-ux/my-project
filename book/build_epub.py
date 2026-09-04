#!/usr/bin/env python3
"""Build a Kindle-ready EPUB 3 from the Markdown chapters in book/src.

No third-party dependencies: implements the small Markdown subset the
manuscript actually uses (headings, paragraphs, lists, blockquotes, tables,
horizontal rules, bold/italic) and packages the result as EPUB 3.
"""

import html
import os
import re
import uuid
import zipfile
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "src")
OUT = os.path.join(HERE, "build")

TITLE = "才能を見落とさない七つの関門"
SUBTITLE = "育成年代スカウティングの設計図"
AUTHOR = "フットボールパラダイム"
LANG = "ja"

FILES = [
    ("00-hajimeni.md", "はじめに"),
    ("01-jyoshou.md", "序章 才能は、こぼれている"),
    ("02-gate1-sonzai.md", "第1関門 存在"),
    ("03-gate2-kashi.md", "第2関門 可視"),
    ("04-gate3-shikibetsu.md", "第3関門 識別"),
    ("05-gate4-kiroku.md", "第4関門 記録"),
    ("06-gate5-goui.md", "第5関門 合意"),
    ("07-gate6-jikan.md", "第6関門 時間"),
    ("08-gate7-kaiki.md", "第7関門 回帰"),
    ("09-audit.md", "第8章 監査"),
    ("10-90days.md", "第9章 90日"),
    ("11-shushou.md", "終章 選手である前に、子どもである"),
    ("12-appendix.md", "付録・出典"),
]

CSS = """\
html { -epub-writing-mode: horizontal-tb; }
body { margin: 0 4%; line-height: 1.8; font-size: 1em; }
h1 { font-size: 1.5em; line-height: 1.4; margin: 2em 0 1.2em; page-break-before: always;
     border-bottom: 3px solid #333; padding-bottom: .4em; }
h2 { font-size: 1.2em; line-height: 1.5; margin: 2em 0 .8em; border-left: 6px solid #333;
     padding-left: .5em; }
h3 { font-size: 1.05em; margin: 1.6em 0 .6em; }
p  { margin: 0 0 1em; text-indent: 0; }
ul, ol { margin: 0 0 1.2em; padding-left: 1.4em; }
li { margin-bottom: .4em; }
blockquote { margin: 1.2em 0; padding: .8em 1em; border-left: 4px solid #888;
             background: #f2f2f2; }
blockquote p { margin: 0; }
hr { border: 0; border-top: 1px solid #bbb; margin: 2em 0; }
table { border-collapse: collapse; width: 100%; margin: 1.2em 0; font-size: .9em; }
th, td { border: 1px solid #999; padding: .4em .5em; text-align: left; vertical-align: top; }
th { background: #eee; }
strong { font-weight: bold; }
.titlepage { text-align: center; margin-top: 25%; }
.titlepage h1 { border: 0; page-break-before: auto; font-size: 2em; }
.titlepage .sub { font-size: 1em; margin-top: 1.5em; line-height: 1.7; }
.titlepage .author { margin-top: 3em; font-size: 1.1em; }
"""


def inline(text):
    text = html.escape(text, quote=False)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*\n]+?)\*(?!\*)", r"<em>\1</em>", text)
    return text


def is_table_sep(line):
    return bool(re.match(r"^\|[\s:|-]+\|$", line.strip()))


def md_to_xhtml(md):
    lines = md.split("\n")
    out = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        if stripped == "---":
            out.append("<hr/>")
            i += 1
            continue

        m = re.match(r"^(#{1,4})\s+(.*)$", stripped)
        if m:
            level = len(m.group(1))
            out.append("<h%d>%s</h%d>" % (level, inline(m.group(2)), level))
            i += 1
            continue

        # table
        if stripped.startswith("|") and i + 1 < n and is_table_sep(lines[i + 1]):
            header = [c.strip() for c in stripped.strip("|").split("|")]
            i += 2
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            out.append("<table>")
            out.append("<thead><tr>" + "".join(
                "<th>%s</th>" % inline(c) for c in header) + "</tr></thead>")
            out.append("<tbody>")
            for r in rows:
                r = (r + [""] * len(header))[:len(header)]
                out.append("<tr>" + "".join("<td>%s</td>" % inline(c) for c in r) + "</tr>")
            out.append("</tbody></table>")
            continue

        # blockquote
        if stripped.startswith(">"):
            buf = []
            while i < n and lines[i].strip().startswith(">"):
                buf.append(lines[i].strip().lstrip(">").strip())
                i += 1
            out.append("<blockquote><p>%s</p></blockquote>" % inline(" ".join(buf)))
            continue

        # unordered list
        if re.match(r"^[-*]\s+", stripped):
            out.append("<ul>")
            while i < n and re.match(r"^[-*]\s+", lines[i].strip()):
                out.append("<li>%s</li>" % inline(re.sub(r"^[-*]\s+", "", lines[i].strip())))
                i += 1
            out.append("</ul>")
            continue

        # ordered list
        if re.match(r"^\d+\.\s+", stripped):
            out.append("<ol>")
            while i < n and re.match(r"^\d+\.\s+", lines[i].strip()):
                out.append("<li>%s</li>" % inline(re.sub(r"^\d+\.\s+", "", lines[i].strip())))
                i += 1
            out.append("</ol>")
            continue

        # paragraph
        buf = []
        while i < n and lines[i].strip() and not re.match(
                r"^(#{1,4}\s|[-*]\s|\d+\.\s|>|\|)", lines[i].strip()) and lines[i].strip() != "---":
            buf.append(lines[i].strip())
            i += 1
        out.append("<p>%s</p>" % inline("".join(buf)))

    return "\n".join(out)


def page(title, body):
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" '
        'xml:lang="%s" lang="%s">\n<head>\n<meta charset="utf-8"/>\n'
        '<title>%s</title>\n<link rel="stylesheet" type="text/css" href="style.css"/>\n'
        '</head>\n<body>\n%s\n</body>\n</html>\n'
        % (LANG, LANG, html.escape(title), body)
    )


def build():
    os.makedirs(OUT, exist_ok=True)
    book_id = "urn:uuid:" + str(uuid.uuid5(uuid.NAMESPACE_DNS, "nanatsu-no-kanmon"))
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    chapters = []
    total_chars = 0
    for fname, nav_title in FILES:
        md = open(os.path.join(SRC, fname), encoding="utf-8").read()
        total_chars += len(re.sub(r"\s", "", md))
        chapters.append((fname.replace(".md", ".xhtml"), nav_title, md_to_xhtml(md)))

    title_body = (
        '<div class="titlepage">\n<h1>%s</h1>\n<p class="sub">%s</p>\n'
        '<p class="author">%s</p>\n</div>\n' % (
            html.escape(TITLE), html.escape(SUBTITLE), html.escape(AUTHOR))
    )

    nav_items = "\n".join(
        '      <li><a href="%s">%s</a></li>' % (fn, html.escape(t))
        for fn, t, _ in chapters)
    nav_body = (
        '<nav epub:type="toc" id="toc">\n<h1>目次</h1>\n<ol>\n%s\n</ol>\n</nav>\n' % nav_items)

    manifest = ['<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" '
                'properties="nav"/>',
                '<item id="css" href="style.css" media-type="text/css"/>',
                '<item id="title" href="title.xhtml" media-type="application/xhtml+xml"/>']
    spine = ['<itemref idref="title"/>', '<itemref idref="nav"/>']
    for idx, (fn, _t, _b) in enumerate(chapters):
        manifest.append('<item id="c%d" href="%s" media-type="application/xhtml+xml"/>'
                        % (idx, fn))
        spine.append('<itemref idref="c%d"/>' % idx)

    opf = (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid">\n'
        '  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">\n'
        '    <dc:identifier id="bookid">%s</dc:identifier>\n'
        '    <dc:title>%s</dc:title>\n'
        '    <dc:creator>%s</dc:creator>\n'
        '    <dc:language>%s</dc:language>\n'
        '    <dc:description>%s</dc:description>\n'
        '    <meta property="dcterms:modified">%s</meta>\n'
        '  </metadata>\n'
        '  <manifest>\n    %s\n  </manifest>\n'
        '  <spine>\n    %s\n  </spine>\n'
        '</package>\n' % (book_id, html.escape(TITLE), html.escape(AUTHOR), LANG,
                          html.escape(SUBTITLE), now,
                          "\n    ".join(manifest), "\n    ".join(spine))
    )

    container = (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">\n'
        '  <rootfiles>\n'
        '    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>\n'
        '  </rootfiles>\n</container>\n'
    )

    epub_path = os.path.join(OUT, "nanatsu-no-kanmon.epub")
    with zipfile.ZipFile(epub_path, "w") as z:
        z.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        z.writestr("META-INF/container.xml", container, zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/content.opf", opf, zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/style.css", CSS, zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/title.xhtml", page(TITLE, title_body), zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/nav.xhtml", page("目次", nav_body), zipfile.ZIP_DEFLATED)
        for fn, t, body in chapters:
            z.writestr("OEBPS/" + fn, page(t, body), zipfile.ZIP_DEFLATED)

    # single-file markdown for editing / Word import
    combined = os.path.join(OUT, "nanatsu-no-kanmon.md")
    with open(combined, "w", encoding="utf-8") as f:
        f.write("# %s\n\n## %s\n\n---\n\n" % (TITLE, SUBTITLE))
        for fname, _t in FILES:
            f.write(open(os.path.join(SRC, fname), encoding="utf-8").read().rstrip() + "\n\n")

    print("EPUB : %s (%.1f KB)" % (epub_path, os.path.getsize(epub_path) / 1024))
    print("MD   : %s" % combined)
    print("本文文字数（空白除く）: %d 字" % total_chars)


if __name__ == "__main__":
    build()
