#!/usr/bin/env python3
"""
Europe Scout Map Generator for STVV 2025-2026 Season
Uses actual club logos downloaded from Wikimedia Commons via Wikipedia API.
"""
import os
import sys
import json
import math
import time
import urllib.request
import urllib.parse

import matplotlib
matplotlib.use('Agg')
import matplotlib.font_manager as _fm
_cjk_path = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
_fm.fontManager.addfont(_cjk_path)
import matplotlib.pyplot as plt
matplotlib.rcParams['font.family'] = ['Noto Sans CJK JP', 'DejaVu Sans']
import matplotlib.patches as mpatches
from matplotlib.patches import Circle, FancyBboxPatch
from matplotlib.patches import Polygon as MplPolygon
import matplotlib.patheffects as pe
import numpy as np
from matplotlib.offsetbox import AnnotationBbox, OffsetImage

from PIL import Image, ImageDraw, ImageOps
import io

# ─── Club Data ────────────────────────────────────────────────────────────────
CLUBS = [
    # (abbreviation, full_name, city, lat, lon, wiki_page, bg_color, fg_color)
    ("STVV",  "Sint-Truidense VV",       "Sint-Truiden",    50.82,  5.17, "Sint-Truidense_VV",              "#FFDD00", "#000000"),
    ("HSV",   "Hamburger SV",            "Hamburg",         53.55, 10.00, "Hamburger_SV",                   "#009EE0", "#FFFFFF"),
    ("FCSP",  "FC St. Pauli",            "Hamburg",         53.58, 10.04, "FC_St._Pauli",                   "#824F20", "#FFFFFF"),
    ("D98",   "SV Darmstadt 98",         "Darmstadt",       49.87,  8.65, "SV_Darmstadt_98",                "#3D52B2", "#FFFFFF"),
    ("B04",   "Bayer Leverkusen",        "Leverkusen",      51.03,  7.00, "Bayer_04_Leverkusen",            "#E32221", "#FFFFFF"),
    ("KÖN",   "FC Köln",                 "Cologne",         50.94,  6.96, "1._FC_Köln",                     "#FF2000", "#FFFFFF"),
    ("F95",   "Fortuna Düsseldorf",      "Düsseldorf",      51.22,  6.78, "Fortuna_Düsseldorf",             "#D2000B", "#FFFFFF"),
    ("BMG",   "Borussia Mönchengladbach","Mönchengladbach", 51.19,  6.44, "Borussia_Mönchengladbach",       "#000000", "#FFFFFF"),
    ("S04",   "FC Schalke 04",           "Gelsenkirchen",   51.57,  7.07, "FC_Schalke_04",                  "#004E9E", "#FFFFFF"),
    ("BVB",   "Borussia Dortmund",       "Dortmund",        51.51,  7.47, "Borussia_Dortmund",              "#FDE100", "#000000"),
    ("WOB",   "VfL Wolfsburg",           "Wolfsburg",       52.42, 10.79, "VfL_Wolfsburg",                  "#65B32E", "#000000"),
    ("SVW",   "Werder Bremen",           "Bremen",          53.08,  8.81, "Werder_Bremen",                  "#1D9053", "#FFFFFF"),
    ("KSC",   "Karlsruher SC",           "Karlsruhe",       49.00,  8.40, "Karlsruher_SC",                  "#009EE0", "#FFFFFF"),
    ("FCK",   "1. FC Kaiserslautern",    "Kaiserslautern",  49.44,  7.77, "1._FC_Kaiserslautern",           "#E2001A", "#FFFFFF"),
    ("FCN",   "1. FC Nürnberg",          "Nuremberg",       49.45, 11.08, "1._FC_Nürnberg",                 "#A0071B", "#FFFFFF"),
    ("RBL",   "RB Leipzig",              "Leipzig",         51.34, 13.38, "RB_Leipzig",                     "#DD0741", "#FFFFFF"),
    ("SGE",   "Eintracht Frankfurt",     "Frankfurt",       50.11,  8.68, "Eintracht_Frankfurt",            "#E1000F", "#000000"),
    ("SCF",   "SC Freiburg",             "Freiburg",        47.99,  7.85, "SC_Freiburg",                    "#E50019", "#000000"),
    ("TSG",   "TSG Hoffenheim",          "Sinsheim",        49.24,  8.89, "TSG_1899_Hoffenheim",            "#1865A4", "#FFFFFF"),
    ("FCA",   "FC Augsburg",             "Augsburg",        48.37, 10.90, "FC_Augsburg",                    "#BA3733", "#FFFFFF"),
    ("FCU",   "1. FC Union Berlin",      "Berlin",          52.47, 13.33, "1._FC_Union_Berlin",             "#EB1923", "#FFFFFF"),
    ("BSC",   "Hertha BSC",              "Berlin",          52.57, 13.46, "Hertha_BSC",                     "#005CA9", "#FFFFFF"),
    ("VFB",   "VfB Stuttgart",           "Stuttgart",       48.78,  9.18, "VfB_Stuttgart",                  "#E32219", "#FFFFFF"),
    ("AJX",   "AFC Ajax",                "Amsterdam",       52.31,  4.94, "AFC_Ajax",                       "#E2001A", "#FFFFFF"),
    ("FCU2",  "FC Utrecht",              "Utrecht",         52.09,  5.12, "FC_Utrecht",                     "#CC0000", "#FFFF00"),
    ("AZ",    "AZ Alkmaar",              "Alkmaar",         52.63,  4.75, "AZ_(football_club)",             "#FF0000", "#FFFFFF"),
    ("FEY",   "Feyenoord",               "Rotterdam",       51.89,  4.52, "Feyenoord",                      "#CC0000", "#FFFFFF"),
    ("PSV",   "PSV Eindhoven",           "Eindhoven",       51.44,  5.48, "PSV_Eindhoven",                  "#E40613", "#FFFFFF"),
    ("FCT",   "FC Twente",               "Enschede",        52.22,  6.90, "FC_Twente",                      "#E2001A", "#FFFFFF"),
    ("SFC",   "Southampton FC",          "Southampton",     50.91, -1.40, "Southampton_F.C.",                "#D71920", "#FFFFFF"),
    ("COV",   "Coventry City",           "Coventry",        52.41, -1.51, "Coventry_City_F.C.",             "#75AADB", "#FFFFFF"),
    ("OXF",   "Oxford United",           "Oxford",          51.75, -1.25, "Oxford_United_F.C.",             "#FFD700", "#000000"),
    ("QPR",   "Queens Park Rangers",     "London",          51.44, -0.23, "Queens_Park_Rangers_F.C.",       "#1D5BA4", "#FFFFFF"),
    ("MIL",   "Millwall FC",             "London",          51.49, -0.05, "Millwall_F.C.",                  "#001D5E", "#FFFFFF"),
    ("NUFC",  "Newcastle United",        "Newcastle",       54.98, -1.62, "Newcastle_United_F.C.",          "#000000", "#FFFFFF"),
    ("MUFC",  "Manchester United",       "Manchester",      53.46, -2.29, "Manchester_United_F.C.",         "#DA020E", "#FFE500"),
    ("WHU",   "West Ham United",         "London",          51.54,  0.02, "West_Ham_United_F.C.",           "#7A263A", "#FFFFFF"),
    ("THFC",  "Tottenham Hotspur",       "London",          51.62, -0.07, "Tottenham_Hotspur_F.C.",         "#132257", "#FFFFFF"),
    ("WWFC",  "Wolverhampton Wanderers", "Wolverhampton",   52.59, -2.13, "Wolverhampton_Wanderers_F.C.",   "#FDB913", "#231F20"),
    ("LCFC",  "Leicester City",          "Leicester",       52.64, -1.13, "Leicester_City_F.C.",            "#003090", "#FFFFFF"),
    ("LUFC",  "Leeds United",            "Leeds",           53.80, -1.55, "Leeds_United_F.C.",              "#1D428A", "#FFCD00"),
    ("BFC",   "Burnley FC",              "Burnley",         53.79, -2.24, "Burnley_F.C.",                   "#6C1D45", "#FFFFFF"),
    ("WAT",   "Watford FC",              "Watford",         51.66, -0.40, "Watford_F.C.",                   "#FBEE23", "#ED2127"),
    ("PNE",   "Preston North End",       "Preston",         53.76, -2.70, "Preston_North_End_F.C.",         "#FFFFFF", "#005C97"),
    ("RFC",   "Rangers FC",              "Glasgow",         55.86, -4.26, "Rangers_F.C.",                   "#0000FF", "#FFFFFF"),
    ("AJA",   "AJ Auxerre",              "Auxerre",         47.80,  3.57, "AJ_Auxerre",                     "#FFFFFF", "#DA251D"),
    ("LOSC",  "LOSC Lille",              "Lille",           50.63,  3.06, "Lille_OSC",                      "#E31E25", "#FFFFFF"),
    ("PSG",   "Paris Saint-Germain",     "Paris",           48.87,  2.33, "Paris_Saint-Germain_F.C.",       "#004170", "#FFFFFF"),
    ("PFC",   "Paris FC",                "Paris",           48.83,  2.38, "Paris_FC",                       "#002D5E", "#FFFFFF"),
    ("SRFC",  "Stade Rennais",           "Rennes",          48.11, -1.68, "Stade_Rennais_F.C.",             "#000000", "#DA291C"),
    ("FCL",   "FC Lorient",              "Lorient",         47.75, -3.37, "FC_Lorient",                     "#F47920", "#000000"),
    ("OL",    "Olympique Lyonnais",      "Lyon",            45.75,  4.83, "Olympique_Lyonnais",             "#002855", "#CC0033"),
    ("CF63",  "Clermont Foot",           "Clermont-Ferrand",45.78,  3.08, "Clermont_Foot_63",               "#AB192B", "#FFFFFF"),
    ("SDR",   "Stade de Reims",          "Reims",           49.26,  4.03, "Stade_de_Reims",                 "#E30613", "#FFFFFF"),
    ("TFC",   "Toulouse FC",             "Toulouse",        43.60,  1.44, "Toulouse_FC",                    "#7B2D8B", "#FFFFFF"),
    ("COM",   "FC Como",                 "Como",            45.81,  9.09, "Como_1907",                      "#0033A0", "#FFFFFF"),
    ("TOR",   "Torino FC",               "Turin",           45.07,  7.69, "Torino_F.C.",                    "#8B1A1A", "#FFFFFF"),
    ("SASU",  "U.S. Sassuolo",           "Sassuolo",        44.54, 10.79, "U.S._Sassuolo_Calcio",           "#2D6741", "#000000"),
    ("BOL",   "Bologna FC",              "Bologna",         44.50, 11.34, "Bologna_F.C._1909",              "#003591", "#FFFFFF"),
    ("HVR",   "Hellas Verona",           "Verona",          45.44, 10.99, "Hellas_Verona_F.C.",             "#FFD700", "#003399"),
    ("FIOR",  "ACF Fiorentina",          "Florence",        43.78, 11.25, "ACF_Fiorentina",                 "#4C247D", "#FFFFFF"),
    ("ATA",   "Atalanta BC",             "Bergamo",         45.70,  9.67, "Atalanta_B.C.",                  "#1E3E85", "#FFFFFF"),
    ("INTER", "FC Internazionale",       "Milan",           45.46,  9.17, "FC_Internazionale_Milano",       "#0068A8", "#000000"),
    ("ACM",   "AC Milan",                "Milan",           45.50,  9.22, "A.C._Milan",                     "#FB090B", "#000000"),
    ("CREM",  "U.S. Cremonese",          "Cremona",         45.13, 10.02, "U.S._Cremonese",                 "#9B1730", "#FFFFFF"),
    ("PAR",   "Parma Calcio",            "Parma",           44.80, 10.33, "Parma_Calcio_1913",              "#0058A0", "#FFD700"),
    ("GEN",   "Genoa CFC",               "Genoa",           44.41,  8.93, "Genoa_C.F.C.",                   "#CC0000", "#003399"),
    ("MON",   "AC Monza",                "Monza",           45.58,  9.27, "A.C._Monza",                     "#CC0000", "#FFFFFF"),
    ("CAG",   "Cagliari Calcio",         "Cagliari",        39.22,  9.12, "Cagliari_Calcio",                "#003595", "#FFFFFF"),
    ("LEV",   "Levante UD",              "Valencia",        39.47, -0.38, "Levante_UD",                     "#0047AB", "#FFFFFF"),
    ("BETIS", "Real Betis",              "Seville",         37.36, -5.99, "Real_Betis",                     "#00833F", "#FFFFFF"),
    ("RSO",   "Real Sociedad",           "San Sebastián",   43.32, -1.98, "Real_Sociedad",                  "#0067B1", "#FFFFFF"),
    ("OSA",   "CA Osasuna",              "Pamplona",        42.82, -1.65, "CA_Osasuna",                     "#CC0000", "#003366"),
    ("RSPG",  "Real Sporting de Gijón",  "Gijón",           43.55, -5.66, "Real_Sporting_de_Gijón",         "#CC0000", "#FFFFFF"),
    ("RAPID", "SK Rapid Wien",           "Vienna",          48.21, 16.37, "SK_Rapid_Wien",                  "#007A3D", "#FFFFFF"),
    ("SLA",   "SK Slavia Prague",        "Prague",          50.08, 14.44, "SK_Slavia_Prague",               "#CC0000", "#FFFFFF"),
    ("FKP",   "FC Viktoria Plzeň",       "Plzeň",           49.74, 13.37, "FC_Viktoria_Plzeň",              "#002D62", "#FFFFFF"),
    ("CZV",   "FK Crvena Zvezda",        "Belgrade",        44.80, 20.46, "FK_Crvena_zvezda",               "#CC0000", "#FFFFFF"),
    ("FCK2",  "FC København",            "Copenhagen",      55.68, 12.57, "FC_Copenhagen",                  "#0B479D", "#FFFFFF"),
]

# ─── Map extent ───────────────────────────────────────────────────────────────
LON_MIN, LON_MAX = -9.0, 25.0
LAT_MIN, LAT_MAX = 36.0, 58.5

# ─── Figure setup ─────────────────────────────────────────────────────────────
FIG_W_IN = 22.0
FIG_H_IN = 12.375  # 16:9
DPI = 160

# ─── Coordinate transform ─────────────────────────────────────────────────────
def to_xy(lat, lon):
    x = (lon - LON_MIN) / (LON_MAX - LON_MIN) * FIG_W_IN
    y = (lat - LAT_MIN) / (LAT_MAX - LAT_MIN) * FIG_H_IN
    return x, y

# ─── Logo download ────────────────────────────────────────────────────────────
LOGO_DIR = "/home/user/my-project/logos"
os.makedirs(LOGO_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "STVV-ScoutMap/1.0 (scout-map-generator; contact@example.com)"
}

def fetch_url(url, timeout=15):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()

def get_wiki_logo_url(wiki_page, thumb_size=200):
    """Query Wikipedia API to get the page image URL."""
    api = (
        "https://en.wikipedia.org/w/api.php"
        f"?action=query&titles={urllib.parse.quote(wiki_page)}"
        f"&prop=pageimages&format=json&pithumbsize={thumb_size}"
    )
    data = json.loads(fetch_url(api))
    pages = data.get("query", {}).get("pages", {})
    for page in pages.values():
        thumb = page.get("thumbnail", {})
        if thumb:
            return thumb.get("source")
    return None

def download_logo(abbr, wiki_page):
    """Download logo for a club. Returns path if success, None if failed."""
    out_path = os.path.join(LOGO_DIR, f"{abbr}.png")
    if os.path.exists(out_path):
        print(f"  [CACHED] {abbr}")
        return out_path
    try:
        url = get_wiki_logo_url(wiki_page, thumb_size=200)
        if not url:
            print(f"  [FAIL-NO-URL] {abbr} ({wiki_page})")
            return None
        img_data = fetch_url(url)
        img = Image.open(io.BytesIO(img_data)).convert("RGBA")
        img.save(out_path)
        print(f"  [OK] {abbr} ← {url}")
        return out_path
    except Exception as e:
        print(f"  [FAIL] {abbr} ({wiki_page}): {e}")
        return None

# ─── Download all logos ───────────────────────────────────────────────────────
print("=== Downloading logos ===")
logo_paths = {}
failed_logos = []

for (abbr, full_name, city, lat, lon, wiki_page, bg, fg) in CLUBS:
    path = download_logo(abbr, wiki_page)
    if path:
        logo_paths[abbr] = path
    else:
        failed_logos.append(abbr)
    time.sleep(0.1)  # be polite to Wikipedia

print(f"\nDownloaded: {len(logo_paths)}/{len(CLUBS)}")
if failed_logos:
    print(f"Failed: {failed_logos}")

# ─── Make circular-masked logo image ─────────────────────────────────────────
def make_circular_logo(img_path, size_px=120, border_px=6, border_color=(255,255,255,255), shadow=True):
    """
    Load an image, make it circular with a white border ring.
    Returns a PIL RGBA image (square, size_px+border+shadow).
    """
    pad = border_px + (4 if shadow else 0)
    total = size_px + 2 * pad

    result = Image.new("RGBA", (total, total), (0, 0, 0, 0))

    # Shadow
    if shadow:
        shadow_img = Image.new("RGBA", (total, total), (0, 0, 0, 0))
        sdraw = ImageDraw.Draw(shadow_img)
        off = 3
        sdraw.ellipse(
            [pad + off, pad + off, pad + size_px + off, pad + size_px + off],
            fill=(0, 0, 0, 60)
        )
        result = Image.alpha_composite(result, shadow_img)

    # White border ring
    ring_img = Image.new("RGBA", (total, total), (0, 0, 0, 0))
    rdraw = ImageDraw.Draw(ring_img)
    rdraw.ellipse(
        [pad - border_px, pad - border_px,
         pad + size_px + border_px, pad + size_px + border_px],
        fill=border_color
    )
    result = Image.alpha_composite(result, ring_img)

    # Load and resize logo
    try:
        logo = Image.open(img_path).convert("RGBA")
        logo = logo.resize((size_px, size_px), Image.LANCZOS)
    except Exception:
        logo = Image.new("RGBA", (size_px, size_px), (200, 200, 200, 255))

    # Create circular mask
    mask = Image.new("L", (size_px, size_px), 0)
    mdraw = ImageDraw.Draw(mask)
    mdraw.ellipse([0, 0, size_px - 1, size_px - 1], fill=255)

    logo_circ = Image.new("RGBA", (size_px, size_px), (0, 0, 0, 0))
    logo_circ.paste(logo, (0, 0), mask)

    result.paste(logo_circ, (pad, pad), mask)
    return result

def make_fallback_badge(abbr, bg_hex, fg_hex, size_px=120, border_px=6):
    """Create a colored circle fallback badge (like old script)."""
    pad = border_px + 4
    total = size_px + 2 * pad

    def hex_to_rgb(h):
        h = h.lstrip('#')
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4)) + (255,)

    bg_rgb = hex_to_rgb(bg_hex)
    fg_rgb = hex_to_rgb(fg_hex)

    result = Image.new("RGBA", (total, total), (0, 0, 0, 0))

    # Shadow
    sdraw_img = Image.new("RGBA", (total, total), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(sdraw_img)
    sdraw.ellipse([pad+3, pad+3, pad+size_px+3, pad+size_px+3], fill=(0,0,0,60))
    result = Image.alpha_composite(result, sdraw_img)

    # White ring
    ring_img = Image.new("RGBA", (total, total), (0, 0, 0, 0))
    rdraw = ImageDraw.Draw(ring_img)
    rdraw.ellipse([pad-border_px, pad-border_px, pad+size_px+border_px, pad+size_px+border_px],
                  fill=(255,255,255,255))
    result = Image.alpha_composite(result, ring_img)

    # Colored circle
    circ_img = Image.new("RGBA", (total, total), (0, 0, 0, 0))
    cdraw = ImageDraw.Draw(circ_img)
    cdraw.ellipse([pad, pad, pad+size_px, pad+size_px], fill=bg_rgb)
    result = Image.alpha_composite(result, circ_img)

    # Text
    from PIL import ImageFont
    try:
        font = ImageFont.truetype(_cjk_path, size=max(16, size_px // 5))
    except Exception:
        font = ImageFont.load_default()

    text_img = Image.new("RGBA", (total, total), (0, 0, 0, 0))
    tdraw = ImageDraw.Draw(text_img)
    cx, cy = pad + size_px // 2, pad + size_px // 2
    bbox = tdraw.textbbox((0, 0), abbr, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tdraw.text((cx - tw//2, cy - th//2), abbr, fill=fg_rgb, font=font)
    result = Image.alpha_composite(result, text_img)

    return result

# ─── Preprocess logos ─────────────────────────────────────────────────────────
print("\n=== Processing logos ===")
LOGO_SIZE_PX = 100    # regular clubs
STVV_SIZE_PX = 180    # STVV larger

club_images = {}
for (abbr, full_name, city, lat, lon, wiki_page, bg, fg) in CLUBS:
    is_stvv = (abbr == "STVV")
    sz = STVV_SIZE_PX if is_stvv else LOGO_SIZE_PX

    if abbr in logo_paths:
        img = make_circular_logo(logo_paths[abbr], size_px=sz, border_px=8 if is_stvv else 6)
    else:
        img = make_fallback_badge(abbr, bg, fg, size_px=sz, border_px=8 if is_stvv else 6)
    club_images[abbr] = img
    print(f"  Processed {abbr}")

# ─── Figure & map ────────────────────────────────────────────────────────────
print("\n=== Rendering map ===")
fig = plt.figure(figsize=(FIG_W_IN, FIG_H_IN), dpi=DPI)
ax = fig.add_axes([0, 0, 1, 1])

FW = FIG_W_IN
FH = FIG_H_IN

# ─── Sea background ───────────────────────────────────────────────────────────
ax.set_facecolor('#B8D4E8')
fig.patch.set_facecolor('#B8D4E8')
gradient = np.linspace(0, 1, 500).reshape(1, -1)
ax.imshow(
    np.tile(gradient, (300, 1)),
    extent=[0, FW, 0, FH],
    aspect='auto',
    cmap=plt.cm.Blues,
    vmin=-0.5, vmax=1.0,
    alpha=0.5,
    zorder=0,
)

# ─── Land polygons ────────────────────────────────────────────────────────────
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
    xs = [(lon - LON_MIN) / (LON_MAX - LON_MIN) * FW for lon, lat in pts]
    ys = [(lat - LAT_MIN) / (LAT_MAX - LAT_MIN) * FH for lon, lat in pts]
    return list(zip(xs, ys))

def draw_land(pts, color='#E4EDD0', edge='#94B06A', zorder=1):
    poly = MplPolygon(
        outline_to_xy(pts),
        closed=True,
        facecolor=color,
        edgecolor=edge,
        linewidth=0.8,
        zorder=zorder,
    )
    ax.add_patch(poly)

draw_land(EUROPE_OUTLINE, color='#E4EDD0', edge='#94B06A', zorder=1)
draw_land(BRITAIN,        color='#E4EDD0', edge='#94B06A', zorder=1)
draw_land(IRELAND,        color='#E4EDD0', edge='#94B06A', zorder=1)

# Subtle graticule
for lat in range(37, 59, 3):
    y = (lat - LAT_MIN) / (LAT_MAX - LAT_MIN) * FH
    ax.axhline(y, color='white', lw=0.3, alpha=0.35, zorder=2)
for lon in range(-9, 26, 3):
    x = (lon - LON_MIN) / (LON_MAX - LON_MIN) * FW
    ax.axvline(x, color='white', lw=0.3, alpha=0.35, zorder=2)

# ─── Badge sizing in figure-inch units (for overlap detection) ───────────────
# Logo images are sized in pixels; at DPI we convert to figure inches for overlap
# LOGO_SIZE_PX total = LOGO_SIZE_PX + 2*(border+shadow) ≈ size + 20px
LOGO_R_IN  = (LOGO_SIZE_PX  + 20) / (2 * DPI)   # radius in figure inches
STVV_R_IN  = (STVV_SIZE_PX  + 24) / (2 * DPI)

# ─── Non-overlapping placement (golden-angle spiral) ─────────────────────────
placed = []  # (cx, cy, r)

def overlap_check(cx, cy, r, placed, min_gap=0.07):
    for px, py, pr in placed:
        dist = math.sqrt((cx - px)**2 + (cy - py)**2)
        if dist < (r + pr + min_gap):
            return True
    return False

def try_place(lat, lon, r, attempts=80, spread=0.45):
    base_x, base_y = to_xy(lat, lon)
    golden = 137.508
    for i in range(attempts):
        if i == 0:
            cx, cy = base_x, base_y
        else:
            angle = (i * golden) % 360
            dist = spread * (0.25 + (i // 10) * 0.28)
            cx = base_x + dist * math.cos(math.radians(angle))
            cy = base_y + dist * math.sin(math.radians(angle))
        cx = max(r + 0.05, min(FW - r - 0.05, cx))
        cy = max(r + 0.05, min(FH - r - 0.05, cy))
        if not overlap_check(cx, cy, r, placed):
            return cx, cy, base_x, base_y
    return base_x, base_y, base_x, base_y

# Sort: STVV first, then others
clubs_sorted = sorted(CLUBS, key=lambda c: 0 if c[0] == "STVV" else 1)

badge_data = []
for (abbr, full_name, city, lat, lon, wiki_page, bg, fg) in clubs_sorted:
    is_stvv = (abbr == "STVV")
    r = STVV_R_IN if is_stvv else LOGO_R_IN
    cx, cy, orig_x, orig_y = try_place(lat, lon, r)
    placed.append((cx, cy, r))
    badge_data.append((abbr, cx, cy, orig_x, orig_y, r, bg, fg, is_stvv))

# ─── STVV pulse rings ─────────────────────────────────────────────────────────
stvv_cx, stvv_cy = next(
    (cx, cy) for (abbr, cx, cy, *_) in badge_data if abbr == "STVV"
)
for ring_r, alpha in [(STVV_R_IN * 1.35, 0.30), (STVV_R_IN * 1.80, 0.18), (STVV_R_IN * 2.4, 0.09)]:
    ring = Circle((stvv_cx, stvv_cy), ring_r,
                  fill=False, edgecolor='#FFDD00',
                  linewidth=1.8, alpha=alpha, zorder=3)
    ax.add_patch(ring)

# ─── Draw leader lines (behind logos) ────────────────────────────────────────
for (abbr, cx, cy, orig_x, orig_y, r, bg, fg, is_stvv) in badge_data:
    dist = math.sqrt((cx - orig_x)**2 + (cy - orig_y)**2)
    if dist > 0.06:
        ax.plot(
            [cx, orig_x], [cy, orig_y],
            color='#3A3A3A', lw=0.65, alpha=0.55,
            zorder=3, solid_capstyle='round',
        )
        ax.plot(orig_x, orig_y, 'o', ms=2.5, color='#222222', alpha=0.75, zorder=3)

# ─── Draw logos ───────────────────────────────────────────────────────────────
for (abbr, cx, cy, orig_x, orig_y, r, bg, fg, is_stvv) in badge_data:
    pil_img = club_images[abbr]
    # Convert PIL to numpy
    np_img = np.array(pil_img)
    zoom = 1.0 / DPI  # OffsetImage zoom: 1px = 1/DPI inches
    oi = OffsetImage(np_img, zoom=zoom, zorder=6)
    oi.image.axes = ax
    ab = AnnotationBbox(
        oi, (cx, cy),
        xycoords='data',
        frameon=False,
        zorder=6 if not is_stvv else 8,
        pad=0,
    )
    ax.add_artist(ab)

# ─── Title ────────────────────────────────────────────────────────────────────
title_y = FH - 0.40
ax.text(
    FW / 2, title_y,
    "2025−2026シーズンにスカウトに来たクラブ",
    ha='center', va='top',
    fontsize=26,
    fontweight='bold',
    color='#1A2A4A',
    transform=ax.transData,
    zorder=15,
    path_effects=[pe.withStroke(linewidth=5, foreground='white')],
)

# Sub-info bar
bar_h = 0.28
bar_rect = FancyBboxPatch(
    (0.15, title_y - bar_h - 0.42), FW - 0.30, bar_h,
    boxstyle="round,pad=0.06",
    facecolor='#1A2A4A', edgecolor='none',
    alpha=0.78, zorder=14,
)
ax.add_patch(bar_rect)
ax.text(
    FW / 2, title_y - bar_h - 0.28,
    f"Sint-Truidense VV  ●  {len(CLUBS) - 1} clubs scouted",
    ha='center', va='center',
    fontsize=10, color='white', fontweight='semibold',
    transform=ax.transData, zorder=15,
)

# ─── North arrow ─────────────────────────────────────────────────────────────
na_x, na_y = 0.45, 0.55
ax.annotate("N", xy=(na_x, na_y + 0.25), xytext=(na_x, na_y),
            ha='center', fontsize=9, fontweight='bold', color='#1A2A4A',
            arrowprops=dict(arrowstyle='->', color='#1A2A4A', lw=1.5),
            zorder=15)

# ─── Scale bar ────────────────────────────────────────────────────────────────
km500_deg = 500 / (111.32 * math.cos(math.radians(48)))
km500_fig = km500_deg / (LON_MAX - LON_MIN) * FW
sb_x, sb_y = 0.3, 0.22
ax.plot([sb_x, sb_x + km500_fig], [sb_y, sb_y],
        color='#1A2A4A', lw=3, zorder=15)
ax.plot([sb_x, sb_x], [sb_y - 0.04, sb_y + 0.04], color='#1A2A4A', lw=2, zorder=15)
ax.plot([sb_x + km500_fig, sb_x + km500_fig],
        [sb_y - 0.04, sb_y + 0.04], color='#1A2A4A', lw=2, zorder=15)
ax.text(sb_x + km500_fig / 2, sb_y + 0.10, "500 km",
        ha='center', va='bottom', fontsize=7, color='#1A2A4A', zorder=15)

# ─── Final axis setup ────────────────────────────────────────────────────────
ax.set_xlim(0, FW)
ax.set_ylim(0, FH)
ax.set_aspect('equal')
ax.axis('off')

# ─── Save ─────────────────────────────────────────────────────────────────────
OUT = "/home/user/my-project/scout_map_logos.png"
plt.savefig(OUT, dpi=DPI, bbox_inches='tight', pad_inches=0,
            facecolor=fig.get_facecolor())
plt.close()
print(f"\nSaved → {OUT}")

# ─── Final report ─────────────────────────────────────────────────────────────
print(f"\n=== Summary ===")
print(f"Total clubs: {len(CLUBS)}")
print(f"Logos downloaded: {len(logo_paths)}")
print(f"Fallback badges: {len(failed_logos)}")
if failed_logos:
    print(f"Clubs using fallback: {', '.join(failed_logos)}")
