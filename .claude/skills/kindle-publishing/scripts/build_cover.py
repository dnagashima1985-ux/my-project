#!/usr/bin/env python3
"""Render three cover candidates at 1600x2560 — different ones for every book.

Usage:  python3 build_cover.py [book.json] [--seed N]

Nine compositions live here, in three families. Each book gets one from each
family, so the three candidates never rhyme with each other:

  絵 scene   pitch  grass and the goal-area markings
             night  floodlights over a dark stand
             stripe the shirt: broad vertical bars
  図 diagram board  a coach's tactics board, the model drawn as chips
             formation  the team as dots and passing lines
             cycle  the model as a ring with stations around it
  文字 type   typo   a diagonal ribbon and one enormous title
             frame  a heavy rule box, everything centred
             number a giant numeral ghosted behind the title

Which three a book gets is decided by its slug, so a rebuild is stable but
the next book looks nothing like this one. `--seed 2` (or "seed" in
book.json's cover block) rerolls when the author wants another set. Palettes
are picked the same way, so even a repeated layout arrives in new colours.

What every cover shares comes from what sells on a phone: one dominant word,
three colours, a single emphasis, an obi across the foot, and a hairline
border on pale grounds so the thumbnail does not dissolve into Amazon's
white page.

Fonts: only the glyphs this cover prints are fetched from Google Fonts and
cached in cover/.fonts/. Rendering uses Chromium when present and Pillow
otherwise (COVER_RENDERER=pillow forces it); both read the geometry tables
below, so the two paths cannot drift apart.
"""

import base64
import hashlib
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
                           hashlib.md5(chars.encode()).hexdigest()[:8], fmt)
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
    chars = "".join([cfg["title_1"], cfg["title_2"], cfg.get("subtitle", ""),
                     cfg.get("publisher", ""), cfg.get("hook", ""),
                     "".join(cfg.get("copy", [])), "".join(cfg.get("badge", [])),
                     "".join(cfg.get("diagram_labels", [])),
                     "".join(cfg.get("diagram_numbers", [])),
                     "発行元著0123456789 、。・〜"])
    return "".join(sorted(set(chars)))


def fonts_css(cfg, cache_dir):
    out, chars = [], glyphs(cfg)
    for weight in (400, 700, 900):
        path = fetch_font("Noto Sans JP", weight, chars, cache_dir)
        if not path:
            continue
        b64 = base64.b64encode(open(path, "rb").read()).decode()
        out.append("@font-face{font-family:'NSJP';font-style:normal;"
                   "font-weight:%d;src:url(data:font/woff2;base64,%s) "
                   "format('woff2');}" % (weight, b64))
    if not out:
        print("  ! font download failed — falling back to system fonts")
    return "".join(out)


def pil_fonts(cfg, cache_dir):
    out, chars = {}, glyphs(cfg)
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


def mix(a, b, t):
    """Hex colour a moved t of the way toward hex colour b."""
    return "#%02X%02X%02X" % blend(rgb(b), rgb(a), t)


def contrast(bg):
    """Ink for the art area: black on a light ground, white on a dark one.

    The palette's "ink" belongs to the type, which on several layouts sits on
    the panel rather than the ground — reading it here is how a dark diagram
    ended up drawn on a dark field.
    """
    r, g, b = rgb(bg)
    return "#16161A" if (0.299 * r + 0.587 * g + 0.114 * b) > 150 else "#FFFFFF"


def art(P, t=1.0):
    """Art-area ink, optionally faded toward the ground."""
    return mix(P["bg"], contrast(P["bg"]), t)


# ---------------------------------------------------------------- geometry
#
# Text blocks: key -> (x, y, size, line-height, weight, colour role, align).
# y is the top of the first line. Roles resolve against the palette.

TEXT = {
    # type sits on a panel across the lower half
    "lower": {
        "byline": (110, 1246, 34, 1.2, 700, "ink70", "left"),
        "t1": (104, 1312, 130, 1.15, 900, "ink", "left"),
        "t2": (104, 1468, 208, 1.08, 900, "t2", "left"),
        "sub": (112, 1742, 50, 1.3, 700, "ink80", "left"),
        "hook": (104, 1876, 98, 1.2, 900, "accent", "left"),
    },
    # the ribbon carries the hook, so the title drops to the middle
    "ribbon": {
        "byline": (110, 168, 34, 1.2, 700, "ink70", "left"),
        "t1": (104, 1000, 138, 1.15, 900, "ink", "left"),
        "t2": (104, 1164, 226, 1.06, 900, "t2", "left"),
        "sub": (112, 1520, 52, 1.3, 700, "ink80", "left"),
    },
    # everything centred, for the rule box and the giant numeral
    "centre": {
        "byline": (800, 300, 34, 1.2, 700, "ink70", "centre"),
        "t1": (800, 940, 126, 1.15, 900, "ink", "centre"),
        "t2": (800, 1094, 206, 1.08, 900, "t2", "centre"),
        "sub": (800, 1420, 48, 1.3, 700, "ink80", "centre"),
        "hook": (800, 1600, 92, 1.2, 900, "accent", "centre"),
    },
}

PITCH = {"line": 9, "goal_line": 214, "box": (232, 214, 1368, 872),
         "goal_area": (540, 214, 1060, 470), "goal": (632, 96, 968, 214),
         "spot": (800, 726), "arc_r": 248, "corner_r": 88}
BOARD = {"top": 232, "chip_h": 92, "gap": 40, "left": 200, "right": 1400,
         "grid": 96}
# 4-2-3-1 seen from above, in the art area
FORMATION = [(800, 240), (330, 470), (620, 470), (980, 470), (1270, 470),
             (560, 700), (1040, 700), (330, 930), (800, 930), (1270, 930),
             (800, 1120)]
FORMATION_LINKS = [(0, 1), (0, 2), (1, 5), (2, 5), (3, 6), (4, 6), (5, 7),
                   (5, 8), (6, 8), (6, 9), (8, 10)]

# Palettes are (bg, paper, ink, accent, obi_bg, obi_fg, badge, border|None).
LAYOUTS = {
    "pitch": {
        "family": "scene", "art": "pitch", "text": "lower", "panel": 1180,
        "badge": (1300, 2072, 148), "obi_y": 2300,
        "palettes": [
            ("#0B6B3A", "#0A3B22", "#FFFFFF", "#F2A33A", "#FFFFFF", "#0A3B22",
             "#C0392B", None),
            ("#1D6E5F", "#0C332C", "#FFFFFF", "#F5D06A", "#F5F2EC", "#0C332C",
             "#C0392B", None),
        ],
    },
    "night": {
        "family": "scene", "art": "night", "text": "lower", "panel": 1180,
        "badge": (1300, 2072, 148), "obi_y": 2300,
        "palettes": [
            ("#0D1B2A", "#0A1420", "#FFFFFF", "#F2A33A", "#F2A33A", "#0A1420",
             "#C0392B", None),
            ("#241634", "#170E22", "#FFFFFF", "#7BE3C6", "#F5F2EC", "#170E22",
             "#7A3EA8", None),
        ],
    },
    "stripe": {
        "family": "scene", "art": "stripe", "text": "lower", "panel": 1180,
        "badge": (1300, 2072, 148), "obi_y": 2300,
        "palettes": [
            ("#B62025", "#1A1A1E", "#FFFFFF", "#F2C230", "#F2C230", "#1A1A1E",
             "#1A1A1E", None),
            ("#1B5FA8", "#10233A", "#FFFFFF", "#F5F2EC", "#FFFFFF", "#10233A",
             "#C0392B", None),
        ],
    },
    "board": {
        "family": "diagram", "art": "board", "text": "lower", "panel": None,
        "badge": (1300, 2098, 140), "obi_y": 2320, "t2": "accent",
        "palettes": [
            ("#141A22", "#141A22", "#FFFFFF", "#F2C230", "#F2C230", "#141A22",
             "#1B5FA8", None),
            ("#14261F", "#14261F", "#FFFFFF", "#6FD08C", "#6FD08C", "#0E1A15",
             "#C0392B", None),
        ],
    },
    "formation": {
        "family": "diagram", "art": "formation", "text": "lower",
        "panel": 1180, "badge": (1300, 2072, 148), "obi_y": 2300,
        "palettes": [
            ("#F5F2EC", "#16161A", "#FFFFFF", "#F08A24", "#F08A24", "#16161A",
             "#1B5FA8", "#DCD6C8"),
            ("#0E2A3A", "#08151D", "#FFFFFF", "#4FC3E8", "#FFFFFF", "#08151D",
             "#C0392B", None),
        ],
    },
    "cycle": {
        "family": "diagram", "art": "cycle", "text": "lower", "panel": 1180,
        "badge": (1300, 2072, 148), "obi_y": 2300,
        "palettes": [
            ("#F5F2EC", "#123B6D", "#FFFFFF", "#F08A24", "#F08A24", "#123B6D",
             "#C0392B", "#DCD6C8"),
            ("#2B1B12", "#1A100A", "#FFFFFF", "#E8A33D", "#E8A33D", "#1A100A",
             "#8C3B1E", None),
        ],
    },
    "typo": {
        "family": "type", "art": "ribbon", "text": "ribbon", "panel": None,
        "badge": (1290, 1930, 140), "obi_y": 2320,
        "palettes": [
            ("#F5F2EC", "#F5F2EC", "#16161A", "#C0392B", "#16161A", "#F5F2EC",
             "#16161A", "#DCD6C8"),
            ("#16161A", "#16161A", "#FFFFFF", "#F2C230", "#F2C230", "#16161A",
             "#C0392B", None),
        ],
    },
    "frame": {
        "family": "type", "art": "frame", "text": "centre", "panel": None,
        "badge": (800, 1900, 132), "obi_y": 2320,
        "palettes": [
            ("#F5F2EC", "#F5F2EC", "#16161A", "#C0392B", "#C0392B", "#F5F2EC",
             "#16161A", None),
            ("#123B6D", "#123B6D", "#FFFFFF", "#F2C230", "#FFFFFF", "#123B6D",
             "#C0392B", None),
        ],
    },
    "number": {
        "family": "type", "art": "number", "text": "centre", "panel": None,
        "badge": (800, 1900, 132), "obi_y": 2320,
        "palettes": [
            ("#F5F2EC", "#F5F2EC", "#16161A", "#C0392B", "#16161A", "#F5F2EC",
             "#C0392B", "#DCD6C8"),
            ("#0F1D2E", "#0F1D2E", "#FFFFFF", "#F2A33A", "#F2A33A", "#0F1D2E",
             "#1B5FA8", None),
        ],
    },
}

FAMILIES = ["scene", "diagram", "type"]


def palette(name, idx):
    keys = ("bg", "paper", "ink", "accent", "obi_bg", "obi_fg", "badge",
            "border")
    pals = LAYOUTS[name]["palettes"]
    return dict(zip(keys, pals[idx % len(pals)]))


def pick_layouts(cfg, seed):
    """One layout from each family, decided by the book's slug and the seed."""
    import random
    rnd = random.Random("%s|%s" % (cfg.get("slug", ""), seed))
    chosen = []
    for fam in FAMILIES:
        names = sorted(n for n, L in LAYOUTS.items() if L["family"] == fam)
        name = rnd.choice(names)
        chosen.append((name, rnd.randrange(8)))
    return chosen


def resolve(role, P):
    if role in ("accent", "paper", "bg"):
        return P[role], 1.0
    if role == "t2":
        return P["accent"] if P.get("_t2") == "accent" else P["ink"], 1.0
    if role.startswith("ink"):
        return P["ink"], 1.0 if role == "ink" else int(role[3:]) / 100.0
    return role, 1.0


def obi_line(cfg):
    line = "　".join(x for x in cfg.get("copy", []) if x) or cfg.get("hook", "")
    return line.replace("、　", "、")


def numeral_size(num):
    """Shrink the ghosted numeral so more than two digits still fit the page."""
    return min(1180, int(1400 / (0.55 * max(len(num), 1))))


def big_number(cfg):
    """The numeral the 'number' layout ghosts behind the title."""
    nums = cfg.get("diagram_numbers") or []
    if nums:
        m = re.search(r"\d+", nums[0])
        if m:
            return m.group()
    labels = cfg.get("diagram_labels") or []
    if labels:
        return str(len(labels))
    m = re.search(r"\d+", cfg["title_1"] + cfg["title_2"])
    return m.group() if m else ""


def chip_top(n):
    b = BOARD
    stack = n * (b["chip_h"] + b["gap"]) - b["gap"]
    return max(b["top"], int((1180 - stack) / 2))


def board_rows(cfg):
    return [l for l in (cfg.get("diagram_labels") or []) if l][:8]


# ------------------------------------------------------------ art: svg side

def svg_pitch(cfg, P):
    p, ink = PITCH, art(P)
    lw = p["line"]
    out = ['<g fill="none" stroke="%s" stroke-width="%d">' % (ink, lw)]
    out.append('<line x1="0" y1="%d" x2="%d" y2="%d"/>'
               % (p["goal_line"], W, p["goal_line"]))
    for x1, y1, x2, y2 in (p["box"], p["goal_area"]):
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


def svg_night(cfg, P):
    glow = mix(P["bg"], P["accent"], .18)
    out = []
    for i, (x, spread) in enumerate([(230, 150), (640, 190), (1060, 190),
                                     (1400, 150)]):
        out.append('<polygon points="%d,-40 %d,-40 %d,1180 %d,1180" '
                   'fill="%s" opacity="%.2f"/>'
                   % (x - 34, x + 34, x + spread * 2.4, x - spread * 2.4,
                      glow, .55 - i * .04))
        out.append('<rect x="%d" y="20" width="68" height="52" fill="%s"/>'
                   % (x - 34, P["accent"]))
    out.append('<line x1="0" y1="1010" x2="%d" y2="1010" stroke="%s" '
               'stroke-width="8" opacity=".85"/>' % (W, art(P)))
    out.append('<path d="M560 1010 A240 240 0 0 0 1040 1010" fill="none" '
               'stroke="%s" stroke-width="8" opacity=".85"/>' % art(P))
    return "".join(out)


def svg_stripe(cfg, P):
    dark = mix(P["bg"], "#000000", .3)
    out = []
    for i in range(9):
        if i % 2:
            out.append('<rect x="%d" y="0" width="180" height="1180" '
                       'fill="%s"/>' % (i * 180, dark))
    out.append('<rect x="0" y="1096" width="%d" height="84" fill="%s"/>'
               % (W, P["accent"]))
    return "".join(out)


def svg_board(cfg, P):
    b, out = BOARD, []
    line = art(P, .12)
    for x in range(0, W, b["grid"]):
        out.append('<line x1="%d" y1="0" x2="%d" y2="1180" stroke="%s" '
                   'stroke-width="2"/>' % (x, x, line))
    for y in range(0, 1180, b["grid"]):
        out.append('<line x1="0" y1="%d" x2="%d" y2="%d" stroke="%s" '
                   'stroke-width="2"/>' % (y, W, y, line))
    labels = board_rows(cfg)
    chip = art(P, .16)
    if labels:
        n, top = len(labels), chip_top(len(labels))
        step = int(520 / max(n - 1, 1))
        for i, lab in enumerate(labels):
            y = top + i * (b["chip_h"] + b["gap"])
            x1, x2 = b["left"] + i * step // 2, b["right"] - i * step // 2
            out.append('<rect x="%d" y="%d" width="%d" height="%d" rx="8" '
                       'fill="%s"/>' % (x1, y, x2 - x1, b["chip_h"], chip))
            out.append('<rect x="%d" y="%d" width="10" height="%d" fill="%s"/>'
                       % (x1, y, b["chip_h"], P["accent"]))
            out.append('<text x="%d" y="%d" fill="%s" font-size="44" '
                       'font-family="NSJP" font-weight="700" letter-spacing="4" '
                       'text-anchor="middle">%s</text>'
                       % ((x1 + x2) / 2, y + b["chip_h"] / 2 + 16, art(P), lab))
        nums = cfg.get("diagram_numbers") or []
        if len(nums) == 2:
            last = top + (n - 1) * (b["chip_h"] + b["gap"]) + b["chip_h"]
            out.append('<text x="%d" y="%d" fill="%s" font-size="52" '
                       'font-family="NSJP" font-weight="900">%s</text>'
                       % (b["left"], top - 30, P["accent"], nums[0]))
            out.append('<text x="%d" y="%d" fill="%s" font-size="52" '
                       'font-family="NSJP" font-weight="900" '
                       'text-anchor="end">%s</text>'
                       % (b["right"], last + 74, P["accent"], nums[1]))
    else:
        cell, gap = 150, 30
        left = (W - (7 * cell + 6 * gap)) // 2
        marked = {(0, 1), (1, 3), (2, 0), (2, 5), (3, 2)}
        for r in range(4):
            for c in range(7):
                out.append('<rect x="%d" y="%d" width="%d" height="%d" rx="6" '
                           'fill="%s"/>'
                           % (left + c * (cell + gap), 320 + r * (cell + gap),
                              cell, cell,
                              P["accent"] if (r, c) in marked else chip))
    return "".join(out)


def svg_formation(cfg, P):
    line = art(P, .3)
    out = ['<rect x="0" y="0" width="%d" height="1180" fill="%s"/>'
           % (W, art(P, .05))]
    for a, b in FORMATION_LINKS:
        x1, y1 = FORMATION[a]
        x2, y2 = FORMATION[b]
        out.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" '
                   'stroke-width="4"/>' % (x1, y1, x2, y2, line))
    for i, (x, y) in enumerate(FORMATION):
        fill = P["accent"] if i in (0, 10) else art(P, .88)
        out.append('<circle cx="%d" cy="%d" r="36" fill="%s"/>' % (x, y, fill))
    return "".join(out)


def svg_cycle(cfg, P):
    cx, cy, r = 800, 620, 372
    labels = board_rows(cfg) or ["", "", "", ""]
    out = ['<circle cx="%d" cy="%d" r="%d" fill="none" stroke="%s" '
           'stroke-width="16"/>' % (cx, cy, r, art(P, .22))]
    n = len(labels)
    for i, lab in enumerate(labels):
        a = math.pi * 2 * i / n - math.pi / 2
        x, y = cx + r * math.cos(a), cy + r * math.sin(a)
        out.append('<circle cx="%.0f" cy="%.0f" r="30" fill="%s"/>'
                   % (x, y, P["accent"]))
        lx, ly = cx + (r + 96) * math.cos(a), cy + (r + 96) * math.sin(a)
        anchor = "middle" if abs(math.cos(a)) < .3 else (
            "start" if math.cos(a) > 0 else "end")
        out.append('<text x="%.0f" y="%.0f" fill="%s" font-size="42" '
                   'font-family="NSJP" font-weight="700" text-anchor="%s">%s'
                   '</text>' % (lx, ly + 14, art(P, .85), anchor, lab))
    nums = cfg.get("diagram_numbers") or []
    if nums:
        out.append('<text x="%d" y="%d" fill="%s" font-size="132" '
                   'font-family="NSJP" font-weight="900" text-anchor="middle">'
                   '%s</text>' % (cx, cy + 46, P["accent"], nums[0]))
    return "".join(out)


def svg_ribbon(cfg, P):
    return ('<polygon points="0,300 %d,180 %d,470 0,590" fill="%s"/>'
            % (W, W, P["accent"]))


def svg_frame(cfg, P):
    return ('<rect x="64" y="64" width="%d" height="%d" fill="none" '
            'stroke="%s" stroke-width="26"/>'
            '<rect x="132" y="132" width="%d" height="%d" fill="none" '
            'stroke="%s" stroke-width="4"/>'
            % (W - 128, H - 128, P["accent"], W - 264, H - 264,
               art(P, .35)))


def svg_number(cfg, P):
    num = big_number(cfg)
    if not num:
        return ""
    size = numeral_size(num)
    return ('<text x="%d" y="%d" fill="%s" font-size="%d" font-family="NSJP" '
            'font-weight="900" text-anchor="middle">%s</text>'
            % (W / 2, 620 + size / 2, art(P, .1), size, num))


ART_SVG = {"pitch": svg_pitch, "night": svg_night, "stripe": svg_stripe,
           "board": svg_board, "formation": svg_formation, "cycle": svg_cycle,
           "ribbon": svg_ribbon, "frame": svg_frame, "number": svg_number}


# ----------------------------------------------------------- html renderer

def text_values(cfg):
    return {"byline": ["発行元　" + cfg.get("publisher", "")],
            "t1": [cfg["title_1"]], "t2": [cfg["title_2"]],
            "sub": [cfg.get("subtitle", "")], "hook": [cfg.get("hook", "")]}


def html_text(cfg, L, P):
    out, values = [], text_values(cfg)
    for key, spec in TEXT[L["text"]].items():
        x, y, size, lh, weight, role, align = spec
        lines = [l for l in values.get(key, []) if l]
        if not lines:
            continue
        color, alpha = resolve(role, P)
        pos = ("left:%dpx;" % x if align == "left" else
               "left:0;width:%dpx;text-align:center;" % W)
        out.append('<div style="position:absolute;%stop:%dpx;font-size:%dpx;'
                   'line-height:%s;font-weight:%d;color:%s;opacity:%s;'
                   'white-space:nowrap;letter-spacing:-.02em">%s</div>'
                   % (pos, y, size, lh, weight, color, alpha,
                      "<br>".join(lines)))
    return "".join(out)


def badge_points(cx, cy, r):
    pts = []
    for i in range(60):
        rr = r if i % 2 == 0 else r * 0.9
        a = math.pi * 2 * i / 60 - math.pi / 2
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return pts


def html_badge(cfg, L, P):
    lines = cfg.get("badge") or []
    if not lines:
        return ""
    cx, cy, r = L["badge"]
    fill = cfg.get("badge_color", P["badge"])
    pts = " ".join("%.1f,%.1f" % p for p in badge_points(cx, cy, r))
    size = int(r * 0.33)
    return ('<svg width="%d" height="%d" style="position:absolute;inset:0">'
            '<polygon points="%s" fill="%s"/></svg>'
            '<div style="position:absolute;left:%dpx;top:%dpx;width:%dpx;'
            'text-align:center;color:#fff;font-weight:900;font-size:%dpx;'
            'line-height:1.34">%s</div>'
            % (W, H, pts, fill, cx - r,
               cy - int(size * 1.34 * len(lines) / 2), 2 * r, size,
               "<br>".join(lines)))


def html_obi(cfg, L, P):
    y = L["obi_y"]
    band = ('<div style="position:absolute;left:0;top:%dpx;width:%dpx;'
            'height:%dpx;background:%s"></div>' % (y, W, H - y, P["obi_bg"]))
    line = obi_line(cfg)
    if not line:
        return band
    return band + ('<div style="position:absolute;left:110px;top:%dpx;'
                   'font-size:48px;font-weight:700;color:%s;'
                   'white-space:nowrap">%s</div>' % (y + 88, P["obi_fg"], line))


def render_html(cfg, name, idx, fonts, out_dir, chrome, stem):
    L, P = LAYOUTS[name], palette(name, idx)
    P["_t2"] = L.get("t2", "ink")
    art = ART_SVG[L["art"]](cfg, P)
    panel = ""
    if L["panel"]:
        panel = ('<div style="position:absolute;left:0;top:%dpx;width:%dpx;'
                 'height:%dpx;background:%s"></div>'
                 % (L["panel"], W, H - L["panel"], P["paper"]))
    ribbon_text = ""
    if L["art"] == "ribbon" and cfg.get("hook"):
        ribbon_text = ('<div style="position:absolute;left:0;top:300px;'
                       'width:%dpx;text-align:center;font-size:96px;'
                       'font-weight:900;color:%s;white-space:nowrap;'
                       'transform:rotate(-4.4deg)">%s</div>'
                       % (W, P["bg"] if P["accent"] != P["bg"] else "#fff",
                          cfg["hook"]))
    border = ""
    if P["border"]:
        border = ('<div style="position:absolute;inset:0;border:5px solid %s">'
                  '</div>' % P["border"])
    body = ('<div class="page"><svg class="art" width="%d" height="%d">%s</svg>'
            '%s%s%s%s%s%s</div>'
            % (W, H, art, panel, ribbon_text, html_text(cfg, L, P),
               html_badge(cfg, L, P), html_obi(cfg, L, P), border))
    # .page must be sized explicitly: with inset:0 it inherits the viewport,
    # which headless Chromium can make shorter than the page, and overflow
    # hidden then crops the obi off the foot of the cover.
    css = ("*{margin:0;padding:0;box-sizing:border-box}"
           "html,body{width:%dpx;height:%dpx;overflow:hidden;background:%s}"
           "body{font-family:'NSJP',sans-serif;-webkit-font-smoothing:antialiased}"
           ".page{position:absolute;left:0;top:0;width:%dpx;height:%dpx;"
           "overflow:hidden;background:%s}"
           "svg.art{position:absolute;left:0;top:0}"
           % (W, H, P["bg"], W, H, P["bg"]))
    html = ('<!doctype html><html lang="ja"><head><meta charset="utf-8">'
            '<style>%s%s</style></head><body>%s</body></html>'
            % (fonts, css, body))
    os.makedirs(out_dir, exist_ok=True)
    html_path = os.path.join(out_dir, stem + ".html")
    png = os.path.join(out_dir, stem + ".png")
    open(html_path, "w", encoding="utf-8").write(html)
    # Headless captures the viewport and pads the rest, and the viewport comes
    # out a little shorter than the window — which silently cropped the obi off
    # the foot. Give it a taller window and cut the page back to size.
    subprocess.run([chrome, "--headless=new", "--disable-gpu", "--no-sandbox",
                    "--hide-scrollbars", "--force-device-scale-factor=1",
                    "--window-size=%d,%d" % (W, H + 160),
                    "--virtual-time-budget=4000",
                    "--default-background-color=FFFFFFFF",
                    "--screenshot=" + png, "file://" + html_path],
                   check=True, capture_output=True)
    return save(png, out_dir, stem, "")


def save(png, out_dir, stem, note):
    from PIL import Image
    img = Image.open(png).convert("RGB")
    if img.size != (W, H):
        img = img.crop((0, 0, W, H))
    jpg = os.path.join(out_dir, stem + ".jpg")
    img.save(jpg, "JPEG", quality=92, subsampling=0, optimize=True)
    img.resize((180, int(180 * H / W)), Image.LANCZOS).save(
        os.path.join(out_dir, stem + "-thumb.png"))
    print("  %-38s %5.0f KB%s" % (os.path.basename(jpg),
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


def pil_art(d, cfg, L, P, fonts):
    kind = L["art"]
    if kind == "pitch":
        p, ink, lw = PITCH, rgb(art(P)), PITCH["line"]
        d.line([(0, p["goal_line"]), (W, p["goal_line"])], fill=ink, width=lw)
        for x1, y1, x2, y2 in (p["box"], p["goal_area"]):
            d.line([(x1, y1), (x1, y2), (x2, y2), (x2, y1)], fill=ink, width=lw)
        x1, y1, x2, y2 = p["goal"]
        d.rectangle([x1, y1, x2, y2], outline=ink, width=lw + 4)
        cx, cy = p["spot"]
        d.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=ink)
        r = p["arc_r"]
        d.arc([cx - r, cy + 60 - r, cx + r, cy + 60 + r], 0, 180, fill=ink,
              width=lw)
        cr, gl = p["corner_r"], p["goal_line"]
        d.arc([-cr, gl - cr, cr, gl + cr], 0, 90, fill=ink, width=lw)
        d.arc([W - cr, gl - cr, W + cr, gl + cr], 90, 180, fill=ink, width=lw)
    elif kind == "night":
        base = rgb(P["bg"])
        for i, (x, spread) in enumerate([(230, 150), (640, 190), (1060, 190),
                                         (1400, 150)]):
            fill = blend(rgb(P["accent"]), base, .10 - i * .01)
            d.polygon([(x - 34, -40), (x + 34, -40),
                       (x + spread * 2.4, 1180), (x - spread * 2.4, 1180)],
                      fill=fill)
            d.rectangle([x - 34, 20, x + 34, 72], fill=rgb(P["accent"]))
        ink = blend(rgb(art(P)), base, .85)
        d.line([(0, 1010), (W, 1010)], fill=ink, width=8)
        d.arc([560, 770, 1040, 1250], 0, 180, fill=ink, width=8)
    elif kind == "stripe":
        dark = rgb(mix(P["bg"], "#000000", .3))
        for i in range(9):
            if i % 2:
                d.rectangle([i * 180, 0, i * 180 + 180, 1180], fill=dark)
        d.rectangle([0, 1096, W, 1180], fill=rgb(P["accent"]))
    elif kind == "board":
        b, line = BOARD, rgb(art(P, .12))
        for x in range(0, W, b["grid"]):
            d.line([(x, 0), (x, 1180)], fill=line, width=2)
        for y in range(0, 1180, b["grid"]):
            d.line([(0, y), (W, y)], fill=line, width=2)
        labels, chip = board_rows(cfg), rgb(art(P, .16))
        accent = rgb(P["accent"])
        if labels:
            n, top = len(labels), chip_top(len(labels))
            step = int(520 / max(n - 1, 1))
            f = pil_font(fonts, 700, 44)
            for i, lab in enumerate(labels):
                y = top + i * (b["chip_h"] + b["gap"])
                x1, x2 = b["left"] + i * step // 2, b["right"] - i * step // 2
                d.rectangle([x1, y, x2, y + b["chip_h"]], fill=chip)
                d.rectangle([x1, y, x1 + 10, y + b["chip_h"]], fill=accent)
                d.text(((x1 + x2) / 2, y + b["chip_h"] / 2), "　".join(lab),
                       font=f, fill=rgb(art(P)), anchor="mm")
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
                    x, y = left + c * (cell + gap), 320 + r * (cell + gap)
                    d.rectangle([x, y, x + cell, y + cell],
                                fill=accent if (r, c) in marked else chip)
    elif kind == "formation":
        d.rectangle([0, 0, W, 1180], fill=rgb(art(P, .05)))
        line = rgb(art(P, .3))
        for a, b in FORMATION_LINKS:
            d.line([FORMATION[a], FORMATION[b]], fill=line, width=4)
        for i, (x, y) in enumerate(FORMATION):
            fill = rgb(P["accent"] if i in (0, 10) else art(P, .88))
            d.ellipse([x - 36, y - 36, x + 36, y + 36], fill=fill)
    elif kind == "cycle":
        cx, cy, r = 800, 620, 372
        labels = board_rows(cfg) or ["", "", "", ""]
        d.ellipse([cx - r, cy - r, cx + r, cy + r],
                  outline=rgb(art(P, .22)), width=16)
        f = pil_font(fonts, 700, 42)
        for i, lab in enumerate(labels):
            a = math.pi * 2 * i / len(labels) - math.pi / 2
            x, y = cx + r * math.cos(a), cy + r * math.sin(a)
            d.ellipse([x - 30, y - 30, x + 30, y + 30], fill=rgb(P["accent"]))
            lx, ly = cx + (r + 96) * math.cos(a), cy + (r + 96) * math.sin(a)
            anchor = "mm" if abs(math.cos(a)) < .3 else (
                "lm" if math.cos(a) > 0 else "rm")
            d.text((lx, ly), lab, font=f, fill=rgb(art(P, .85)), anchor=anchor)
        nums = cfg.get("diagram_numbers") or []
        if nums:
            d.text((cx, cy), nums[0], font=pil_font(fonts, 900, 132),
                   fill=rgb(P["accent"]), anchor="mm")
    elif kind == "ribbon":
        d.polygon([(0, 300), (W, 180), (W, 470), (0, 590)],
                  fill=rgb(P["accent"]))
        if cfg.get("hook"):
            d.text((W / 2, 385), cfg["hook"], font=pil_font(fonts, 900, 96),
                   fill=rgb(P["bg"]) if P["accent"] != P["bg"] else (255,) * 3,
                   anchor="mm")
    elif kind == "frame":
        d.rectangle([64, 64, W - 64, H - 64], outline=rgb(P["accent"]), width=26)
        d.rectangle([132, 132, W - 132, H - 132],
                    outline=rgb(art(P, .35)), width=4)
    elif kind == "number":
        num = big_number(cfg)
        if num:
            size = numeral_size(num)
            d.text((W / 2, 620 + size / 2), num,
                   font=pil_font(fonts, 900, size), fill=rgb(art(P, .1)),
                   anchor="ms")


def render_pil(cfg, name, idx, fonts, out_dir, stem):
    from PIL import Image, ImageDraw
    L, P = LAYOUTS[name], palette(name, idx)
    P["_t2"] = L.get("t2", "ink")
    img = Image.new("RGB", (W, H), rgb(P["bg"]))
    d = ImageDraw.Draw(img)
    pil_art(d, cfg, L, P, fonts)
    if L["panel"]:
        d.rectangle([0, L["panel"], W, H], fill=rgb(P["paper"]))

    bgc = rgb(P["paper"] if L["panel"] else P["bg"])
    values = text_values(cfg)
    for key, spec in TEXT[L["text"]].items():
        x, y, size, lh, weight, role, align = spec
        lines = [l for l in values.get(key, []) if l]
        if not lines:
            continue
        color, alpha = resolve(role, P)
        fill = blend(rgb(color), bgc, alpha)
        f = pil_font(fonts, weight, size)
        anchor = "la" if align == "left" else "ma"
        ax = x if align == "left" else W / 2
        pad = (lh - 1) * size / 2
        for i, line in enumerate(lines):
            d.text((ax, y + pad + i * size * lh), line, font=f, fill=fill,
                   anchor=anchor)

    lines = cfg.get("badge") or []
    if lines:
        cx, cy, r = L["badge"]
        d.polygon(badge_points(cx, cy, r),
                  fill=rgb(cfg.get("badge_color", P["badge"])))
        size = int(r * 0.33)
        f = pil_font(fonts, 900, size)
        step = size * 1.34
        y0 = cy - step * (len(lines) - 1) / 2
        for i, line in enumerate(lines):
            d.text((cx, y0 + i * step), line, font=f, fill=(255, 255, 255),
                   anchor="mm")

    y = L["obi_y"]
    d.rectangle([0, y, W, H], fill=rgb(P["obi_bg"]))
    line = obi_line(cfg)
    if line:
        d.text((110, y + 88), line, font=pil_font(fonts, 700, 48),
               fill=rgb(P["obi_fg"]), anchor="la")
    if P["border"]:
        for i in range(5):
            d.rectangle([i, i, W - 1 - i, H - 1 - i], outline=rgb(P["border"]))

    os.makedirs(out_dir, exist_ok=True)
    png = os.path.join(out_dir, stem + ".png")
    img.save(png)
    return save(png, out_dir, stem, "  (pillow)")


# ------------------------------------------------------------------- main

def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    cfg_path = args[0] if args else "book.json"
    seed = None
    for a in argv:
        if a.startswith("--seed"):
            seed = a.split("=", 1)[1] if "=" in a else argv[argv.index(a) + 1]

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
    if seed is None:
        seed = cover.get("seed", 1)

    explicit = cover.get("layouts")
    chosen = ([(n, 0) if isinstance(n, str) else tuple(n) for n in explicit]
              if explicit else pick_layouts(cover, seed))

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
    print("covers (seed %s):" % seed)
    for name, idx in chosen:
        if name not in LAYOUTS:
            print("  ! unknown layout %r — skipped" % name)
            continue
        stem = "%s-%s" % (cover["slug"], name)
        if use_pil:
            render_pil(cover, name, idx, fonts, out_dir, stem)
        else:
            render_html(cover, name, idx, fonts, out_dir, chrome, stem)
    if not explicit:
        print("  別の3案が見たいときは --seed 2 （book.json の cover.seed でも可）")


if __name__ == "__main__":
    main(sys.argv[1:])
