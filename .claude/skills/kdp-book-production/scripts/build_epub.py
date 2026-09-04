#!/usr/bin/env python3
"""Build a KDP-ready EPUB 3 from Markdown chapters, driven by book.json.

Usage:  python3 build_epub.py [book.json]

Expects the config next to a src/ directory of Markdown chapters. Writes
build/<slug>.epub plus build/<slug>.md (all chapters concatenated, for Word
import or further editing).

Only the Python standard library is used, so this runs anywhere without a
pandoc install. The Markdown subset covers what a practical non-fiction
manuscript actually needs: headings, paragraphs, bullet and numbered lists,
blockquotes, tables, horizontal rules, bold and italic.

A caveat worth knowing: consecutive non-blank lines are joined into one
paragraph, which is normal Markdown but surprises people writing a colophon.
If you want separate lines, separate them with a blank line.
"""

import html
import json
import os
import re
import sys
import uuid
import zipfile
from datetime import datetime, timezone

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
.titlepage .publisher { margin-top: .8em; font-size: .95em; }
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
    out, i, n = [], 0, len(md.split("\n"))
    while i < n:
        stripped = lines[i].strip()

        if not stripped:
            i += 1
            continue

        if stripped == "---":
            out.append("<hr/>")
            i += 1
            continue

        m = re.match(r"^(#{1,4})\s+(.*)$", stripped)
        if m:
            lvl = len(m.group(1))
            out.append("<h%d>%s</h%d>" % (lvl, inline(m.group(2)), lvl))
            i += 1
            continue

        if stripped.startswith("|") and i + 1 < n and is_table_sep(lines[i + 1]):
            header = [c.strip() for c in stripped.strip("|").split("|")]
            i += 2
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            out.append("<table>")
            out.append("<thead><tr>" + "".join(
                "<th>%s</th>" % inline(c) for c in header) + "</tr></thead><tbody>")
            for r in rows:
                r = (r + [""] * len(header))[:len(header)]
                out.append("<tr>" + "".join("<td>%s</td>" % inline(c) for c in r) + "</tr>")
            out.append("</tbody></table>")
            continue

        if stripped.startswith(">"):
            buf = []
            while i < n and lines[i].strip().startswith(">"):
                buf.append(lines[i].strip().lstrip(">").strip())
                i += 1
            out.append("<blockquote><p>%s</p></blockquote>" % inline(" ".join(buf)))
            continue

        if re.match(r"^[-*]\s+", stripped):
            out.append("<ul>")
            while i < n and re.match(r"^[-*]\s+", lines[i].strip()):
                out.append("<li>%s</li>" % inline(re.sub(r"^[-*]\s+", "", lines[i].strip())))
                i += 1
            out.append("</ul>")
            continue

        if re.match(r"^\d+\.\s+", stripped):
            out.append("<ol>")
            while i < n and re.match(r"^\d+\.\s+", lines[i].strip()):
                out.append("<li>%s</li>" % inline(re.sub(r"^\d+\.\s+", "", lines[i].strip())))
                i += 1
            out.append("</ol>")
            continue

        buf = []
        while i < n and lines[i].strip() and not re.match(
                r"^(#{1,4}\s|[-*]\s|\d+\.\s|>|\|)", lines[i].strip()) \
                and lines[i].strip() != "---":
            buf.append(lines[i].strip())
            i += 1
        out.append("<p>%s</p>" % inline("".join(buf)))

    return "\n".join(out)


def page(title, body, lang):
    return ('<?xml version="1.0" encoding="utf-8"?>\n'
            '<html xmlns="http://www.w3.org/1999/xhtml" '
            'xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="%s" lang="%s">\n'
            '<head>\n<meta charset="utf-8"/>\n<title>%s</title>\n'
            '<link rel="stylesheet" type="text/css" href="style.css"/>\n</head>\n'
            '<body>\n%s\n</body>\n</html>\n'
            % (lang, lang, html.escape(title), body))


def build(cfg_path):
    cfg = json.load(open(cfg_path, encoding="utf-8"))
    root = os.path.dirname(os.path.abspath(cfg_path))
    src = os.path.join(root, cfg.get("src_dir", "src"))
    out = os.path.join(root, cfg.get("build_dir", "build"))
    os.makedirs(out, exist_ok=True)

    lang = cfg.get("lang", "ja")
    slug = cfg["slug"]
    title, subtitle = cfg["title"], cfg.get("subtitle", "")
    author, publisher = cfg["author"], cfg.get("publisher", cfg["author"])

    chapters, total = [], 0
    for fname, nav in cfg["chapters"]:
        md = open(os.path.join(src, fname), encoding="utf-8").read()
        total += len(re.sub(r"\s", "", md))
        chapters.append((fname.replace(".md", ".xhtml"), nav, md_to_xhtml(md)))

    title_body = ('<div class="titlepage">\n<h1>%s</h1>\n<p class="sub">%s</p>\n'
                  '<p class="author">%s</p>\n<p class="publisher">発行元　%s</p>\n</div>\n'
                  % (html.escape(title), html.escape(subtitle),
                     html.escape(author), html.escape(publisher)))
    nav_body = ('<nav epub:type="toc" id="toc">\n<h1>目次</h1>\n<ol>\n%s\n</ol>\n</nav>\n'
                % "\n".join('<li><a href="%s">%s</a></li>' % (fn, html.escape(t))
                            for fn, t, _ in chapters))

    manifest = ['<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" '
                'properties="nav"/>',
                '<item id="css" href="style.css" media-type="text/css"/>',
                '<item id="title" href="title.xhtml" media-type="application/xhtml+xml"/>']
    spine = ['<itemref idref="title"/>', '<itemref idref="nav"/>']
    for idx, (fn, _t, _b) in enumerate(chapters):
        manifest.append('<item id="c%d" href="%s" media-type="application/xhtml+xml"/>'
                        % (idx, fn))
        spine.append('<itemref idref="c%d"/>' % idx)

    opf = ('<?xml version="1.0" encoding="utf-8"?>\n'
           '<package xmlns="http://www.idpf.org/2007/opf" version="3.0" '
           'unique-identifier="bookid">\n'
           '  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">\n'
           '    <dc:identifier id="bookid">urn:uuid:%s</dc:identifier>\n'
           '    <dc:title>%s</dc:title>\n'
           '    <dc:creator>%s</dc:creator>\n'
           '    <dc:publisher>%s</dc:publisher>\n'
           '    <dc:language>%s</dc:language>\n'
           '    <dc:description>%s</dc:description>\n'
           '    <meta property="dcterms:modified">%s</meta>\n'
           '  </metadata>\n  <manifest>\n    %s\n  </manifest>\n'
           '  <spine>\n    %s\n  </spine>\n</package>\n'
           % (uuid.uuid5(uuid.NAMESPACE_DNS, slug), html.escape(title),
              html.escape(author), html.escape(publisher), lang,
              html.escape(subtitle),
              datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
              "\n    ".join(manifest), "\n    ".join(spine)))

    container = ('<?xml version="1.0" encoding="utf-8"?>\n<container version="1.0" '
                 'xmlns="urn:oasis:names:tc:opendocument:xmlns:container">\n  <rootfiles>\n'
                 '    <rootfile full-path="OEBPS/content.opf" '
                 'media-type="application/oebps-package+xml"/>\n  </rootfiles>\n</container>\n')

    epub = os.path.join(out, slug + ".epub")
    with zipfile.ZipFile(epub, "w") as z:
        z.writestr("mimetype", "application/epub+zip", zipfile.ZIP_STORED)
        z.writestr("META-INF/container.xml", container, zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/content.opf", opf, zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/style.css", CSS, zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/title.xhtml", page(title, title_body, lang), zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/nav.xhtml", page("目次", nav_body, lang), zipfile.ZIP_DEFLATED)
        for fn, t, body in chapters:
            z.writestr("OEBPS/" + fn, page(t, body, lang), zipfile.ZIP_DEFLATED)

    combined = os.path.join(out, slug + ".md")
    with open(combined, "w", encoding="utf-8") as f:
        f.write("# %s\n\n## %s\n\n---\n\n" % (title, subtitle))
        for fname, _t in cfg["chapters"]:
            f.write(open(os.path.join(src, fname), encoding="utf-8").read().rstrip() + "\n\n")

    print("EPUB : %s (%.1f KB)" % (epub, os.path.getsize(epub) / 1024))
    print("MD   : %s" % combined)
    print("本文文字数（空白除く）: %d 字" % total)


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "book.json")
