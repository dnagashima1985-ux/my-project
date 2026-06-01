#!/usr/bin/env python3
"""
STVV Scout Map 2025-2026 - Final version matching reference design
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.font_manager as _fm
_fm.fontManager.addfont("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Polygon as MplPolygon, Circle, FancyArrowPatch
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
import matplotlib.patheffects as pe
import numpy as np
from PIL import Image
import io, os

# ── Constants ────────────────────────────────────────────────────────────────
LOGOS_DIR = "/home/user/my-project/logos"
OUT_FILE  = "/home/user/my-project/scout_map_final.png"
FIG_W, FIG_H = 22.0, 12.375   # inches 16:9
DPI = 160
LON_MIN, LON_MAX = -10.5, 26.0
LAT_MIN, LAT_MAX = 35.5, 59.5

STVV_LAT, STVV_LON = 50.82, 5.17

# ── Club data ─────────────────────────────────────────────────────────────────
# (abbr, lat, lon, fallback_color)
CLUBS = [
    ("STVV",  50.82,  5.17, "#FFDD00"),   # center - special treatment
    ("HSV",   53.55, 10.00, "#009EE0"),
    ("FCSP",  53.58, 10.04, "#824F20"),
    ("D98",   49.87,  8.65, "#3D52B2"),
    ("B04",   51.03,  7.00, "#E32221"),
    ("KOL",   50.94,  6.96, "#FF2000"),
    ("F95",   51.22,  6.78, "#D2000B"),
    ("BMG",   51.19,  6.44, "#000000"),
    ("S04",   51.57,  7.07, "#004E9E"),
    ("BVB",   51.51,  7.47, "#FDE100"),
    ("WOB",   52.42, 10.79, "#65B32E"),
    ("SVW",   53.08,  8.81, "#1D9053"),
    ("KSC",   49.00,  8.40, "#009EE0"),
    ("FCK",   49.44,  7.77, "#E2001A"),
    ("FCN",   49.45, 11.08, "#A0071B"),
    ("RBL",   51.34, 13.38, "#DD0741"),
    ("SGE",   50.11,  8.68, "#E1000F"),
    ("SCF",   47.99,  7.85, "#E50019"),
    ("TSG",   49.24,  8.89, "#1865A4"),
    ("FCA",   48.37, 10.90, "#BA3733"),
    ("FCU",   52.47, 13.33, "#EB1923"),
    ("BSC",   52.57, 13.46, "#005CA9"),
    ("VFB",   48.78,  9.18, "#E32219"),
    ("AJX",   52.31,  4.94, "#E2001A"),
    ("FCU2",  52.09,  5.12, "#CC0000"),
    ("AZ",    52.63,  4.75, "#FF0000"),
    ("FEY",   51.89,  4.52, "#CC0000"),
    ("PSV",   51.44,  5.48, "#E40613"),
    ("FCT",   52.22,  6.90, "#E2001A"),
    ("SFC",   50.91, -1.40, "#D71920"),
    ("COV",   52.41, -1.51, "#75AADB"),
    ("OXF",   51.75, -1.25, "#FFD700"),
    ("QPR",   51.44, -0.23, "#1D5BA4"),
    ("MIL",   51.49, -0.05, "#001D5E"),
    ("NUFC",  54.98, -1.62, "#000000"),
    ("MUFC",  53.46, -2.29, "#DA020E"),
    ("WHU",   51.54,  0.02, "#7A263A"),
    ("THFC",  51.62, -0.07, "#132257"),
    ("WWFC",  52.59, -2.13, "#FDB913"),
    ("LCFC",  52.64, -1.13, "#003090"),
    ("LUFC",  53.80, -1.55, "#1D428A"),
    ("BFC",   53.79, -2.24, "#6C1D45"),
    ("WAT",   51.66, -0.40, "#FBEE23"),
    ("PNE",   53.76, -2.70, "#FFFFFF"),
    ("RFC",   55.86, -4.26, "#0000FF"),
    ("AJA",   47.80,  3.57, "#FFFFFF"),
    ("LOSC",  50.63,  3.06, "#E31E25"),
    ("PSG",   48.87,  2.33, "#004170"),
    ("PFC",   48.83,  2.38, "#002D5E"),
    ("SRFC",  48.11, -1.68, "#000000"),
    ("FCL",   47.75, -3.37, "#F47920"),
    ("OL",    45.75,  4.83, "#002855"),
    ("CF63",  45.78,  3.08, "#AB192B"),
    ("SDR",   49.26,  4.03, "#E30613"),
    ("TFC",   43.60,  1.44, "#7B2D8B"),
    ("COM",   45.81,  9.09, "#0033A0"),
    ("TOR",   45.07,  7.69, "#8B1A1A"),
    ("SASU",  44.54, 10.79, "#2D6741"),
    ("BOL",   44.50, 11.34, "#003591"),
    ("HVR",   45.44, 10.99, "#FFD700"),
    ("FIOR",  43.78, 11.25, "#4C247D"),
    ("ATA",   45.70,  9.67, "#1E3E85"),
    ("INTER", 45.46,  9.17, "#0068A8"),
    ("ACM",   45.50,  9.22, "#FB090B"),
    ("CREM",  45.13, 10.02, "#9B1730"),
    ("PAR",   44.80, 10.33, "#0058A0"),
    ("GEN",   44.41,  8.93, "#CC0000"),
    ("MON",   45.58,  9.27, "#CC0000"),
    ("CAG",   39.22,  9.12, "#003595"),
    ("LEV",   39.47, -0.38, "#0047AB"),
    ("BETIS", 37.36, -5.99, "#00833F"),
    ("RSO",   43.32, -1.98, "#0067B1"),
    ("OSA",   42.82, -1.65, "#CC0000"),
    ("RSPG",  43.55, -5.66, "#CC0000"),
    ("RAPID", 48.21, 16.37, "#007A3D"),
    ("SLA",   50.08, 14.44, "#CC0000"),
    ("FKP",   49.74, 13.37, "#002D62"),
    ("CZV",   44.80, 20.46, "#CC0000"),
    ("FCK2",  55.68, 12.57, "#0B479D"),
]

# ── Helper: coordinate → figure units ────────────────────────────────────────
def ll2fig(lat, lon):
    x = (lon - LON_MIN) / (LON_MAX - LON_MIN) * FIG_W
    y = (lat - LAT_MIN) / (LAT_MAX - LAT_MIN) * FIG_H
    return x, y

stvv_fx, stvv_fy = ll2fig(STVV_LAT, STVV_LON)

# ── Load logo ─────────────────────────────────────────────────────────────────
LOGO_CACHE = {}
def load_logo(abbr, size_px):
    path = os.path.join(LOGOS_DIR, f"{abbr}.png")
    if not os.path.exists(path) or os.path.getsize(path) < 500:
        return None
    try:
        img = Image.open(path).convert("RGBA")
        w, h = img.size
        # Filter out panoramic stadium photos (aspect ratio > 2.5:1)
        if w / h > 2.5 or h / w > 2.5:
            return None
        scale = size_px / max(w, h)
        nw, nh = max(1, int(w * scale)), max(1, int(h * scale))
        img = img.resize((nw, nh), Image.LANCZOS)
        return np.array(img)
    except Exception:
        return None

# ── Europe land polygons ──────────────────────────────────────────────────────
EUROPE = [
    (-9.5, 38.7), (-9.2, 39.5), (-8.6, 41.1), (-8.0, 42.0),
    (-7.0, 43.7), (-5.7, 43.6), (-4.0, 43.5), (-3.8, 43.5),
    (-1.8, 43.4), (-1.7, 43.3), (-1.5, 46.8), (-2.5, 47.7),
    (-4.5, 47.8), (-4.8, 48.4), (-4.0, 48.5), (-2.0, 48.7),
    (-1.5, 49.2), (-1.0, 49.6), (0.0, 49.4), (1.3, 50.8),
    (1.8, 50.9), (2.5, 51.0), (3.0, 51.4), (3.4, 51.4),
    (3.8, 51.6), (4.3, 51.9), (4.0, 52.4), (3.7, 53.0),
    (4.7, 53.0), (5.4, 53.4), (7.0, 53.7), (8.0, 55.0),
    (8.5, 55.2), (9.4, 54.8), (10.0, 55.0), (10.5, 57.7),
    (11.0, 57.6), (11.2, 56.0), (12.5, 56.1), (12.7, 55.5),
    (12.6, 55.0), (14.0, 54.0), (14.5, 54.0), (16.0, 54.5),
    (18.0, 54.8), (19.5, 54.4), (22.5, 54.4), (24.0, 55.0),
    (24.0, 58.5), (22.0, 58.5), (21.0, 57.5), (20.5, 56.5),
    (19.0, 54.5), (17.0, 51.0), (15.0, 50.5), (14.8, 50.2),
    (17.2, 48.0), (18.8, 47.8), (22.0, 48.4), (22.5, 49.0),
    (22.0, 46.0), (23.0, 45.5), (22.5, 44.5), (21.5, 44.0),
    (19.0, 43.5), (17.5, 43.0), (16.5, 43.5), (15.5, 44.0),
    (14.0, 45.1), (13.7, 45.8), (13.5, 45.6), (12.5, 45.5),
    (13.0, 45.6), (13.4, 45.8), (13.8, 44.4), (15.0, 41.0),
    (16.0, 40.0), (15.6, 38.2), (15.0, 37.0), (15.5, 36.6),
    (16.5, 37.8), (16.2, 39.0), (16.8, 41.2), (16.0, 41.5),
    (15.5, 42.0), (14.5, 43.0), (13.5, 44.5), (13.0, 45.0),
    (8.0, 44.0), (7.5, 43.8), (7.0, 43.7), (5.5, 43.3),
    (4.5, 43.4), (3.2, 43.5), (2.0, 42.5), (0.5, 42.7),
    (-0.5, 43.4), (-1.7, 43.3), (-1.8, 43.4), (-4.0, 43.5),
    (-8.0, 42.0), (-8.9, 38.5), (-9.0, 37.0), (-6.0, 36.0),
    (-5.3, 36.1), (-5.0, 36.0), (-4.0, 36.5), (-2.0, 36.5),
    (0.0, 37.5), (1.0, 38.0), (0.5, 39.5), (0.0, 40.5),
    (0.8, 41.0), (3.2, 41.9), (3.3, 42.3), (1.0, 42.5),
    (-0.5, 43.4),
]

BRITAIN = [
    (-5.7, 50.0), (-5.0, 49.9), (-3.0, 50.2), (-1.0, 50.7),
    (0.5, 51.1), (0.7, 51.4), (1.0, 52.0), (0.5, 52.9),
    (0.2, 53.6), (-0.1, 53.8), (-1.0, 54.3), (-1.7, 55.1),
    (-2.0, 55.6), (-2.5, 56.0), (-3.0, 56.5), (-3.5, 57.3),
    (-4.5, 57.9), (-5.3, 58.3), (-5.0, 57.5), (-5.5, 56.8),
    (-5.5, 56.0), (-5.0, 55.5), (-4.0, 55.0), (-4.7, 54.2),
    (-3.5, 54.0), (-3.0, 53.4), (-3.0, 53.0), (-3.1, 51.5),
    (-4.0, 51.2), (-5.1, 51.6), (-5.7, 50.8), (-5.7, 50.0),
]

IRELAND = [
    (-6.0, 52.0), (-7.0, 52.2), (-8.5, 52.0), (-9.5, 51.5),
    (-10.0, 52.0), (-9.0, 53.5), (-8.0, 54.5), (-7.0, 55.0),
    (-6.0, 54.5), (-6.0, 54.0), (-5.8, 53.2), (-6.5, 52.5),
    (-6.0, 52.0),
]

SARDINIA = [(9.2, 38.9), (9.7, 38.5), (9.8, 39.5), (9.4, 41.2),
            (8.5, 41.2), (8.2, 40.5), (8.4, 39.2), (9.2, 38.9)]
SICILY   = [(13.0, 37.5), (15.5, 37.0), (15.6, 37.5), (15.0, 38.2),
            (16.5, 38.0), (16.0, 39.0), (15.6, 38.2), (13.0, 37.5)]
CORSICA  = [(8.6, 41.4), (9.4, 41.1), (9.5, 42.0), (9.0, 43.0),
            (8.7, 42.5), (8.6, 41.4)]

def poly_xy(pts_lonlat):
    xs = [(lon - LON_MIN) / (LON_MAX - LON_MIN) * FIG_W for lon, lat in pts_lonlat]
    ys = [(lat - LAT_MIN) / (LAT_MAX - LAT_MIN) * FIG_H for lon, lat in pts_lonlat]
    return list(zip(xs, ys))

# ── Overlap resolution ────────────────────────────────────────────────────────
def resolve_overlaps(entries, logo_w, min_gap=0.03, max_drift=0.90):
    """entries: list of [fx, fy, lat, lon, abbr, color]. Mutates fx/fy."""
    origins = [(e[0], e[1]) for e in entries]
    for _ in range(600):
        moved = False
        for i in range(len(entries)):
            for j in range(i + 1, len(entries)):
                dx = entries[i][0] - entries[j][0]
                dy = entries[i][1] - entries[j][1]
                dist = (dx**2 + dy**2)**0.5
                needed = logo_w + min_gap
                if dist < needed and dist > 1e-6:
                    push = (needed - dist) / 2
                    nx, ny = dx / dist, dy / dist
                    entries[i][0] += nx * push
                    entries[i][1] += ny * push
                    entries[j][0] -= nx * push
                    entries[j][1] -= ny * push
                    moved = True
        # Clamp drift from original position
        for i, e in enumerate(entries):
            ox, oy = origins[i]
            ddx, ddy = e[0] - ox, e[1] - oy
            drift = (ddx**2 + ddy**2)**0.5
            if drift > max_drift:
                scale = max_drift / drift
                e[0] = ox + ddx * scale
                e[1] = oy + ddy * scale
        # Clamp to figure bounds
        for e in entries:
            e[0] = np.clip(e[0], 0.3, FIG_W - 0.3)
            e[1] = np.clip(e[1], 0.3, FIG_H - 0.3)
        if not moved:
            break
    return entries

# ── Figure ────────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(FIG_W, FIG_H), dpi=DPI)
ax  = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, FIG_W); ax.set_ylim(0, FIG_H)
ax.axis('off')
fig.patch.set_facecolor('#5BA3CC')
ax.set_facecolor('#5BA3CC')

# ── Ocean gradient ────────────────────────────────────────────────────────────
from matplotlib.colors import LinearSegmentedColormap
ocean_cmap = LinearSegmentedColormap.from_list("ocean",
    ["#3A8AB5", "#5BAED0", "#7EC8E3", "#A8DCF0"], N=256)
grad = np.linspace(0, 1, 400).reshape(1, -1)
ax.imshow(np.tile(grad.T, (1, 800)), extent=[0, FIG_W, 0, FIG_H],
          aspect='auto', cmap=ocean_cmap, alpha=0.9, zorder=0)

# ── Land ──────────────────────────────────────────────────────────────────────
land_color = "#C8D98A"
land_edge  = "#8FAA50"
for pts in [EUROPE, BRITAIN, IRELAND, SARDINIA, SICILY, CORSICA]:
    poly = MplPolygon(poly_xy(pts), closed=True,
                      facecolor=land_color, edgecolor=land_edge,
                      linewidth=0.9, zorder=1)
    ax.add_patch(poly)

# ── Starburst / radial light from STVV ───────────────────────────────────────
n_beams = 32
for i in range(n_beams):
    angle = i * 360 / n_beams
    rad   = np.radians(angle)
    length = max(FIG_W, FIG_H) * 1.5
    ex = stvv_fx + length * np.cos(rad)
    ey = stvv_fy + length * np.sin(rad)
    lw   = 6 if i % 2 == 0 else 3
    alph = 0.18 if i % 2 == 0 else 0.10
    ax.plot([stvv_fx, ex], [stvv_fy, ey],
            color='white', lw=lw, alpha=alph, zorder=2, solid_capstyle='round')

# soft glow at STVV
for r, a in [(2.5, 0.06), (1.8, 0.10), (1.2, 0.14), (0.7, 0.20)]:
    glow = Circle((stvv_fx, stvv_fy), r, color='white', alpha=a, zorder=3)
    ax.add_patch(glow)

# ── Pre-compute logo sizes ────────────────────────────────────────────────────
LOGO_PX_NORMAL = 62    # pixels for most clubs
LOGO_PX_STVV   = 140   # pixels for STVV

# ── Build placement list ──────────────────────────────────────────────────────
# inches per logo on figure
LOGO_IN = LOGO_PX_NORMAL / DPI   # ~0.50 in
STVV_IN = LOGO_PX_STVV   / DPI   # ~1.00 in

entries = []  # [fx, fy, lat, lon, abbr, color]
for abbr, lat, lon, color in CLUBS:
    fx, fy = ll2fig(lat, lon)
    entries.append([fx, fy, lat, lon, abbr, color])

# Separate STVV from the rest for overlap resolution
stvv_entry = next(e for e in entries if e[4] == "STVV")
others = [e for e in entries if e[4] != "STVV"]

others = resolve_overlaps(others, LOGO_IN, min_gap=0.03, max_drift=0.80)

# ── Draw thin lines from STVV to each club city ───────────────────────────────
for e in others:
    city_x, city_y = ll2fig(e[2], e[3])
    ax.plot([stvv_fx, city_x], [stvv_fy, city_y],
            color='white', lw=0.6, alpha=0.45, zorder=4,
            solid_capstyle='round')

# ── Draw glowing city dots ────────────────────────────────────────────────────
for e in others:
    city_x, city_y = ll2fig(e[2], e[3])
    color = e[5]
    # outer glow
    for gr, ga in [(0.14, 0.25), (0.09, 0.40), (0.055, 0.70)]:
        gc = Circle((city_x, city_y), gr, color=color, alpha=ga, zorder=5)
        ax.add_patch(gc)
    # white center
    dot = Circle((city_x, city_y), 0.030, color='white', zorder=6)
    ax.add_patch(dot)

# ── Draw club logos ───────────────────────────────────────────────────────────
for e in others:
    fx, fy = e[0], e[1]
    abbr   = e[4]
    color  = e[5]

    arr = load_logo(abbr, LOGO_PX_NORMAL)
    if arr is not None:
        # Add drop shadow by placing a dark image slightly offset
        shadow_arr = arr.copy()
        shadow_arr[..., :3] = 0
        shadow_arr[..., 3] = (shadow_arr[..., 3] * 0.35).astype(np.uint8)
        sh_img = OffsetImage(shadow_arr, zoom=1.0, interpolation='lanczos')
        sh_box = AnnotationBbox(sh_img, (fx + 0.025, fy - 0.025),
                                frameon=False, zorder=7,
                                xycoords='data', box_alignment=(0.5, 0.5))
        ax.add_artist(sh_box)
        # Main logo
        im_obj = OffsetImage(arr, zoom=1.0, interpolation='lanczos')
        ab = AnnotationBbox(im_obj, (fx, fy),
                            frameon=False, zorder=8,
                            xycoords='data', box_alignment=(0.5, 0.5))
        ax.add_artist(ab)
    else:
        # Fallback: colored shield badge
        r = LOGO_IN * 0.38
        outer = Circle((fx, fy), r + 0.04, color='white', zorder=7)
        ax.add_patch(outer)
        main  = Circle((fx, fy), r, color=color, zorder=8)
        ax.add_patch(main)
        ax.text(fx, fy, abbr[:4], ha='center', va='center',
                fontsize=5.5, fontweight='bold', color='white',
                zorder=9,
                path_effects=[pe.withStroke(linewidth=1, foreground='black')])

# ── STVV center (drawn last / on top) ─────────────────────────────────────────
# Gold location pin
pin_x, pin_y = stvv_fx, stvv_fy + STVV_IN * 0.55
pin_r = 0.22
# Pin circle
for pr, pc, pa in [(pin_r+0.06, '#B8860B', 1.0),
                   (pin_r+0.02, '#FFD700', 1.0),
                   (pin_r,      '#FDB913', 1.0)]:
    ax.add_patch(Circle((pin_x, pin_y), pr, color=pc, zorder=12))
# Inner white dot
ax.add_patch(Circle((pin_x, pin_y), pin_r * 0.32, color='white', zorder=13))
# Pin tail (triangle pointing down)
tail_pts = [(pin_x, stvv_fy + STVV_IN * 0.06),
            (pin_x - pin_r * 0.55, pin_y - pin_r * 0.4),
            (pin_x + pin_r * 0.55, pin_y - pin_r * 0.4)]
tail_poly = MplPolygon(tail_pts, closed=True, facecolor='#FDB913',
                       edgecolor='#B8860B', linewidth=1, zorder=11)
ax.add_patch(tail_poly)

# STVV logo
arr_stvv = load_logo("STVV", LOGO_PX_STVV)
if arr_stvv is not None:
    # Shadow
    shadow = arr_stvv.copy()
    shadow[..., :3] = 0
    shadow[..., 3] = (shadow[..., 3] * 0.4).astype(np.uint8)
    sh_img = OffsetImage(shadow, zoom=1.0, interpolation='lanczos')
    ax.add_artist(AnnotationBbox(sh_img, (stvv_fx + 0.04, stvv_fy - 0.04),
                                 frameon=False, zorder=9,
                                 xycoords='data', box_alignment=(0.5, 0.5)))
    im_obj = OffsetImage(arr_stvv, zoom=1.0, interpolation='lanczos')
    ax.add_artist(AnnotationBbox(im_obj, (stvv_fx, stvv_fy),
                                 frameon=False, zorder=10,
                                 xycoords='data', box_alignment=(0.5, 0.5)))
else:
    # Fallback big badge
    ax.add_patch(Circle((stvv_fx, stvv_fy), STVV_IN*0.5+0.06, color='white', zorder=9))
    ax.add_patch(Circle((stvv_fx, stvv_fy), STVV_IN*0.5, color='#FFDD00', zorder=10))
    ax.text(stvv_fx, stvv_fy, "STVV", ha='center', va='center',
            fontsize=14, fontweight='bold', color='black', zorder=11)

# "STVV" label below
ax.text(stvv_fx, stvv_fy - STVV_IN * 0.65, "STVV",
        ha='center', va='top', fontsize=11, fontweight='bold', color='white',
        zorder=11, path_effects=[pe.withStroke(linewidth=2.5, foreground='#333333')])

# ── Title (top-left, two lines) ───────────────────────────────────────────────
title_box_x = 0.18
title_box_y = FIG_H - 0.15
box_w, box_h = 4.0, 1.45
title_bg = mpatches.FancyBboxPatch(
    (title_box_x - 0.12, title_box_y - box_h - 0.05), box_w, box_h + 0.15,
    boxstyle="round,pad=0.08",
    facecolor='white', edgecolor='none', alpha=0.88, zorder=20)
ax.add_patch(title_bg)
ax.text(title_box_x, title_box_y - 0.10,
        "2025−2026シーズンに",
        ha='left', va='top', fontsize=20, fontweight='bold',
        color='#1A2A4A', fontfamily='Noto Sans CJK JP',
        transform=ax.transData, zorder=21)
ax.text(title_box_x, title_box_y - 0.80,
        "スカウトに来たクラブ",
        ha='left', va='top', fontsize=20, fontweight='bold',
        color='#1A2A4A', fontfamily='Noto Sans CJK JP',
        transform=ax.transData, zorder=21)

# ── Save ──────────────────────────────────────────────────────────────────────
plt.savefig(OUT_FILE, dpi=DPI, bbox_inches='tight', pad_inches=0,
            facecolor='#5BA3CC')
plt.close()
print(f"Saved → {OUT_FILE}")
