#!/usr/bin/env python3
"""
Europe Scout Map Generator for STVV 2025-2026 Season – Logo Edition
Uses actual club logos (circular-masked) downloaded from Wikimedia/Wikipedia.
Falls back to colored circle badges when logos are unavailable.
"""
import os
import math
import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.font_manager as _fm
_cjk_path = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
_fm.fontManager.addfont(_cjk_path)
import matplotlib.pyplot as plt
matplotlib.rcParams['font.family'] = ['Noto Sans CJK JP', 'DejaVu Sans']
from matplotlib.patches import Circle, FancyBboxPatch
from matplotlib.patches import Polygon as MplPolygon
import matplotlib.patheffects as pe
from matplotlib.offsetbox import AnnotationBbox, OffsetImage

from PIL import Image, ImageDraw, ImageFont
import io

# ─── Club Data ────────────────────────────────────────────────────────────────
# (abbr, full_name, city, lat, lon, logo_file_abbr, bg_color, fg_color)
# Note: KÖN logo was saved as KÖN.png but fallback key is "KÖN"
CLUBS = [
    ("STVV",  "Sint-Truidense VV",        "Sint-Truiden",     50.82,  5.17, "STVV",  "#FFDD00", "#000000"),
    ("HSV",   "Hamburger SV",             "Hamburg",          53.55, 10.00, "HSV",   "#009EE0", "#FFFFFF"),
    ("FCSP",  "FC St. Pauli",             "Hamburg",          53.58, 10.04, "FCSP",  "#824F20", "#FFFFFF"),
    ("D98",   "SV Darmstadt 98",          "Darmstadt",        49.87,  8.65, "D98",   "#3D52B2", "#FFFFFF"),
    ("B04",   "Bayer Leverkusen",         "Leverkusen",       51.03,  7.00, "B04",   "#E32221", "#FFFFFF"),
    ("KÖN",   "FC Köln",                  "Cologne",          50.94,  6.96, "KÖN",   "#FF2000", "#FFFFFF"),
    ("F95",   "Fortuna Düsseldorf",       "Düsseldorf",       51.22,  6.78, "F95",   "#D2000B", "#FFFFFF"),
    ("BMG",   "Borussia Mönchengladbach", "Mönchengladbach",  51.19,  6.44, "BMG",   "#000000", "#FFFFFF"),
    ("S04",   "FC Schalke 04",            "Gelsenkirchen",    51.57,  7.07, "S04",   "#004E9E", "#FFFFFF"),
    ("BVB",   "Borussia Dortmund",        "Dortmund",         51.51,  7.47, "BVB",   "#FDE100", "#000000"),
    ("WOB",   "VfL Wolfsburg",            "Wolfsburg",        52.42, 10.79, "WOB",   "#65B32E", "#000000"),
    ("SVW",   "Werder Bremen",            "Bremen",           53.08,  8.81, "SVW",   "#1D9053", "#FFFFFF"),
    ("KSC",   "Karlsruher SC",            "Karlsruhe",        49.00,  8.40, "KSC",   "#009EE0", "#FFFFFF"),
    ("FCK",   "1. FC Kaiserslautern",     "Kaiserslautern",   49.44,  7.77, "FCK",   "#E2001A", "#FFFFFF"),
    ("FCN",   "1. FC Nürnberg",           "Nuremberg",        49.45, 11.08, "FCN",   "#A0071B", "#FFFFFF"),
    ("RBL",   "RB Leipzig",               "Leipzig",          51.34, 13.38, "RBL",   "#DD0741", "#FFFFFF"),
    ("SGE",   "Eintracht Frankfurt",      "Frankfurt",        50.11,  8.68, "SGE",   "#E1000F", "#000000"),
    ("SCF",   "SC Freiburg",              "Freiburg",         47.99,  7.85, "SCF",   "#E50019", "#000000"),
    ("TSG",   "TSG Hoffenheim",           "Sinsheim",         49.24,  8.89, "TSG",   "#1865A4", "#FFFFFF"),
    ("FCA",   "FC Augsburg",              "Augsburg",         48.37, 10.90, "FCA",   "#BA3733", "#FFFFFF"),
    ("FCU",   "1. FC Union Berlin",       "Berlin",           52.47, 13.33, "FCU",   "#EB1923", "#FFFFFF"),
    ("BSC",   "Hertha BSC",               "Berlin",           52.57, 13.46, "BSC",   "#005CA9", "#FFFFFF"),
    ("VFB",   "VfB Stuttgart",            "Stuttgart",        48.78,  9.18, "VFB",   "#E32219", "#FFFFFF"),
    ("AJX",   "AFC Ajax",                 "Amsterdam",        52.31,  4.94, "AJX",   "#E2001A", "#FFFFFF"),
    ("FCU2",  "FC Utrecht",               "Utrecht",          52.09,  5.12, "FCU2",  "#CC0000", "#FFFF00"),
    ("AZ",    "AZ Alkmaar",               "Alkmaar",          52.63,  4.75, "AZ",    "#FF0000", "#FFFFFF"),
    ("FEY",   "Feyenoord",                "Rotterdam",        51.89,  4.52, "FEY",   "#CC0000", "#FFFFFF"),
    ("PSV",   "PSV Eindhoven",            "Eindhoven",        51.44,  5.48, "PSV",   "#E40613", "#FFFFFF"),
    ("FCT",   "FC Twente",                "Enschede",         52.22,  6.90, "FCT",   "#E2001A", "#FFFFFF"),
    ("SFC",   "Southampton FC",           "Southampton",      50.91, -1.40, "SFC",   "#D71920", "#FFFFFF"),
    ("COV",   "Coventry City",            "Coventry",         52.41, -1.51, "COV",   "#75AADB", "#FFFFFF"),
    ("OXF",   "Oxford United",            "Oxford",           51.75, -1.25, "OXF",   "#FFD700", "#000000"),
    ("QPR",   "Queens Park Rangers",      "London",           51.44, -0.23, "QPR",   "#1D5BA4", "#FFFFFF"),
    ("MIL",   "Millwall FC",              "London",           51.49, -0.05, "MIL",   "#001D5E", "#FFFFFF"),
    ("NUFC",  "Newcastle United",         "Newcastle",        54.98, -1.62, "NUFC",  "#000000", "#FFFFFF"),
    ("MUFC",  "Manchester United",        "Manchester",       53.46, -2.29, "MUFC",  "#DA020E", "#FFE500"),
    ("WHU",   "West Ham United",          "London",           51.54,  0.02, "WHU",   "#7A263A", "#FFFFFF"),
    ("THFC",  "Tottenham Hotspur",        "London",           51.62, -0.07, "THFC",  "#132257", "#FFFFFF"),
    ("WWFC",  "Wolverhampton Wanderers",  "Wolverhampton",    52.59, -2.13, "WWFC",  "#FDB913", "#231F20"),
    ("LCFC",  "Leicester City",           "Leicester",        52.64, -1.13, "LCFC",  "#003090", "#FFFFFF"),
    ("LUFC",  "Leeds United",             "Leeds",            53.80, -1.55, "LUFC",  "#1D428A", "#FFCD00"),
    ("BFC",   "Burnley FC",               "Burnley",          53.79, -2.24, "BFC",   "#6C1D45", "#FFFFFF"),
    ("WAT",   "Watford FC",               "Watford",          51.66, -0.40, "WAT",   "#FBEE23", "#ED2127"),
    ("PNE",   "Preston North End",        "Preston",          53.76, -2.70, "PNE",   "#FFFFFF", "#005C97"),
    ("RFC",   "Rangers FC",               "Glasgow",          55.86, -4.26, "RFC",   "#0000FF", "#FFFFFF"),
    ("AJA",   "AJ Auxerre",               "Auxerre",          47.80,  3.57, "AJA",   "#FFFFFF", "#DA251D"),
    ("LOSC",  "LOSC Lille",               "Lille",            50.63,  3.06, "LOSC",  "#E31E25", "#FFFFFF"),
    ("PSG",   "Paris Saint-Germain",      "Paris",            48.87,  2.33, "PSG",   "#004170", "#FFFFFF"),
    ("PFC",   "Paris FC",                 "Paris",            48.83,  2.38, "PFC",   "#002D5E", "#FFFFFF"),
    ("SRFC",  "Stade Rennais",            "Rennes",           48.11, -1.68, "SRFC",  "#000000", "#DA291C"),
    ("FCL",   "FC Lorient",               "Lorient",          47.75, -3.37, "FCL",   "#F47920", "#000000"),
    ("OL",    "Olympique Lyonnais",       "Lyon",             45.75,  4.83, "OL",    "#002855", "#CC0033"),
    ("CF63",  "Clermont Foot",            "Clermont-Ferrand", 45.78,  3.08, "CF63",  "#AB192B", "#FFFFFF"),
    ("SDR",   "Stade de Reims",           "Reims",            49.26,  4.03, "SDR",   "#E30613", "#FFFFFF"),
    ("TFC",   "Toulouse FC",              "Toulouse",         43.60,  1.44, "TFC",   "#7B2D8B", "#FFFFFF"),
    ("COM",   "FC Como",                  "Como",             45.81,  9.09, "COM",   "#0033A0", "#FFFFFF"),
    ("TOR",   "Torino FC",                "Turin",            45.07,  7.69, "TOR",   "#8B1A1A", "#FFFFFF"),
    ("SASU",  "U.S. Sassuolo",            "Sassuolo",         44.54, 10.79, "SASU",  "#2D6741", "#000000"),
    ("BOL",   "Bologna FC",               "Bologna",          44.50, 11.34, "BOL",   "#003591", "#FFFFFF"),
    ("HVR",   "Hellas Verona",            "Verona",           45.44, 10.99, "HVR",   "#FFD700", "#003399"),
    ("FIOR",  "ACF Fiorentina",           "Florence",         43.78, 11.25, "FIOR",  "#4C247D", "#FFFFFF"),
    ("ATA",   "Atalanta BC",              "Bergamo",          45.70,  9.67, "ATA",   "#1E3E85", "#FFFFFF"),
    ("INTER", "FC Internazionale",        "Milan",            45.46,  9.17, "INTER", "#0068A8", "#000000"),
    ("ACM",   "AC Milan",                 "Milan",            45.50,  9.22, "ACM",   "#FB090B", "#000000"),
    ("CREM",  "U.S. Cremonese",           "Cremona",          45.13, 10.02, "CREM",  "#9B1730", "#FFFFFF"),
    ("PAR",   "Parma Calcio",             "Parma",            44.80, 10.33, "PAR",   "#0058A0", "#FFD700"),
    ("GEN",   "Genoa CFC",                "Genoa",            44.41,  8.93, "GEN",   "#CC0000", "#003399"),
    ("MON",   "AC Monza",                 "Monza",            45.58,  9.27, "MON",   "#CC0000", "#FFFFFF"),
    ("CAG",   "Cagliari Calcio",          "Cagliari",         39.22,  9.12, "CAG",   "#003595", "#FFFFFF"),
    ("LEV",   "Levante UD",               "Valencia",         39.47, -0.38, "LEV",   "#0047AB", "#FFFFFF"),
    ("BETIS", "Real Betis",               "Seville",          37.36, -5.99, "BETIS", "#00833F", "#FFFFFF"),
    ("RSO",   "Real Sociedad",            "San Sebastián",    43.32, -1.98, "RSO",   "#0067B1", "#FFFFFF"),
    ("OSA",   "CA Osasuna",               "Pamplona",         42.82, -1.65, "OSA",   "#CC0000", "#003366"),
    ("RSPG",  "Real Sporting de Gijón",   "Gijón",            43.55, -5.66, "RSPG",  "#CC0000", "#FFFFFF"),
    ("RAPID", "SK Rapid Wien",            "Vienna",           48.21, 16.37, "RAPID", "#007A3D", "#FFFFFF"),
    ("SLA",   "SK Slavia Prague",         "Prague",           50.08, 14.44, "SLA",   "#CC0000", "#FFFFFF"),
    ("FKP",   "FC Viktoria Plzeň",        "Plzeň",            49.74, 13.37, "FKP",   "#002D62", "#FFFFFF"),
    ("CZV",   "FK Crvena Zvezda",         "Belgrade",         44.80, 20.46, "CZV",   "#CC0000", "#FFFFFF"),
    ("FCK2",  "FC København",             "Copenhagen",       55.68, 12.57, "FCK2",  "#0B479D", "#FFFFFF"),
]

LOGO_DIR = "/home/user/my-project/logos"

# ─── Map constants ────────────────────────────────────────────────────────────
LON_MIN, LON_MAX = -9.0, 25.0
LAT_MIN, LAT_MAX = 36.0, 58.5
FIG_W_IN = 22.0
FIG_H_IN = 12.375
DPI = 160

def to_xy(lat, lon):
    x = (lon - LON_MIN) / (LON_MAX - LON_MIN) * FIG_W_IN
    y = (lat - LAT_MIN) / (LAT_MAX - LAT_MIN) * FIG_H_IN
    return x, y

# ─── Logo image helpers ───────────────────────────────────────────────────────
def hex_to_rgba(h, a=255):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4)) + (a,)

def make_circular_logo(img_path, size_px=100, border_px=7, shadow=True):
    """Load image, crop to square, apply circular mask, add white border + shadow."""
    pad = border_px + (4 if shadow else 0)
    total = size_px + 2 * pad
    result = Image.new("RGBA", (total, total), (0, 0, 0, 0))

    # Shadow
    if shadow:
        s = Image.new("RGBA", (total, total), (0, 0, 0, 0))
        d = ImageDraw.Draw(s)
        off = 3
        d.ellipse([pad + off, pad + off, pad + size_px + off, pad + size_px + off],
                  fill=(0, 0, 0, 55))
        result = Image.alpha_composite(result, s)

    # White border ring
    ring = Image.new("RGBA", (total, total), (0, 0, 0, 0))
    d = ImageDraw.Draw(ring)
    d.ellipse([pad - border_px, pad - border_px,
               pad + size_px + border_px, pad + size_px + border_px],
              fill=(255, 255, 255, 255))
    result = Image.alpha_composite(result, ring)

    # Logo
    try:
        logo = Image.open(img_path).convert("RGBA")
    except Exception:
        logo = Image.new("RGBA", (size_px, size_px), (180, 180, 180, 255))

    # Crop to square (center)
    w, h = logo.size
    side = min(w, h)
    logo = logo.crop(((w - side) // 2, (h - side) // 2,
                       (w + side) // 2, (h + side) // 2))
    logo = logo.resize((size_px, size_px), Image.LANCZOS)

    # Circular mask
    mask = Image.new("L", (size_px, size_px), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, size_px - 1, size_px - 1], fill=255)

    logo_circ = Image.new("RGBA", (size_px, size_px), (0, 0, 0, 0))
    logo_circ.paste(logo, (0, 0), mask)
    result.paste(logo_circ, (pad, pad), mask)
    return result

def make_fallback_badge(abbr, bg_hex, fg_hex, size_px=100, border_px=7):
    """Colored circle fallback when logo not available."""
    pad = border_px + 4
    total = size_px + 2 * pad
    bg = hex_to_rgba(bg_hex)
    fg = hex_to_rgba(fg_hex)

    result = Image.new("RGBA", (total, total), (0, 0, 0, 0))

    # Shadow
    s = Image.new("RGBA", (total, total), (0, 0, 0, 0))
    ImageDraw.Draw(s).ellipse([pad+3, pad+3, pad+size_px+3, pad+size_px+3],
                               fill=(0, 0, 0, 55))
    result = Image.alpha_composite(result, s)

    # White ring
    ring = Image.new("RGBA", (total, total), (0, 0, 0, 0))
    ImageDraw.Draw(ring).ellipse([pad-border_px, pad-border_px,
                                  pad+size_px+border_px, pad+size_px+border_px],
                                 fill=(255, 255, 255, 255))
    result = Image.alpha_composite(result, ring)

    # Color circle
    circ = Image.new("RGBA", (total, total), (0, 0, 0, 0))
    ImageDraw.Draw(circ).ellipse([pad, pad, pad+size_px, pad+size_px], fill=bg)
    result = Image.alpha_composite(result, circ)

    # Text
    try:
        font_sz = max(14, size_px // 5)
        if len(abbr) > 4:
            font_sz = max(12, size_px // 6)
        font = ImageFont.truetype(_cjk_path, size=font_sz)
    except Exception:
        font = ImageFont.load_default()

    txt = Image.new("RGBA", (total, total), (0, 0, 0, 0))
    d = ImageDraw.Draw(txt)
    cx, cy = pad + size_px // 2, pad + size_px // 2
    bbox = d.textbbox((0, 0), abbr, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.text((cx - tw // 2, cy - th // 2), abbr, fill=fg, font=font)
    result = Image.alpha_composite(result, txt)
    return result

# ─── Build PIL images for each club ──────────────────────────────────────────
LOGO_SIZE  = 100  # regular
STVV_SIZE  = 180  # STVV larger

print("Building club images...")
club_images = {}
used_logos = []
used_fallback = []

for (abbr, full_name, city, lat, lon, logo_key, bg, fg) in CLUBS:
    is_stvv = (abbr == "STVV")
    sz = STVV_SIZE if is_stvv else LOGO_SIZE
    bpx = 9 if is_stvv else 7

    logo_path = os.path.join(LOGO_DIR, f"{logo_key}.png")
    if os.path.exists(logo_path):
        try:
            img = make_circular_logo(logo_path, size_px=sz, border_px=bpx)
            club_images[abbr] = img
            used_logos.append(abbr)
        except Exception as e:
            print(f"  Logo load failed for {abbr}: {e}, using fallback")
            club_images[abbr] = make_fallback_badge(abbr, bg, fg, size_px=sz, border_px=bpx)
            used_fallback.append(abbr)
    else:
        club_images[abbr] = make_fallback_badge(abbr, bg, fg, size_px=sz, border_px=bpx)
        used_fallback.append(abbr)

print(f"  Logos: {len(used_logos)}, Fallback: {len(used_fallback)}")
if used_fallback:
    print(f"  Fallback clubs: {', '.join(used_fallback)}")

# ─── Figure and axes ─────────────────────────────────────────────────────────
fig = plt.figure(figsize=(FIG_W_IN, FIG_H_IN), dpi=DPI)
ax = fig.add_axes([0, 0, 1, 1])
FW, FH = FIG_W_IN, FIG_H_IN

# ─── Sea background ───────────────────────────────────────────────────────────
ax.set_facecolor('#B4CDE6')
fig.patch.set_facecolor('#B4CDE6')
grad = np.linspace(0, 1, 500).reshape(1, -1)
ax.imshow(np.tile(grad, (300, 1)), extent=[0, FW, 0, FH], aspect='auto',
          cmap=plt.cm.Blues, vmin=-0.5, vmax=1.0, alpha=0.45, zorder=0)

# ─── Land outlines ────────────────────────────────────────────────────────────
EUROPE_OUTLINE = [
    (-9.0, 36.0), (-9.0, 37.5), (-8.5, 37.3), (-8.9, 38.5), (-9.5, 38.7),
    (-9.2, 39.5), (-8.6, 41.1), (-8.0, 42.0), (-7.0, 43.7), (-5.7, 43.6),
    (-3.8, 43.5), (-1.8, 43.4), (-1.7, 43.3),
    (-1.5, 46.8), (-1.0, 47.0), (-2.5, 47.7), (-4.5, 47.8), (-4.8, 48.4),
    (-4.0, 48.5), (-2.0, 48.7), (-1.5, 49.2), (-1.0, 49.6), (0.0, 49.4),
    (1.3, 50.8), (1.8, 50.9), (2.5, 51.0),
    (3.0, 51.4), (3.4, 51.4), (3.8, 51.6), (4.3, 51.9),
    (4.0, 52.4), (3.7, 53.0), (4.7, 53.0), (5.4, 53.4), (7.0, 53.7),
    (8.0, 55.0), (8.5, 55.2), (9.4, 54.8), (10.0, 55.0), (10.5, 57.7),
    (11.0, 57.6), (11.2, 56.0), (12.5, 56.1), (12.7, 55.5), (12.6, 55.0),
    (14.0, 54.0), (14.5, 54.0),
    (16.0, 54.5), (18.0, 54.8), (19.5, 54.4), (22.5, 54.4), (24.0, 55.0),
    (24.0, 58.5), (22.0, 58.5), (21.0, 57.5), (20.5, 56.5),
    (19.0, 54.5), (17.0, 51.0), (15.0, 50.5), (14.8, 50.2),
    (17.2, 48.0), (18.8, 47.8), (22.0, 48.4), (22.5, 49.0),
    (22.0, 46.0), (23.0, 45.5), (22.5, 44.5), (21.5, 44.0),
    (19.0, 43.5), (17.5, 43.0), (16.5, 43.5), (15.5, 44.0),
    (14.0, 45.1), (13.7, 45.8), (13.5, 45.6),
    (12.5, 45.5), (13.0, 45.6), (13.4, 45.8), (13.8, 44.4),
    (15.0, 41.0), (16.0, 40.0), (15.6, 38.2), (15.0, 37.0),
    (15.5, 36.6), (16.5, 37.8), (16.2, 39.0),
    (16.8, 41.2), (16.0, 41.5), (15.5, 42.0), (14.5, 43.0),
    (13.5, 44.5), (13.0, 45.0),
    (8.0, 44.0), (7.5, 43.8), (7.0, 43.7), (5.5, 43.3),
    (4.5, 43.4), (3.2, 43.5), (2.0, 42.5), (0.5, 42.7),
    (-0.5, 43.4), (-1.7, 43.3),
    (-1.8, 43.4), (-4.0, 43.5),
    (-8.0, 42.0), (-8.9, 38.5), (-9.0, 37.0), (-6.0, 36.0), (-5.3, 36.1),
    (-5.0, 36.0),
]
BRITAIN = [
    (-5.7, 50.0), (-5.0, 49.9), (-3.0, 50.2), (-1.0, 50.7), (0.5, 51.1),
    (0.7, 51.4), (1.0, 52.0), (0.5, 52.9), (0.2, 53.6), (-0.1, 53.8),
    (-1.0, 54.3), (-1.7, 55.1), (-2.0, 55.6), (-2.5, 56.0), (-3.0, 56.5),
    (-3.5, 57.3), (-4.5, 57.9), (-5.3, 58.3), (-5.0, 57.5), (-5.5, 56.8),
    (-5.5, 56.0), (-5.0, 55.5), (-4.0, 55.0), (-4.7, 54.2), (-3.5, 54.0),
    (-3.0, 53.4), (-3.0, 53.0), (-3.1, 51.5), (-4.0, 51.2), (-5.1, 51.6),
    (-5.7, 50.8), (-5.7, 50.0),
]
IRELAND = [
    (-6.0, 52.0), (-7.0, 52.2), (-8.5, 52.0), (-9.5, 51.5), (-10.0, 52.0),
    (-9.0, 53.5), (-8.0, 54.5), (-7.0, 55.0), (-6.0, 54.5), (-6.0, 54.0),
    (-5.8, 53.2), (-6.5, 52.5), (-6.0, 52.0),
]

def outline_to_xy(pts):
    return [((lon - LON_MIN) / (LON_MAX - LON_MIN) * FW,
             (lat - LAT_MIN) / (LAT_MAX - LAT_MIN) * FH)
            for lon, lat in pts]

def draw_land(pts, color='#E4EDD0', edge='#94B06A'):
    ax.add_patch(MplPolygon(outline_to_xy(pts), closed=True,
                            facecolor=color, edgecolor=edge, linewidth=0.8, zorder=1))

draw_land(EUROPE_OUTLINE)
draw_land(BRITAIN)
draw_land(IRELAND)

# Subtle graticule
for lat in range(37, 59, 3):
    ax.axhline((lat - LAT_MIN) / (LAT_MAX - LAT_MIN) * FH,
               color='white', lw=0.28, alpha=0.32, zorder=2)
for lon in range(-9, 26, 3):
    ax.axvline((lon - LON_MIN) / (LON_MAX - LON_MIN) * FW,
               color='white', lw=0.28, alpha=0.32, zorder=2)

# ─── Placement: golden-angle spiral de-overlap ───────────────────────────────
# Radius in figure-inch units for overlap detection
# Image total size in px = size + 2*(border + shadow_pad) ≈ size + 22
LOGO_R  = (LOGO_SIZE + 22) / (2.0 * DPI)
STVV_R  = (STVV_SIZE + 26) / (2.0 * DPI)

placed = []  # (cx, cy, r)

def overlaps(cx, cy, r, placed, gap=0.06):
    for px, py, pr in placed:
        if math.sqrt((cx - px)**2 + (cy - py)**2) < r + pr + gap:
            return True
    return False

def find_spot(lat, lon, r, attempts=90, spread=0.50):
    bx, by = to_xy(lat, lon)
    golden = 137.508
    for i in range(attempts):
        if i == 0:
            cx, cy = bx, by
        else:
            angle = (i * golden) % 360
            dist = spread * (0.22 + (i // 12) * 0.26)
            cx = bx + dist * math.cos(math.radians(angle))
            cy = by + dist * math.sin(math.radians(angle))
        cx = max(r + 0.04, min(FW - r - 0.04, cx))
        cy = max(r + 0.04, min(FH - r - 0.04, cy))
        if not overlaps(cx, cy, r, placed):
            return cx, cy, bx, by
    return bx, by, bx, by

# Sort: STVV first
clubs_sorted = sorted(CLUBS, key=lambda c: 0 if c[0] == "STVV" else 1)
badge_data = []
for (abbr, full_name, city, lat, lon, logo_key, bg, fg) in clubs_sorted:
    r = STVV_R if abbr == "STVV" else LOGO_R
    cx, cy, ox, oy = find_spot(lat, lon, r)
    placed.append((cx, cy, r))
    badge_data.append((abbr, cx, cy, ox, oy, r, abbr == "STVV"))

# ─── STVV pulse rings ─────────────────────────────────────────────────────────
stvv_cx, stvv_cy = next((cx, cy) for (a, cx, cy, *_) in badge_data if a == "STVV")
for ring_r, alpha in [(STVV_R * 1.4, 0.32), (STVV_R * 1.9, 0.18), (STVV_R * 2.5, 0.09)]:
    ax.add_patch(Circle((stvv_cx, stvv_cy), ring_r,
                        fill=False, edgecolor='#FFDD00',
                        linewidth=1.8, alpha=alpha, zorder=3))

# ─── Leader lines ─────────────────────────────────────────────────────────────
for (abbr, cx, cy, ox, oy, r, is_stvv) in badge_data:
    dist = math.sqrt((cx - ox)**2 + (cy - oy)**2)
    if dist > 0.07:
        ax.plot([cx, ox], [cy, oy], color='#3A3A3A', lw=0.65,
                alpha=0.55, zorder=3, solid_capstyle='round')
        ax.plot(ox, oy, 'o', ms=2.5, color='#222222', alpha=0.75, zorder=3)

# ─── Draw logo badges ─────────────────────────────────────────────────────────
for (abbr, cx, cy, ox, oy, r, is_stvv) in badge_data:
    pil_img = club_images[abbr]
    np_img = np.array(pil_img)
    zoom = 1.0 / DPI  # 1px in image → 1/DPI inches on figure
    oi = OffsetImage(np_img, zoom=zoom)
    oi.image.axes = ax
    ab = AnnotationBbox(oi, (cx, cy), xycoords='data',
                        frameon=False,
                        zorder=8 if is_stvv else 6,
                        pad=0)
    ax.add_artist(ab)

# ─── Title ────────────────────────────────────────────────────────────────────
title_y = FH - 0.38
ax.text(FW / 2, title_y,
        "2025−2026シーズンにスカウトに来たクラブ",
        ha='center', va='top', fontsize=26, fontweight='bold',
        color='#1A2A4A', transform=ax.transData, zorder=15,
        path_effects=[pe.withStroke(linewidth=5, foreground='white')])

# Sub-bar
bar_h = 0.27
bar_rect = FancyBboxPatch((0.15, title_y - bar_h - 0.44), FW - 0.30, bar_h,
                          boxstyle="round,pad=0.06",
                          facecolor='#1A2A4A', edgecolor='none',
                          alpha=0.78, zorder=14)
ax.add_patch(bar_rect)
ax.text(FW / 2, title_y - bar_h - 0.30,
        f"Sint-Truidense VV  ●  {len(CLUBS) - 1} clubs scouted",
        ha='center', va='center', fontsize=10, color='white',
        fontweight='semibold', transform=ax.transData, zorder=15)

# ─── North arrow ─────────────────────────────────────────────────────────────
ax.annotate("N", xy=(0.45, 0.80), xytext=(0.45, 0.55),
            ha='center', fontsize=9, fontweight='bold', color='#1A2A4A',
            arrowprops=dict(arrowstyle='->', color='#1A2A4A', lw=1.5),
            zorder=15)

# ─── Scale bar ────────────────────────────────────────────────────────────────
km500_fig = (500 / (111.32 * math.cos(math.radians(48)))) / (LON_MAX - LON_MIN) * FW
sb_x, sb_y = 0.30, 0.22
ax.plot([sb_x, sb_x + km500_fig], [sb_y, sb_y], color='#1A2A4A', lw=3, zorder=15)
ax.plot([sb_x, sb_x], [sb_y - 0.04, sb_y + 0.04], color='#1A2A4A', lw=2, zorder=15)
ax.plot([sb_x + km500_fig, sb_x + km500_fig], [sb_y - 0.04, sb_y + 0.04],
        color='#1A2A4A', lw=2, zorder=15)
ax.text(sb_x + km500_fig / 2, sb_y + 0.10, "500 km",
        ha='center', va='bottom', fontsize=7, color='#1A2A4A', zorder=15)

# ─── Finalize ────────────────────────────────────────────────────────────────
ax.set_xlim(0, FW)
ax.set_ylim(0, FH)
ax.set_aspect('equal')
ax.axis('off')

OUT = "/home/user/my-project/scout_map_logos.png"
print("Saving...")
plt.savefig(OUT, dpi=DPI, bbox_inches='tight', pad_inches=0,
            facecolor=fig.get_facecolor())
plt.close()
print(f"Saved → {OUT}")

print(f"\n=== Final Report ===")
print(f"Total clubs: {len(CLUBS)}")
print(f"Logos used: {len(used_logos)} — {', '.join(used_logos)}")
print(f"Fallback badges: {len(used_fallback)}")
if used_fallback:
    print(f"  Clubs with fallback: {', '.join(used_fallback)}")
