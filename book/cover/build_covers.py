#!/usr/bin/env python3
"""Render the Kindle cover concepts at KDP spec (1600x2560).

The layout follows the house style of the フットボールパラダイム series:
a flat colour field, a heavy gothic title with the author set small beside
it, a block of selling copy at the foot, and the serrated series badge
(サッカー指導者にひらめきを) in the bottom-right corner.

Each concept is authored as a self-contained HTML page with the Japanese
webfonts embedded as base64, rendered with the Chromium that ships with
this environment, then saved as JPEG (the format KDP accepts for eBook
covers).
"""

import base64
import math
import os
import random
import subprocess

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(HERE, "fonts")
OUT = os.path.join(HERE, "out")

W, H = 1600, 2560

TITLE_1 = "才能を見落とさない"
TITLE_2 = "七つの関門"
SUBTITLE = "育成年代スカウティングの設計図"
AUTHOR = "フットボールパラダイム"
HOOK = "才能は、こぼれている"
COPY_1 = "見つける技術より、"
COPY_2 = "見落とさない仕組みを"
BADGE = ["サッカー", "指導者に", "ひらめきを"]

CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"


# ------------------------------------------------------------------ helpers

def font_face(family, weight, filename):
    with open(os.path.join(FONT_DIR, filename), "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return ("@font-face{font-family:'%s';font-style:normal;font-weight:%d;"
            "src:url(data:font/woff2;base64,%s) format('woff2');}"
            % (family, weight, b64))


def fonts_css():
    return "".join([
        font_face("NSJP", 400, "notosansjp-400.woff2"),
        font_face("NSJP", 700, "notosansjp-700.woff2"),
        font_face("NSJP", 900, "notosansjp-900.woff2"),
    ])


BASE_CSS = """
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:%dpx;height:%dpx;overflow:hidden}
body{font-family:'NSJP',sans-serif;-webkit-font-smoothing:antialiased}
.page{position:absolute;inset:0;overflow:hidden}
.badge{position:absolute;right:88px;top:1980px;width:400px;height:400px}
.badge .t{position:absolute;inset:0;display:flex;flex-direction:column;
          align-items:center;justify-content:center;color:#fff;font-weight:900;
          font-size:52px;line-height:1.34;letter-spacing:.02em}
.byline{font-size:34px;font-weight:700;letter-spacing:.02em}
""" % (W, H)


def badge_svg(color):
    """The serrated circle the series uses in the bottom-right corner."""
    cx = cy = 200.0
    pts = []
    teeth = 30
    for i in range(teeth * 2):
        r = 196 if i % 2 == 0 else 176
        a = math.pi * 2 * i / (teeth * 2) - math.pi / 2
        pts.append("%.1f,%.1f" % (cx + r * math.cos(a), cy + r * math.sin(a)))
    return ('<svg width="400" height="400" style="position:absolute;inset:0">'
            '<polygon points="%s" fill="%s"/></svg>' % (" ".join(pts), color))


def badge(color):
    return ('<div class="badge">%s<div class="t">%s</div></div>'
            % (badge_svg(color), "".join("<div>%s</div>" % b for b in BADGE)))


# ---------------------------------------------------------------- concept A

def concept_a():
    """Navy field, an ordered grid of dots coming apart and falling."""
    rnd = random.Random(7)
    circles = []
    for r in range(7):
        for c in range(13):
            x, y = 176 + c * 104, 250 + r * 104
            slip = 0.0
            if r >= 3 and rnd.random() < (r - 2) * 0.24:
                slip = rnd.uniform(10, 30) * (r - 2)
            op = 1.0 if slip == 0 else max(0.3, 1 - slip / 200)
            circles.append('<circle cx="%.1f" cy="%.1f" r="14" fill="#fff" '
                           'opacity="%.2f"/>' % (x, y + slip, op))
    for i in range(18):
        circles.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="#fff" '
                       'opacity="%.2f"/>' % (rnd.uniform(180, 1420),
                                             rnd.uniform(1020, 1160),
                                             rnd.uniform(8, 13),
                                             max(0.14, 0.55 - i * 0.026)))
    circles.append('<circle cx="1046" cy="1112" r="21" fill="#F08A24"/>'
                   '<circle cx="1046" cy="1112" r="44" fill="none" '
                   'stroke="#F08A24" stroke-width="4" opacity=".6"/>')

    css = """
html,body,.page{background:#123B6D}
svg.art{position:absolute;inset:0}
.title{position:absolute;left:104px;top:1258px;color:#fff;font-weight:900;
       white-space:nowrap}
.t1{font-size:138px;line-height:1.2;letter-spacing:-.03em}
.t2{font-size:214px;line-height:1.1;letter-spacing:-.03em}
.byline{position:absolute;left:112px;top:1206px;color:#fff;opacity:.72}
.sub{position:absolute;left:112px;top:1712px;color:#fff;opacity:.82;
     font-size:52px;font-weight:700;letter-spacing:.03em}
.hook{position:absolute;left:104px;top:1884px;color:#F08A24;font-weight:900;
      font-size:104px;letter-spacing:-.01em}
.copy{position:absolute;left:112px;top:2062px;color:#fff;font-weight:700;
      font-size:62px;line-height:1.42;letter-spacing:.01em}
"""
    body = """
<div class="page">
  <svg class="art" width="%d" height="%d">%s</svg>
  <div class="byline">著　%s</div>
  <div class="title"><div class="t1">%s</div><div class="t2">%s</div></div>
  <div class="sub">%s</div>
  <div class="hook">%s</div>
  <div class="copy">%s<br>%s</div>
  %s
</div>""" % (W, H, "".join(circles), AUTHOR, TITLE_1, TITLE_2, SUBTITLE,
             HOOK, COPY_1, COPY_2, badge("#F08A24"))
    return css, body


# ---------------------------------------------------------------- concept B

def concept_b():
    """Off-white field, black and orange dots - closest to the series look."""
    rnd = random.Random(31)
    circles = []
    for r in range(6):
        for c in range(12):
            x, y = 208 + c * 108, 300 + r * 108
            slip = 0.0
            if r >= 2 and rnd.random() < (r - 1) * 0.22:
                slip = rnd.uniform(12, 34) * (r - 1)
            op = 1.0 if slip == 0 else max(0.22, 1 - slip / 190)
            circles.append('<circle cx="%.1f" cy="%.1f" r="15" fill="#16161A" '
                           'opacity="%.2f"/>' % (x, y + slip, op))
    for i in range(14):
        circles.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="#16161A" '
                       'opacity="%.2f"/>' % (rnd.uniform(210, 1400),
                                             rnd.uniform(980, 1108),
                                             rnd.uniform(9, 14),
                                             max(0.12, 0.42 - i * 0.024)))
    for x, y, r in [(880, 1074, 23), (1128, 1032, 15), (612, 1108, 13)]:
        circles.append('<circle cx="%d" cy="%d" r="%d" fill="#F08A24"/>'
                       % (x, y, r))

    css = """
html,body,.page{background:#F5F2EC}
svg.art{position:absolute;inset:0}
.bar{position:absolute;left:0;top:1180px;width:1600px;height:12px;background:#F08A24}
.title{position:absolute;left:104px;top:1268px;color:#16161A;font-weight:900;
       white-space:nowrap}
.t1{font-size:138px;line-height:1.2;letter-spacing:-.03em}
.t2{font-size:214px;line-height:1.1;letter-spacing:-.03em}
.byline{position:absolute;left:112px;top:1216px;color:#16161A;opacity:.62}
.sub{position:absolute;left:112px;top:1726px;color:#16161A;opacity:.72;
     font-size:52px;font-weight:700;letter-spacing:.03em}
.hook{position:absolute;left:104px;top:1898px;color:#C0392B;font-weight:900;
      font-size:104px;letter-spacing:-.01em}
.copy{position:absolute;left:112px;top:2076px;color:#16161A;font-weight:700;
      font-size:62px;line-height:1.42}
"""
    body = """
<div class="page">
  <svg class="art" width="%d" height="%d">%s</svg>
  <div class="bar"></div>
  <div class="byline">著　%s</div>
  <div class="title"><div class="t1">%s</div><div class="t2">%s</div></div>
  <div class="sub">%s</div>
  <div class="hook">%s</div>
  <div class="copy">%s<br>%s</div>
  %s
</div>""" % (W, H, "".join(circles), AUTHOR, TITLE_1, TITLE_2, SUBTITLE,
             HOOK, COPY_1, COPY_2, badge("#1B5FA8"))
    return css, body


# ---------------------------------------------------------------- concept C

def concept_c():
    """Diagram-led: the seven gates drawn as a narrowing stack."""
    labels = ["存在", "可視", "識別", "記録", "合意", "時間", "回帰"]
    parts = []
    x_left, x_right = 150, 1450
    top = 300
    gap = 120
    for i, lab in enumerate(labels):
        y = top + i * gap
        inset = i * 76
        parts.append('<rect x="%.1f" y="%.1f" width="%.1f" height="56" '
                     'fill="#123B6D"/>' % (x_left + inset, y,
                                           (x_right - x_left) - inset * 2))
        parts.append('<text x="%.1f" y="%.1f" fill="#fff" font-size="34" '
                     'font-family="NSJP" font-weight="900" letter-spacing="6" '
                     'text-anchor="middle">%s</text>'
                     % ((x_left + x_right) / 2, y + 40, lab))
    parts.append('<text x="150" y="268" fill="#F08A24" font-size="48" '
                 'font-family="NSJP" font-weight="900">100</text>')
    parts.append('<text x="1450" y="1218" fill="#F08A24" font-size="48" '
                 'font-family="NSJP" font-weight="900" text-anchor="end">8</text>')

    css = """
html,body,.page{background:#F5F2EC}
svg.art{position:absolute;inset:0}
.title{position:absolute;left:104px;top:1316px;color:#16161A;font-weight:900;
       white-space:nowrap}
.t1{font-size:138px;line-height:1.2;letter-spacing:-.03em}
.t2{font-size:214px;line-height:1.1;letter-spacing:-.03em}
.byline{position:absolute;left:112px;top:1264px;color:#16161A;opacity:.62}
.sub{position:absolute;left:112px;top:1774px;color:#16161A;opacity:.72;
     font-size:52px;font-weight:700;letter-spacing:.03em}
.hook{position:absolute;left:104px;top:1930px;color:#C0392B;font-weight:900;
      font-size:104px;letter-spacing:-.01em}
.copy{position:absolute;left:112px;top:2108px;color:#16161A;font-weight:700;
      font-size:62px;line-height:1.42}
"""
    body = """
<div class="page">
  <svg class="art" width="%d" height="%d">%s</svg>
  <div class="byline">著　%s</div>
  <div class="title"><div class="t1">%s</div><div class="t2">%s</div></div>
  <div class="sub">%s</div>
  <div class="hook">%s</div>
  <div class="copy">%s<br>%s</div>
  %s
</div>""" % (W, H, "".join(parts), AUTHOR, TITLE_1, TITLE_2, SUBTITLE,
             HOOK, COPY_1, COPY_2, badge("#123B6D"))
    return css, body


# ------------------------------------------------------------------- render

def render(name, css, body):
    html = ("<!doctype html><html lang=\"ja\"><head><meta charset=\"utf-8\">"
            "<style>%s%s%s</style></head><body>%s</body></html>"
            % (fonts_css(), BASE_CSS, css, body))
    html_path = os.path.join(OUT, name + ".html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    png = os.path.join(OUT, name + ".png")
    subprocess.run([
        CHROME, "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
        "--force-device-scale-factor=1", "--window-size=%d,%d" % (W, H),
        "--virtual-time-budget=4000", "--default-background-color=FFFFFFFF",
        "--screenshot=" + png, "file://" + html_path,
    ], check=True, capture_output=True)

    img = Image.open(png).convert("RGB")
    jpg = os.path.join(OUT, name + ".jpg")
    img.save(jpg, "JPEG", quality=92, subsampling=0, optimize=True)
    img.resize((180, int(180 * H / W)), Image.LANCZOS).save(
        os.path.join(OUT, name + "-thumb.png"))

    print("%-14s jpg %5.0f KB" % (name, os.path.getsize(jpg) / 1024))


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, fn in [("cover-a-navy", concept_a),
                     ("cover-b-white", concept_b),
                     ("cover-c-gates", concept_c)]:
        css, body = fn()
        render(name, css, body)


if __name__ == "__main__":
    main()
