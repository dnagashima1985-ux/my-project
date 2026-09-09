#!/usr/bin/env python3
"""Render three genuinely different KDP cover candidates at 1600x2560.

Usage:  python3 build_cover.py [book.json]

Three layouts that share nothing but the series furniture, so the author is
choosing between designs rather than between colourways:

  pitch — the book photographed from above the goal. Grass, white markings,
          type on a dark panel. Reads as football from the thumbnail.
  board — a coach's tactics board. Dark slate, faint grid, the book's own
          model drawn as chips (falls back to a week grid).
  typo  — no picture at all. One enormous title, a diagonal banner, an obi.

What the layouts have in common comes from what sells on a phone screen:
a listing is scanned in a fraction of a second, so each cover carries one
dominant word, at most three colours, an obi across the foot (the single
cheapest way to stop looking self-published), and a hairline border so a
pale cover does not dissolve into Amazon's white background.

Fonts: only the glyphs this cover prints are fetched from Google Fonts and
cached in cover/.fonts/, so any title renders. Rendering uses Chromium when
one is present and Pillow otherwise (COVER_RENDERER=pillow forces it); both
paths read the same geometry tables below, so they cannot drift apart.
"""

import base64
import json
import math
import os
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

UA_WOFF2 = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "Chrome/120 Safari/537.36")
UA_TTF = "Mozilla/4.0"


def find_chrome():
    """Path to a usable Chromium, or None — the Pillow renderer covers None."""
    for p in CHROME_CANDIDATES:
        if os.path.exists(p):
            return p
    import glob
    hits = glob.glob("/opt/pw-browsers/chromium*/chrome-linux/chrome")
    return hits[0] if hits else None


# ------------------------------------------------------------------- fonts

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
             UA_TTF if fmt == "ttf" else UA_WOFF2, url],
            capture_output=True, text=True, timeout=60).stdout
        m = re.search(r"url\((https://[^)]+)\)", css)
        if not m:
            return None
        subprocess.run(["curl", "-sS", "-m", "40", "-o", path, m.group(1)],
                       check=True, timeout=60)
        return path
    except Exception:
        return None


def glyphs(cfg):
    """Every character any layout prints — the subset to fetch."""
    chars = "".join([cfg["title_1"], cfg["title_2"], cfg.get("subtitle", ""),
                     cfg.get("publisher", ""), cfg.get("hook", ""),
                     "".join(cfg.get("copy", [])), "".join(cfg.get("badge", [])),
                     "".join(cfg.get("diagram_labels", [])),
                     "".join(cfg.get("diagram_numbers", [])),
                     cfg.get("obi", ""), "発行元著0123456789 、。・〜"])
    return "".join(sorted(set(chars)))


def fonts_css(cfg, cache_dir):
    out = []
    chars = glyphs(cfg)
    for weight in (400, 700, 900):
        path = fetch_font("Noto Sans JP", weight, chars, cache_dir)
        if not path:
            continue
        b64 = base64.b64encode(open(path, "rb").read()).decode()
        out.append("@font-face{font-family:'NSJP';font-style:normal;font-weight:%d;"
                   "src:url(data:font/woff2;base64,%s) format('woff2');}"
                   % (weight, b64))
    if not out:
        print("  ! font download failed — falling back to system fonts")
    return "".join(out)


def pil_fonts(cfg, cache_dir):
    out = {}
    chars = glyphs(cfg)
    for weight in (400, 700, 900):
        path = fetch_font("Noto Sans JP", weight, chars, cache_dir, fmt="ttf")
        if path:
            out[weight] = path
    if not out:
        print("  ! font download failed — falling back to a system font")
    return out


# ------------------------------------------------------------------ colour

def rgb(hexcolor):
    h = hexcolor.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def blend(fg, bg, alpha):
    return tuple(int(round(f * alpha + b * (1 - alpha))) for f, b in zip(fg, bg))


# -------------------------------------------------------------- geometry
#
# One table per layout, read by both renderers.
#
#   text:  key -> (x, y, size, line-height, weight, colour role, align)
#          y is the top of the first line; align is where x sits.
#   badge: (cx, cy, r, fill) — the serrated series seal, or None
#   obi:   band across the foot: y, background, foreground
#
# Colour roles are resolved against the layout's palette: "ink", "ink70",
# "ink80", "accent", "paper".

LAYOUTS = {
    "pitch": {
        "bg": "#0B6B3A",
        "paper": "#0A3B22",          # the panel the type sits on
        "ink": "#FFFFFF",
        "accent": "#F2A33A",
        "art": "pitch",
        "panel_y": 1180,
        "border": None,
        "text": {
            "byline": (110, 1246, 34, 1.2, 700, "ink70", "left"),
            "t1": (104, 1312, 130, 1.15, 900, "ink", "left"),
            "t2": (104, 1468, 208, 1.08, 900, "ink", "left"),
            "sub": (112, 1742, 50, 1.3, 700, "ink80", "left"),
            "hook": (104, 1876, 98, 1.2, 900, "accent", "left"),
        },
        "badge": (1300, 2072, 148, "#C0392B"),
        "obi": {"y": 2300, "bg": "#FFFFFF", "fg": "#0A3B22"},
    },
    "board": {
        "bg": "#141A22",
        "paper": "#141A22",
        "ink": "#FFFFFF",
        "accent": "#F2C230",
        "art": "board",
        "panel_y": None,
        "border": None,
        "text": {
            "byline": (110, 1286, 34, 1.2, 700, "ink70", "left"),
            "t1": (104, 1352, 130, 1.15, 900, "ink", "left"),
            "t2": (104, 1508, 208, 1.08, 900, "accent", "left"),
            "sub": (112, 1782, 50, 1.3, 700, "ink80", "left"),
            "hook": (104, 1916, 98, 1.2, 900, "ink", "left"),
        },
        "badge": (1300, 2098, 140, "#1B5FA8"),
        "obi": {"y": 2320, "bg": "#F2C230", "fg": "#141A22"},
    },
    "typo": {
        "bg": "#F5F2EC",
        "paper": "#F5F2EC",
        "ink": "#16161A",
        "accent": "#C0392B",
        "art": "banner",
        "panel_y": None,
        "border": "#DCD6C8",
        "text": {
            "byline": (110, 168, 34, 1.2, 700, "ink70", "left"),
            "t1": (104, 1000, 138, 1.15, 900, "ink", "left"),
            "t2": (104, 1164, 226, 1.06, 900, "ink", "left"),
            "sub": (112, 1520, 52, 1.3, 700, "ink80", "left"),
            "hook": (104, 1760, 96, 1.25, 900, "accent", "left"),
        },
        "badge": (1290, 1930, 140, "#16161A"),
        "obi": {"y": 2320, "bg": "#16161A", "fg": "#F5F2EC"},
    },
}

DEFAULT_LAYOUTS = ["pitch", "board", "typo"]

# Pitch markings, seen from behind the goal.
PITCH = {
    "line": 9, "goal_line": 214,
    "box": (232, 214, 1368, 872),
    "goal_area": (540, 214, 1060, 470),
    "goal": (632, 96, 968, 214),
    "spot": (800, 726), "arc_r": 248, "corner_r": 88,
}

BOARD = {"top": 232, "chip_h": 92, "gap": 40, "left": 200, "right": 1400,
         "grid": 96}


def resolve(role, L):
    """Colour role -> (hex, alpha)."""
    if role == "accent":
        return L["accent"], 1.0
    if role == "paper":
        return L["paper"], 1.0
    if role.startswith("ink"):
        alpha = 1.0 if role == "ink" else int(role[3:]) / 100.0
        return L["ink"], alpha
    return role, 1.0


def obi_line(cfg):
    """The catchline that runs across the band at the foot."""
    line = "　".join(x for x in cfg.get("copy", []) if x) or cfg.get("hook", "")
    return line.replace("、　", "、")


# ----------------------------------------------------------- html renderer

def svg_pitch(cfg, L):
    p, ink = PITCH, L["ink"]
    lw = p["line"]
    out = ['<g fill="none" stroke="%s" stroke-width="%d">' % (ink, lw)]
    out.append('<line x1="0" y1="%d" x2="%d" y2="%d"/>'
               % (p["goal_line"], W, p["goal_line"]))
    for box in (p["box"], p["goal_area"]):
        x1, y1, x2, y2 = box
        out.append('<path d="M%d %d V%d H%d V%d"/>' % (x1, y1, y2, x2, y1))
    x1, y1, x2, y2 = p["goal"]
    out.append('<rect x="%d" y="%d" width="%d" height="%d" stroke-width="%d"/>'
               % (x1, y1, x2 - x1, y2 - y1, lw + 4))
    cx, cy = p["spot"]
    out.append('<circle cx="%d" cy="%d" r="9" fill="%s" stroke="none"/>'
               % (cx, cy, ink))
    r = p["arc_r"]
    out.append('<path d="M%d %d A%d %d 0 0 0 %d %d"/>'
               % (cx - r, cy + 60, r, r, cx + r, cy + 60))
    cr = p["corner_r"]
    out.append('<path d="M0 %d A%d %d 0 0 0 %d %d"/>'
               % (p["goal_line"] + cr, cr, cr, cr, p["goal_line"]))
    out.append('<path d="M%d %d A%d %d 0 0 0 %d %d"/>'
               % (W - cr, p["goal_line"], cr, cr, W, p["goal_line"] + cr))
    out.append("</g>")
    return "".join(out)


def board_rows(cfg):
    labels = [l for l in (cfg.get("diagram_labels") or []) if l]
    return labels[:8]


def chip_top(n):
    """Centre the stack of chips in the board area above the type."""
    b = BOARD
    stack = n * (b["chip_h"] + b["gap"]) - b["gap"]
    return max(b["top"], int((1180 - stack) / 2))


def svg_board(cfg, L):
    b, out = BOARD, []
    for x in range(0, W, b["grid"]):
        out.append('<line x1="%d" y1="0" x2="%d" y2="%d" stroke="#242D39" '
                   'stroke-width="2"/>' % (x, x, 1180))
    for y in range(0, 1180, b["grid"]):
        out.append('<line x1="0" y1="%d" x2="%d" y2="%d" stroke="#242D39" '
                   'stroke-width="2"/>' % (y, W, y))
    labels = board_rows(cfg)
    if labels:
        n = len(labels)
        step = int(520 / max(n - 1, 1))
        top = chip_top(n)
        for i, lab in enumerate(labels):
            y = top + i * (b["chip_h"] + b["gap"])
            x1, x2 = b["left"] + i * step // 2, b["right"] - i * step // 2
            out.append('<rect x="%d" y="%d" width="%d" height="%d" rx="8" '
                       'fill="#22303F"/>' % (x1, y, x2 - x1, b["chip_h"]))
            out.append('<rect x="%d" y="%d" width="10" height="%d" '
                       'fill="%s"/>' % (x1, y, b["chip_h"], L["accent"]))
            out.append('<text x="%d" y="%d" fill="#FFFFFF" font-size="44" '
                       'font-family="NSJP" font-weight="700" letter-spacing="4" '
                       'text-anchor="middle">%s</text>'
                       % ((x1 + x2) / 2, y + b["chip_h"] / 2 + 16, lab))
        nums = cfg.get("diagram_numbers") or []
        if len(nums) == 2:
            last = top + (n - 1) * (b["chip_h"] + b["gap"]) + b["chip_h"]
            out.append('<text x="%d" y="%d" fill="%s" font-size="52" '
                       'font-family="NSJP" font-weight="900">%s</text>'
                       % (b["left"], top - 30, L["accent"], nums[0]))
            out.append('<text x="%d" y="%d" fill="%s" font-size="52" '
                       'font-family="NSJP" font-weight="900" '
                       'text-anchor="end">%s</text>'
                       % (b["right"], last + 74, L["accent"], nums[1]))
    else:
        cell, gap = 150, 30
        left = (W - (7 * cell + 6 * gap)) // 2
        marked = {(0, 1), (1, 3), (2, 0), (2, 5), (3, 2)}
        for r in range(4):
            for c in range(7):
                x = left + c * (cell + gap)
                y = 320 + r * (cell + gap)
                fill = L["accent"] if (r, c) in marked else "#22303F"
                out.append('<rect x="%d" y="%d" width="%d" height="%d" rx="6" '
                           'fill="%s"/>' % (x, y, cell, cell, fill))
    return "".join(out)


def svg_banner(cfg, L):
    """A diagonal ribbon carrying the hook, for the type-only layout."""
    pts = "0,300 %d,180 %d,470 0,590" % (W, W)
    return ('<polygon points="%s" fill="%s"/>' % (pts, L["accent"]))


ART_SVG = {"pitch": svg_pitch, "board": svg_board, "banner": svg_banner}


def html_text(cfg, L):
    out = []
    values = {
        "byline": ["発行元　" + cfg.get("publisher", "")],
        "t1": [cfg["title_1"]], "t2": [cfg["title_2"]],
        "sub": [cfg.get("subtitle", "")],
        "hook": [cfg.get("hook", "")],
        "copy": list(cfg.get("copy", [])),
    }
    for key, spec in L["text"].items():
        x, y, size, lh, weight, role, align = spec
        lines = [l for l in values.get(key, []) if l]
        if not lines:
            continue
        if key == "hook" and L["art"] == "banner":
            continue  # the ribbon carries it
        color, alpha = resolve(role, L)
        pos = {"left": "left:%dpx;" % x, "right": "right:%dpx;" % (W - x),
               "center": "left:0;width:%dpx;text-align:center;" % W}[align]
        out.append('<div style="position:absolute;%stop:%dpx;font-size:%dpx;'
                   'line-height:%s;font-weight:%d;color:%s;opacity:%s;'
                   'white-space:nowrap;letter-spacing:-.02em">%s</div>'
                   % (pos, y, size, lh, weight, color, alpha,
                      "<br>".join(lines)))
    return "".join(out)


def html_badge(cfg, L):
    lines = cfg.get("badge") or []
    if not lines or not L.get("badge"):
        return ""
    cx, cy, r, fill = L["badge"]
    fill = cfg.get("badge_color", fill)
    pts = []
    for i in range(60):
        rr = r if i % 2 == 0 else r * 0.9
        a = math.pi * 2 * i / 60 - math.pi / 2
        pts.append("%.1f,%.1f" % (cx + rr * math.cos(a), cy + rr * math.sin(a)))
    size = int(r * 0.33)
    return ('<svg width="%d" height="%d" style="position:absolute;inset:0">'
            '<polygon points="%s" fill="%s"/></svg>'
            '<div style="position:absolute;left:%dpx;top:%dpx;width:%dpx;'
            'text-align:center;color:#fff;font-weight:900;font-size:%dpx;'
            'line-height:1.34">%s</div>'
            % (W, H, " ".join(pts), fill, cx - r, cy - int(size * 1.34 * len(lines) / 2),
               2 * r, size, "<br>".join(lines)))


def html_obi(cfg, L):
    o = L["obi"]
    line = obi_line(cfg)
    band = ('<div style="position:absolute;left:0;top:%dpx;width:%dpx;'
            'height:%dpx;background:%s"></div>' % (o["y"], W, H - o["y"], o["bg"]))
    if not line:
        return band
    return band + ('<div style="position:absolute;left:110px;top:%dpx;'
                   'font-size:48px;font-weight:700;color:%s;'
                   'white-space:nowrap">%s</div>' % (o["y"] + 88, o["fg"], line))


def render_html(cfg, layout, fonts, out_dir, chrome):
    L = LAYOUTS[layout]
    art = ART_SVG[L["art"]](cfg, L)
    panel = ""
    if L["panel_y"]:
        panel = ('<div style="position:absolute;left:0;top:%dpx;width:%dpx;'
                 'height:%dpx;background:%s"></div>'
                 % (L["panel_y"], W, H - L["panel_y"], L["paper"]))
    banner_text = ""
    if L["art"] == "banner" and cfg.get("hook"):
        banner_text = ('<div style="position:absolute;left:0;top:300px;'
                       'width:%dpx;text-align:center;font-size:96px;'
                       'font-weight:900;color:#fff;white-space:nowrap;'
                       'transform:rotate(-4.4deg)">%s</div>'
                       % (W, cfg["hook"]))
    border = ""
    if L["border"]:
        border = ('<div style="position:absolute;inset:0;border:5px solid %s"></div>'
                  % L["border"])

    body = ('<div class="page">'
            '<svg class="art" width="%d" height="%d">%s</svg>'
            '%s%s%s%s%s%s</div>'
            % (W, H, art, panel, banner_text, html_text(cfg, L),
               html_badge(cfg, L), html_obi(cfg, L), border))
    css = ("*{margin:0;padding:0;box-sizing:border-box}"
           "html,body{width:%dpx;height:%dpx;overflow:hidden;background:%s}"
           "body{font-family:'NSJP',sans-serif;-webkit-font-smoothing:antialiased}"
           ".page{position:absolute;inset:0;overflow:hidden;background:%s}"
           "svg.art{position:absolute;inset:0}" % (W, H, L["bg"], L["bg"]))
    html = ('<!doctype html><html lang="ja"><head><meta charset="utf-8">'
            '<style>%s%s</style></head><body>%s</body></html>'
            % (fonts, css, body))

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
    return save(png, out_dir, stem, "")


def save(png, out_dir, stem, note):
    from PIL import Image
    img = Image.open(png).convert("RGB")
    jpg = os.path.join(out_dir, stem + ".jpg")
    img.save(jpg, "JPEG", quality=92, subsampling=0, optimize=True)
    img.resize((180, int(180 * H / W)), Image.LANCZOS).save(
        os.path.join(out_dir, stem + "-thumb.png"))
    print("  %-32s %5.0f KB%s" % (os.path.basename(jpg),
                                  os.path.getsize(jpg) / 1024, note))
    return jpg


# --------------------------------------------------------- pillow renderer

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


def pil_art_pitch(d, cfg, L):
    p, ink = PITCH, rgb(L["ink"])
    lw = p["line"]
    d.line([(0, p["goal_line"]), (W, p["goal_line"])], fill=ink, width=lw)
    for box in (p["box"], p["goal_area"]):
        x1, y1, x2, y2 = box
        d.line([(x1, y1), (x1, y2), (x2, y2), (x2, y1)], fill=ink, width=lw)
    x1, y1, x2, y2 = p["goal"]
    d.rectangle([x1, y1, x2, y2], outline=ink, width=lw + 4)
    cx, cy = p["spot"]
    d.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=ink)
    r = p["arc_r"]
    d.arc([cx - r, cy + 60 - r, cx + r, cy + 60 + r], 0, 180, fill=ink, width=lw)
    cr = p["corner_r"]
    gl = p["goal_line"]
    d.arc([-cr, gl - cr, cr, gl + cr], 0, 90, fill=ink, width=lw)
    d.arc([W - cr, gl - cr, W + cr, gl + cr], 90, 180, fill=ink, width=lw)


def pil_art_board(d, cfg, L, fonts):
    b = BOARD
    grid = rgb("#242D39")
    for x in range(0, W, b["grid"]):
        d.line([(x, 0), (x, 1180)], fill=grid, width=2)
    for y in range(0, 1180, b["grid"]):
        d.line([(0, y), (W, y)], fill=grid, width=2)
    labels = board_rows(cfg)
    accent = rgb(L["accent"])
    if labels:
        n = len(labels)
        step = int(520 / max(n - 1, 1))
        top = chip_top(n)
        f = pil_font(fonts, 700, 44)
        for i, lab in enumerate(labels):
            y = top + i * (b["chip_h"] + b["gap"])
            x1, x2 = b["left"] + i * step // 2, b["right"] - i * step // 2
            d.rectangle([x1, y, x2, y + b["chip_h"]], fill=rgb("#22303F"))
            d.rectangle([x1, y, x1 + 10, y + b["chip_h"]], fill=accent)
            d.text(((x1 + x2) / 2, y + b["chip_h"] / 2), "　".join(lab),
                   font=f, fill=(255, 255, 255), anchor="mm")
        nums = cfg.get("diagram_numbers") or []
        if len(nums) == 2:
            fn = pil_font(fonts, 900, 52)
            last = top + (n - 1) * (b["chip_h"] + b["gap"]) + b["chip_h"]
            d.text((b["left"], top - 30), nums[0], font=fn, fill=accent,
                   anchor="ls")
            d.text((b["right"], last + 74), nums[1], font=fn, fill=accent,
                   anchor="rs")
    else:
        cell, gap = 150, 30
        left = (W - (7 * cell + 6 * gap)) // 2
        marked = {(0, 1), (1, 3), (2, 0), (2, 5), (3, 2)}
        for r in range(4):
            for c in range(7):
                x = left + c * (cell + gap)
                y = 320 + r * (cell + gap)
                d.rectangle([x, y, x + cell, y + cell],
                            fill=accent if (r, c) in marked else rgb("#22303F"))


def pil_art_banner(d, cfg, L, fonts):
    d.polygon([(0, 300), (W, 180), (W, 470), (0, 590)], fill=rgb(L["accent"]))
    if cfg.get("hook"):
        f = pil_font(fonts, 900, 96)
        d.text((W / 2, 385), cfg["hook"], font=f, fill=(255, 255, 255),
               anchor="mm")


def render_pil(cfg, layout, fonts, out_dir):
    from PIL import Image, ImageDraw
    L = LAYOUTS[layout]
    img = Image.new("RGB", (W, H), rgb(L["bg"]))
    d = ImageDraw.Draw(img)

    if L["art"] == "pitch":
        pil_art_pitch(d, cfg, L)
    elif L["art"] == "board":
        pil_art_board(d, cfg, L, fonts)
    else:
        pil_art_banner(d, cfg, L, fonts)

    if L["panel_y"]:
        d.rectangle([0, L["panel_y"], W, H], fill=rgb(L["paper"]))

    text_bg = rgb(L["paper"])
    values = {
        "byline": ["発行元　" + cfg.get("publisher", "")],
        "t1": [cfg["title_1"]], "t2": [cfg["title_2"]],
        "sub": [cfg.get("subtitle", "")], "hook": [cfg.get("hook", "")],
        "copy": list(cfg.get("copy", [])),
    }
    for key, spec in L["text"].items():
        x, y, size, lh, weight, role, align = spec
        lines = [l for l in values.get(key, []) if l]
        if not lines or (key == "hook" and L["art"] == "banner"):
            continue
        color, alpha = resolve(role, L)
        fill = blend(rgb(color), text_bg, alpha)
        f = pil_font(fonts, weight, size)
        anchor = {"left": "la", "right": "ra", "center": "ma"}[align]
        ax = {"left": x, "right": x, "center": W / 2}[align]
        pad = (lh - 1) * size / 2
        for i, line in enumerate(lines):
            d.text((ax, y + pad + i * size * lh), line, font=f, fill=fill,
                   anchor=anchor)

    lines = cfg.get("badge") or []
    if lines and L.get("badge"):
        cx, cy, r, fill = L["badge"]
        fill = rgb(cfg.get("badge_color", fill))
        pts = []
        for i in range(60):
            rr = r if i % 2 == 0 else r * 0.9
            a = math.pi * 2 * i / 60 - math.pi / 2
            pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
        d.polygon(pts, fill=fill)
        size = int(r * 0.33)
        f = pil_font(fonts, 900, size)
        step = size * 1.34
        y0 = cy - step * (len(lines) - 1) / 2
        for i, line in enumerate(lines):
            d.text((cx, y0 + i * step), line, font=f, fill=(255, 255, 255),
                   anchor="mm")

    o = L["obi"]
    d.rectangle([0, o["y"], W, H], fill=rgb(o["bg"]))
    line = obi_line(cfg)
    if line:
        d.text((110, o["y"] + 88), line, font=pil_font(fonts, 700, 48),
               fill=rgb(o["fg"]), anchor="la")

    if L["border"]:
        for i in range(5):
            d.rectangle([i, i, W - 1 - i, H - 1 - i], outline=rgb(L["border"]))

    os.makedirs(out_dir, exist_ok=True)
    stem = "%s-%s" % (cfg["slug"], layout)
    png = os.path.join(out_dir, stem + ".png")
    img.save(png)
    return save(png, out_dir, stem, "  (pillow)")


# ------------------------------------------------------------------- main

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
    layouts = cover.get("layouts") or DEFAULT_LAYOUTS
    print("covers:")
    for layout in layouts:
        if layout not in LAYOUTS:
            print("  ! unknown layout %r — skipped" % layout)
            continue
        if use_pil:
            render_pil(cover, layout, fonts, out_dir)
        else:
            render_html(cover, layout, fonts, out_dir, chrome)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "book.json")
