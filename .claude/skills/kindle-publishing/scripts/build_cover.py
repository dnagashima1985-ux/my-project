#!/usr/bin/env python3
"""Render KDP cover candidates at 1600x2560, driven by book.json.

Usage:  python3 build_cover.py [book.json]

Writes cover/<slug>-<layout>.jpg for every layout listed in the config.
JPEG because that is what KDP accepts for eBook covers.

Fonts: the exact glyphs used on the cover are fetched from Google Fonts as a
tiny subset (the CSS API's text= parameter), cached in cover/.fonts/. This
keeps the skill small and means any title renders correctly, rather than
shipping a fixed subset that would show tofu for a different book. If the
network is unavailable the script falls back to whatever CJK font the system
has, which usually still reads acceptably.

Rendering uses the Chromium bundled with Playwright when one is available and
Pillow for the JPEG conversion. Where there is no browser at all (a chat-only
environment, a bare container) the same layouts are drawn directly with Pillow
— set COVER_RENDERER=pillow to force that path. The Pillow output is a few
pixels off the browser's in places; it is a working cover, not a pixel match.
"""

import base64
import json
import math
import os
import random
import re
import subprocess
import sys
import urllib.parse

W, H = 1600, 2560
CHROME_CANDIDATES = [
    "/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
    "/opt/pw-browsers/chromium/chrome-linux/chrome",
    "/usr/bin/chromium", "/usr/bin/chromium-browser", "/usr/bin/google-chrome",
]


def find_chrome():
    """Path to a usable Chromium, or None — the Pillow renderer covers None."""
    for p in CHROME_CANDIDATES:
        if os.path.exists(p):
            return p
    import glob
    hits = glob.glob("/opt/pw-browsers/chromium*/chrome-linux/chrome")
    return hits[0] if hits else None


# ------------------------------------------------------------------- fonts

# Google Fonts picks the file format from the User-Agent: a modern browser
# string gets woff2 (what Chromium wants, embedded as a data: URI), an ancient
# one gets TrueType (what Pillow's FreeType can actually open).
UA_WOFF2 = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "Chrome/120 Safari/537.36")
UA_TTF = "Mozilla/4.0"


def fetch_font(family, weight, chars, cache_dir, fmt="woff2"):
    os.makedirs(cache_dir, exist_ok=True)
    key = "%s-%d-%s.%s" % (family.replace(" ", "").lower(), weight,
                           str(abs(hash(chars)))[:8], fmt)
    path = os.path.join(cache_dir, key)
    if os.path.exists(path):
        return path
    url = ("https://fonts.googleapis.com/css2?family="
           + urllib.parse.quote(family.replace(" ", "+"), safe="+")
           + ":wght@%d&text=" % weight + urllib.parse.quote(chars))
    try:
        css = subprocess.run(
            ["curl", "-sS", "-m", "40", "-A",
             UA_TTF if fmt == "ttf" else UA_WOFF2,
             url], capture_output=True, text=True, timeout=60).stdout
        m = re.search(r"url\((https://[^)]+)\)", css)
        if not m:
            return None
        subprocess.run(["curl", "-sS", "-m", "40", "-o", path, m.group(1)],
                       check=True, timeout=60)
        return path
    except Exception:
        return None


def glyphs(cfg):
    """Every character this cover actually prints — the subset to fetch."""
    chars = "".join([cfg["title_1"], cfg["title_2"], cfg.get("subtitle", ""),
                     cfg.get("publisher", ""), cfg.get("hook", ""),
                     "".join(cfg.get("copy", [])), "".join(cfg.get("badge", [])),
                     "".join(cfg.get("diagram_labels", [])),
                     "".join(cfg.get("diagram_numbers", [])),
                     "発行元著0123456789"])
    return "".join(sorted(set(chars)))


def fonts_css(cfg, cache_dir):
    """Subset only the glyphs this cover actually prints."""
    chars = glyphs(cfg)
    out = []
    for weight in (400, 700, 900):
        path = fetch_font("Noto Sans JP", weight, chars, cache_dir)
        if not path:
            continue
        b64 = base64.b64encode(open(path, "rb").read()).decode()
        out.append("@font-face{font-family:'NSJP';font-style:normal;font-weight:%d;"
                   "src:url(data:font/woff2;base64,%s) format('woff2');}" % (weight, b64))
    if not out:
        print("  ! font download failed — falling back to system fonts")
    return "".join(out)


# ------------------------------------------------------------- furniture

def badge_svg(color):
    """The serrated seal that marks the series."""
    cx = cy = 200.0
    pts = []
    for i in range(60):
        r = 196 if i % 2 == 0 else 176
        a = math.pi * 2 * i / 60 - math.pi / 2
        pts.append("%.1f,%.1f" % (cx + r * math.cos(a), cy + r * math.sin(a)))
    return ('<svg width="400" height="400" style="position:absolute;inset:0">'
            '<polygon points="%s" fill="%s"/></svg>' % (" ".join(pts), color))


def badge_block(cfg):
    lines = cfg.get("badge") or []
    if not lines:
        return ""
    return ('<div class="badge">%s<div class="t">%s</div></div>'
            % (badge_svg(cfg.get("badge_color", "#1B5FA8")),
               "".join("<div>%s</div>" % b for b in lines)))


def furniture(cfg, dark):
    ink = "#fff" if dark else "#16161A"
    return """
<div class="byline">発行元　{pub}</div>
<div class="title"><div class="t1">{t1}</div><div class="t2">{t2}</div></div>
<div class="sub">{sub}</div>
<div class="hook">{hook}</div>
<div class="copy">{copy}</div>
{badge}
""".format(pub=cfg.get("publisher", ""), t1=cfg["title_1"], t2=cfg["title_2"],
           sub=cfg.get("subtitle", ""), hook=cfg.get("hook", ""),
           copy="<br>".join(cfg.get("copy", [])), badge=badge_block(cfg))


BASE_CSS = """
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:%dpx;height:%dpx;overflow:hidden}
body{font-family:'NSJP',sans-serif;-webkit-font-smoothing:antialiased}
.page{position:absolute;inset:0;overflow:hidden}
svg.art{position:absolute;inset:0}
.badge{position:absolute;right:88px;top:1980px;width:400px;height:400px}
.badge .t{position:absolute;inset:0;display:flex;flex-direction:column;
          align-items:center;justify-content:center;color:#fff;font-weight:900;
          font-size:52px;line-height:1.34;letter-spacing:.02em}
.byline{position:absolute;left:112px;font-size:34px;font-weight:700;letter-spacing:.02em}
.title{position:absolute;left:104px;font-weight:900;white-space:nowrap}
.t1{font-size:138px;line-height:1.2;letter-spacing:-.03em}
.t2{font-size:214px;line-height:1.1;letter-spacing:-.03em}
.sub{position:absolute;left:112px;font-size:52px;font-weight:700;letter-spacing:.03em}
.hook{position:absolute;left:104px;font-weight:900;font-size:104px;letter-spacing:-.01em}
.copy{position:absolute;left:112px;font-weight:700;font-size:62px;line-height:1.42}
""" % (W, H)

# Vertical rhythm shared by every layout: art on top, type below.
LAYOUT_CSS = """
.byline{top:%dpx}
.title{top:%dpx}
.sub{top:%dpx}
.hook{top:%dpx}
.copy{top:%dpx}
""" % (1216, 1268, 1726, 1898, 2076)


# --------------------------------------------------------------- layouts

def art_dots(cfg, dark):
    """An ordered grid that comes apart and falls — 'this leaks' in one image."""
    rnd = random.Random(cfg.get("seed", 31))
    ink = "#fff" if dark else "#16161A"
    accent = cfg.get("accent", "#F08A24")
    out = []
    for r in range(6):
        for c in range(12):
            x, y = 208 + c * 108, 300 + r * 108
            slip = 0.0
            if r >= 2 and rnd.random() < (r - 1) * 0.22:
                slip = rnd.uniform(12, 34) * (r - 1)
            op = 1.0 if slip == 0 else max(0.22, 1 - slip / 190)
            out.append('<circle cx="%.1f" cy="%.1f" r="15" fill="%s" opacity="%.2f"/>'
                       % (x, y + slip, ink, op))
    for i in range(14):
        out.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" opacity="%.2f"/>'
                   % (rnd.uniform(210, 1400), rnd.uniform(980, 1108),
                      rnd.uniform(9, 14), ink, max(0.12, 0.42 - i * 0.024)))
    for x, y, r in [(880, 1074, 23), (1128, 1032, 15), (612, 1108, 13)]:
        out.append('<circle cx="%d" cy="%d" r="%d" fill="%s"/>' % (x, y, r, accent))
    return "".join(out)


def art_funnel(cfg, dark):
    """A narrowing stack of bars — for books built on a staged model."""
    labels = cfg.get("diagram_labels") or []
    if not labels:
        return art_dots(cfg, dark)
    bar = cfg.get("diagram_color", "#123B6D")
    accent = cfg.get("accent", "#F08A24")
    left, right, top = 150, 1450, 300
    gap = min(120, int(920 / max(len(labels), 1)))
    inset_step = int(540 / max(len(labels) - 1, 1))
    out = []
    for i, lab in enumerate(labels):
        y = top + i * gap
        inset = i * inset_step
        out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="56" fill="%s"/>'
                   % (left + inset, y, (right - left) - inset * 2, bar))
        out.append('<text x="%.1f" y="%.1f" fill="#fff" font-size="34" '
                   'font-family="NSJP" font-weight="900" letter-spacing="6" '
                   'text-anchor="middle">%s</text>' % ((left + right) / 2, y + 40, lab))
    nums = cfg.get("diagram_numbers") or []
    if len(nums) == 2:
        out.append('<text x="150" y="268" fill="%s" font-size="48" font-family="NSJP" '
                   'font-weight="900">%s</text>' % (accent, nums[0]))
        out.append('<text x="1450" y="%d" fill="%s" font-size="48" font-family="NSJP" '
                   'font-weight="900" text-anchor="end">%s</text>'
                   % (top + len(labels) * gap + 46, accent, nums[1]))
    return "".join(out)


LAYOUTS = {
    # name: (background, dark?, art function)
    "white": ("#F5F2EC", False, art_dots),
    "navy": ("#123B6D", True, art_dots),
    "diagram": ("#F5F2EC", False, art_funnel),
}


def render(cfg, layout, fonts, out_dir, chrome):
    bg, dark, art = LAYOUTS[layout]
    ink = "#fff" if dark else "#16161A"
    hook_color = cfg.get("hook_color", "#F08A24" if dark else "#C0392B")
    # The rule separates art from type on the plain dot layout. The diagram
    # layout already has its own horizontal structure, and the rule would cut
    # through the closing figure, so it only belongs on "white".
    rule = ('<div style="position:absolute;left:0;top:1180px;width:%dpx;height:12px;'
            'background:%s"></div>' % (W, cfg.get("accent", "#F08A24"))) \
        if layout == "white" else ""

    css = BASE_CSS + LAYOUT_CSS + """
html,body,.page{background:%s}
.byline{color:%s;opacity:.62}
.title{color:%s}
.sub{color:%s;opacity:.75}
.hook{color:%s}
.copy{color:%s}
""" % (bg, ink, ink, ink, hook_color, ink)

    body = ('<div class="page"><svg class="art" width="%d" height="%d">%s</svg>%s%s</div>'
            % (W, H, art(cfg, dark), rule, furniture(cfg, dark)))
    html = ('<!doctype html><html lang="ja"><head><meta charset="utf-8">'
            '<style>%s%s</style></head><body>%s</body></html>' % (fonts, css, body))

    os.makedirs(out_dir, exist_ok=True)
    stem = "%s-%s" % (cfg["slug"], layout)
    html_path = os.path.join(out_dir, stem + ".html")
    png = os.path.join(out_dir, stem + ".png")
    open(html_path, "w", encoding="utf-8").write(html)

    subprocess.run([chrome, "--headless=new", "--disable-gpu", "--no-sandbox",
                    "--hide-scrollbars", "--force-device-scale-factor=1",
                    "--window-size=%d,%d" % (W, H), "--virtual-time-budget=4000",
                    "--default-background-color=FFFFFFFF",
                    "--screenshot=" + png, "file://" + html_path],
                   check=True, capture_output=True)

    from PIL import Image
    img = Image.open(png).convert("RGB")
    jpg = os.path.join(out_dir, stem + ".jpg")
    img.save(jpg, "JPEG", quality=92, subsampling=0, optimize=True)
    img.resize((180, int(180 * H / W)), Image.LANCZOS).save(
        os.path.join(out_dir, stem + "-thumb.png"))
    print("  %-28s %5.0f KB" % (os.path.basename(jpg), os.path.getsize(jpg) / 1024))
    return jpg


# ------------------------------------------------- renderer without a browser
#
# Same geometry as the CSS above, expressed in pixels. Kept next to the layout
# constants so the two do not drift: change one, change the other.

GEOM = {
    "byline": (112, 1216, 34, 1.2, 700, .62),
    "t1":     (104, 1268, 138, 1.2, 900, 1.0),
    "t2":     (104, 1268 + 166, 214, 1.1, 900, 1.0),
    "sub":    (112, 1726, 52, 1.2, 700, .75),
    "hook":   (104, 1898, 104, 1.2, 900, 1.0),
    "copy":   (112, 2076, 62, 1.42, 700, 1.0),
}


def blend(fg, bg, alpha):
    return tuple(int(round(f * alpha + b * (1 - alpha))) for f, b in zip(fg, bg))


def rgb(hexcolor):
    h = hexcolor.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def pil_fonts(cfg, cache_dir):
    """weight -> TrueType path. Empty dict means we are down to a system font."""
    out = {}
    chars = glyphs(cfg)
    for weight in (400, 700, 900):
        path = fetch_font("Noto Sans JP", weight, chars, cache_dir, fmt="ttf")
        if path:
            out[weight] = path
    if not out:
        print("  ! font download failed — falling back to a system font")
    return out


def pil_font(fonts, weight, size):
    from PIL import ImageFont
    path = fonts.get(weight) or fonts.get(700) or fonts.get(400)
    if path:
        return ImageFont.truetype(path, size)
    for cand in ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                 "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"]:
        if os.path.exists(cand):
            return ImageFont.truetype(cand, size)
    return ImageFont.load_default()


def draw_block(draw, fonts, key, lines, ink, bg, size=None, top=None):
    """One CSS text box: same left edge, line-height and vertical rhythm."""
    x, y0, fs, lh, weight, alpha = GEOM[key]
    fs = size or fs
    y0 = y0 if top is None else top
    font = pil_font(fonts, weight, fs)
    color = blend(ink, bg, alpha)
    pad = (lh - 1) * fs / 2
    for i, line in enumerate(lines):
        draw.text((x, y0 + pad + i * fs * lh), line, font=font, fill=color,
                  anchor="la")


def render_pil(cfg, layout, fonts, out_dir):
    from PIL import Image, ImageDraw
    bgc, dark, art = LAYOUTS[layout]
    bg = rgb(bgc)
    ink = (255, 255, 255) if dark else rgb("#16161A")
    accent = rgb(cfg.get("accent", "#F08A24"))
    hook = rgb(cfg.get("hook_color", "#F08A24" if dark else "#C0392B"))

    img = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(img)

    if art is art_funnel and (cfg.get("diagram_labels") or []):
        labels = cfg["diagram_labels"]
        bar = rgb(cfg.get("diagram_color", "#123B6D"))
        left, right, top = 150, 1450, 300
        gap = min(120, int(920 / max(len(labels), 1)))
        inset_step = int(540 / max(len(labels) - 1, 1))
        for i, lab in enumerate(labels):
            y = top + i * gap
            inset = i * inset_step
            d.rectangle([left + inset, y, right - inset, y + 56], fill=bar)
            f = pil_font(fonts, 900, 34)
            d.text(((left + right) / 2, y + 28), "　".join(lab), font=f,
                   fill=(255, 255, 255), anchor="mm")
        nums = cfg.get("diagram_numbers") or []
        if len(nums) == 2:
            f = pil_font(fonts, 900, 48)
            d.text((150, 268), nums[0], font=f, fill=accent, anchor="ls")
            d.text((1450, top + len(labels) * gap + 46), nums[1], font=f,
                   fill=accent, anchor="rs")
    else:
        rnd = random.Random(cfg.get("seed", 31))
        for r in range(6):
            for c in range(12):
                x, y = 208 + c * 108, 300 + r * 108
                slip = 0.0
                if r >= 2 and rnd.random() < (r - 1) * 0.22:
                    slip = rnd.uniform(12, 34) * (r - 1)
                op = 1.0 if slip == 0 else max(0.22, 1 - slip / 190)
                col = blend(ink, bg, op)
                d.ellipse([x - 15, y + slip - 15, x + 15, y + slip + 15], fill=col)
        for i in range(14):
            x, y = rnd.uniform(210, 1400), rnd.uniform(980, 1108)
            rr = rnd.uniform(9, 14)
            col = blend(ink, bg, max(0.12, 0.42 - i * 0.024))
            d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=col)
        for x, y, rr in [(880, 1074, 23), (1128, 1032, 15), (612, 1108, 13)]:
            d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=accent)

    if layout == "white":
        d.rectangle([0, 1180, W, 1192], fill=accent)

    draw_block(d, fonts, "byline", ["発行元　" + cfg.get("publisher", "")], ink, bg)
    draw_block(d, fonts, "t1", [cfg["title_1"]], ink, bg)
    draw_block(d, fonts, "t2", [cfg["title_2"]], ink, bg)
    if cfg.get("subtitle"):
        draw_block(d, fonts, "sub", [cfg["subtitle"]], ink, bg)
    if cfg.get("hook"):
        draw_block(d, fonts, "hook", [cfg["hook"]], hook, bg)
    if cfg.get("copy"):
        draw_block(d, fonts, "copy", cfg["copy"], ink, bg)

    lines = cfg.get("badge") or []
    if lines:
        cx, cy = W - 88 - 200, 1980 + 200
        pts = []
        for i in range(60):
            r = 196 if i % 2 == 0 else 176
            a = math.pi * 2 * i / 60 - math.pi / 2
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        d.polygon(pts, fill=rgb(cfg.get("badge_color", "#1B5FA8")))
        f = pil_font(fonts, 900, 52)
        step = 52 * 1.34
        y = cy - step * (len(lines) - 1) / 2
        for i, line in enumerate(lines):
            d.text((cx, y + i * step), line, font=f, fill=(255, 255, 255),
                   anchor="mm")

    os.makedirs(out_dir, exist_ok=True)
    stem = "%s-%s" % (cfg["slug"], layout)
    jpg = os.path.join(out_dir, stem + ".jpg")
    img.save(jpg, "JPEG", quality=92, subsampling=0, optimize=True)
    img.resize((180, int(180 * H / W)), Image.LANCZOS).save(
        os.path.join(out_dir, stem + "-thumb.png"))
    print("  %-28s %5.0f KB  (pillow)" % (os.path.basename(jpg),
                                          os.path.getsize(jpg) / 1024))
    return jpg


def main(cfg_path):
    cfg_all = json.load(open(cfg_path, encoding="utf-8"))
    root = os.path.dirname(os.path.abspath(cfg_path))
    cover = dict(cfg_all.get("cover", {}))
    cover.setdefault("slug", cfg_all["slug"])
    cover.setdefault("publisher", cfg_all.get("publisher", cfg_all.get("author", "")))
    cover.setdefault("subtitle", cfg_all.get("subtitle", ""))
    for key in ("title_1", "title_2"):
        if key not in cover:
            raise SystemExit("book.json cover.%s is required "
                             "(split the title across two lines)" % key)

    out_dir = os.path.join(root, "cover")
    cache = os.path.join(out_dir, ".fonts")
    chrome = os.environ.get("CHROME") or find_chrome()
    forced = os.environ.get("COVER_RENDERER", "").lower()
    use_pil = forced == "pillow" or (not chrome and forced != "chromium")
    if forced == "chromium" and not chrome:
        raise SystemExit("Chromium not found — set CHROME, or unset "
                         "COVER_RENDERER to draw with Pillow instead.")
    if use_pil and not forced:
        print("  Chromium not found — drawing with Pillow")

    fonts = pil_fonts(cover, cache) if use_pil else fonts_css(cover, cache)
    layouts = cover.get("layouts") or ["white", "navy", "diagram"]
    print("covers:")
    for layout in layouts:
        if layout not in LAYOUTS:
            print("  ! unknown layout %r — skipped" % layout)
            continue
        if use_pil:
            render_pil(cover, layout, fonts, out_dir)
        else:
            render(cover, layout, fonts, out_dir, chrome)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "book.json")
