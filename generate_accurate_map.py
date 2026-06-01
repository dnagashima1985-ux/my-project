#!/usr/bin/env python3
"""
STVV Scout Map 2025-2026
Accurate geographic positions using Cartopy + Natural Earth data
Logos placed in Mercator data coordinates for correctness
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.font_manager as _fm
_fm.fontManager.addfont("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc")

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
from matplotlib.patches import Circle as MplCircle, Polygon as MplPoly, FancyBboxPatch
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
from PIL import Image
import os

LOGOS_DIR = "/home/user/my-project/logos"
OUT_FILE  = "/home/user/my-project/scout_map_accurate.png"
DPI  = 160
FW   = 22.0    # figure width  (inches)
FH   = 12.375  # figure height (inches)

EXTENT    = [-11.5, 27.5, 34.5, 60.5]
PROJ      = ccrs.Mercator()
DATA_CRS  = ccrs.PlateCarree()

STVV_LAT, STVV_LON = 50.815, 5.168

# ── Club data ─────────────────────────────────────────────────────────────────
CLUBS = [
    # STVV center
    ("STVV",  50.815,  5.168),
    # Germany
    ("HSV",   53.587,  9.900),
    ("FCSP",  53.554, 10.023),
    ("D98",   49.864,  8.648),
    ("B04",   51.038,  7.002),
    ("KOL",   50.934,  6.875),
    ("F95",   51.257,  6.734),
    ("BMG",   51.175,  6.385),
    ("S04",   51.554,  7.068),
    ("BVB",   51.493,  7.452),
    ("WOB",   52.432, 10.804),
    ("SVW",   53.066,  8.838),
    ("KSC",   49.023,  8.413),
    ("FCK",   49.434,  7.776),
    ("FCN",   49.424, 11.123),
    ("RBL",   51.346, 12.348),
    ("SGE",   50.069,  8.645),
    ("SCF",   47.987,  7.889),
    ("TSG",   49.238,  8.889),
    ("FCA",   48.323, 10.886),
    ("FCU",   52.457, 13.567),
    ("BSC",   52.514, 13.402),
    ("VFB",   48.792,  9.232),
    # Netherlands
    ("AJX",   52.314,  4.942),
    ("FCU2",  52.079,  5.116),
    ("AZ",    52.627,  4.749),
    ("FEY",   51.894,  4.523),
    ("PSV",   51.442,  5.467),
    ("FCT",   52.239,  6.803),
    # England
    ("SFC",   50.906, -1.391),
    ("COV",   52.408, -1.504),
    ("OXF",   51.739, -1.247),
    ("QPR",   51.509, -0.232),
    ("MIL",   51.486, -0.050),
    ("NUFC",  54.976, -1.622),
    ("MUFC",  53.463, -2.291),
    ("WHU",   51.538,  0.017),
    ("THFC",  51.604, -0.066),
    ("WWFC",  52.590, -2.130),
    ("LCFC",  52.620, -1.142),
    ("LUFC",  53.778, -1.572),
    ("BFC",   53.789, -2.230),
    ("WAT",   51.650, -0.402),
    ("PNE",   53.771, -2.687),
    ("RFC",   55.851, -4.309),
    # France
    ("AJA",   47.795,  3.564),
    ("LOSC",  50.612,  3.130),
    ("PSG",   48.841,  2.253),
    ("PFC",   48.827,  2.404),
    ("SRFC",  48.107, -1.712),
    ("FCL",   47.750, -3.367),
    ("OL",    45.765,  4.982),
    ("CF63",  45.778,  3.117),
    ("SDR",   49.234,  4.026),
    ("TFC",   43.582,  1.434),
    # Italy
    ("COM",   45.815,  9.085),
    ("TOR",   45.109,  7.641),
    ("SASU",  44.549, 10.791),
    ("BOL",   44.492, 11.313),
    ("HVR",   45.439, 10.992),
    ("FIOR",  43.781, 11.283),
    ("ATA",   45.709,  9.680),
    ("INTER", 45.478,  9.124),
    ("ACM",   45.478,  9.124),
    ("CREM",  45.120, 10.030),
    ("PAR",   44.800, 10.336),
    ("GEN",   44.416,  8.951),
    ("MON",   45.586,  9.274),
    ("CAG",   39.214,  9.137),
    # Spain
    ("LEV",   39.474, -0.358),
    ("BETIS", 37.357, -5.982),
    ("RSO",   43.301, -2.015),
    ("OSA",   42.796, -1.637),
    ("RSPG",  43.540, -5.635),
    # Austria / Czech / Serbia / Denmark
    ("RAPID", 48.196, 16.260),
    ("SLA",   50.068, 14.472),
    ("FKP",   49.744, 13.386),
    ("CZV",   44.786, 20.462),
    ("FCK2",  55.703, 12.576),
]

COLORS = {
    "STVV":"#FFDD00","HSV":"#009EE0","FCSP":"#824F20","D98":"#3D52B2",
    "B04":"#E32221","KOL":"#FF2000","F95":"#D2000B","BMG":"#333333",
    "S04":"#004E9E","BVB":"#FDE100","WOB":"#65B32E","SVW":"#1D9053",
    "KSC":"#009EE0","FCK":"#E2001A","FCN":"#A0071B","RBL":"#DD0741",
    "SGE":"#E1000F","SCF":"#E50019","TSG":"#1865A4","FCA":"#BA3733",
    "FCU":"#EB1923","BSC":"#005CA9","VFB":"#E32219","AJX":"#E2001A",
    "FCU2":"#CC0000","AZ":"#FF0000","FEY":"#CC0000","PSV":"#E40613",
    "FCT":"#E2001A","SFC":"#D71920","COV":"#75AADB","OXF":"#FFD700",
    "QPR":"#1D5BA4","MIL":"#001D5E","NUFC":"#111111","MUFC":"#DA020E",
    "WHU":"#7A263A","THFC":"#132257","WWFC":"#FDB913","LCFC":"#003090",
    "LUFC":"#1D428A","BFC":"#6C1D45","WAT":"#FBEE23","PNE":"#888888",
    "RFC":"#0000CC","AJA":"#999999","LOSC":"#E31E25","PSG":"#004170",
    "PFC":"#002D5E","SRFC":"#111111","FCL":"#F47920","OL":"#002855",
    "CF63":"#AB192B","SDR":"#E30613","TFC":"#7B2D8B","COM":"#0033A0",
    "TOR":"#8B1A1A","SASU":"#2D6741","BOL":"#003591","HVR":"#FFD700",
    "FIOR":"#4C247D","ATA":"#1E3E85","INTER":"#0068A8","ACM":"#FB090B",
    "CREM":"#9B1730","PAR":"#0058A0","GEN":"#CC0000","MON":"#CC0000",
    "CAG":"#003595","LEV":"#0047AB","BETIS":"#00833F","RSO":"#0067B1",
    "OSA":"#CC0000","RSPG":"#CC0000","RAPID":"#007A3D","SLA":"#CC0000",
    "FKP":"#002D62","CZV":"#CC0000","FCK2":"#0B479D",
}

def load_logo(abbr, size_px):
    path = os.path.join(LOGOS_DIR, f"{abbr}.png")
    if not os.path.exists(path) or os.path.getsize(path) < 500:
        return None
    try:
        img = Image.open(path).convert("RGBA")
        w, h = img.size
        if max(w, h) / min(w, h) > 2.5:
            return None
        scale = size_px / max(w, h)
        nw, nh = max(1, int(w * scale)), max(1, int(h * scale))
        return np.array(img.resize((nw, nh), Image.LANCZOS))
    except Exception:
        return None

def ll2merc(lat, lon):
    x, y = PROJ.transform_point(lon, lat, DATA_CRS)
    return x, y

stvv_mx, stvv_my = ll2merc(STVV_LAT, STVV_LON)

# ── Figure ────────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(FW, FH), dpi=DPI)
ax  = fig.add_subplot(1, 1, 1, projection=PROJ)
ax.set_extent(EXTENT, crs=DATA_CRS)

# ── Base map ──────────────────────────────────────────────────────────────────
ax.add_feature(cfeature.OCEAN.with_scale('50m'), facecolor='#4FAAD5', zorder=0)
ax.add_feature(cfeature.LAND.with_scale('50m'),  facecolor='#CEDE8E',
               edgecolor='#7AA045', linewidth=0.5, zorder=1)
ax.add_feature(cfeature.COASTLINE.with_scale('50m'),
               linewidth=0.7, edgecolor='#5A8832', zorder=2)
ax.add_feature(cfeature.BORDERS.with_scale('50m'),
               linewidth=0.4, edgecolor='#7AA045', linestyle='--', zorder=2)
ax.add_feature(cfeature.LAKES.with_scale('50m'),
               facecolor='#4FAAD5', edgecolor='none', zorder=2)

# ── Starburst ─────────────────────────────────────────────────────────────────
MAX_RAY = 1.2e7
for i in range(36):
    rad = np.radians(i * 10)
    ex  = stvv_mx + MAX_RAY * np.cos(rad)
    ey  = stvv_my + MAX_RAY * np.sin(rad)
    lw, alph = (6, 0.22) if i % 2 == 0 else (3, 0.12)
    ax.plot([stvv_mx, ex], [stvv_my, ey],
            color='white', lw=lw, alpha=alph, zorder=3,
            transform=ax.transData, solid_capstyle='round')

for r_m, a in [(400000,0.06),(250000,0.12),(150000,0.20),(80000,0.30)]:
    ax.add_patch(MplCircle((stvv_mx, stvv_my), r_m, color='white',
                            alpha=a, zorder=4, transform=ax.transData))

# ── Pre-draw to fix transforms ────────────────────────────────────────────────
plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
fig.canvas.draw()

inv = ax.transData.inverted()

# Collect Mercator + display-pixel positions
entries = []  # [disp_px, disp_py, merc_x, merc_y, abbr]
for abbr, lat, lon in CLUBS:
    mx, my = ll2merc(lat, lon)
    px, py = ax.transData.transform((mx, my))
    entries.append([px, py, mx, my, abbr])

stvv_e  = next(e for e in entries if e[4] == "STVV")
stvv_px, stvv_py = stvv_e[0], stvv_e[1]
others  = [e for e in entries if e[4] != "STVV"]

LOGO_PX = 52
STVV_PX = 140

# ── Overlap resolution in display pixels ──────────────────────────────────────
origins = [(e[0], e[1]) for e in others]
needed  = LOGO_PX + 5

for _ in range(1500):
    moved = False
    for i in range(len(others)):
        for j in range(i + 1, len(others)):
            dx = others[i][0] - others[j][0]
            dy = others[i][1] - others[j][1]
            d  = (dx*dx + dy*dy) ** 0.5
            if d < needed and d > 0.1:
                push = (needed - d) / 2.2
                nx, ny = dx / d, dy / d
                others[i][0] += nx * push
                others[i][1] += ny * push
                others[j][0] -= nx * push
                others[j][1] -= ny * push
                moved = True
    # Soft spring back toward origin (prevents runaway drift)
    for i, e in enumerate(others):
        ox, oy = origins[i]
        ddx, ddy = e[0] - ox, e[1] - oy
        drift = (ddx*ddx + ddy*ddy) ** 0.5
        if drift > 180:
            s = 180 / drift
            e[0] = ox + ddx * s
            e[1] = oy + ddy * s
    if not moved:
        break

# Convert resolved display-pixel positions back to Mercator data coords
for e in others:
    mx, my = inv.transform((e[0], e[1]))
    e[2], e[3] = mx, my

# ── Lines from STVV to city dots ──────────────────────────────────────────────
for abbr, lat, lon in CLUBS:
    if abbr == "STVV":
        continue
    city_mx, city_my = ll2merc(lat, lon)
    ax.plot([stvv_mx, city_mx], [stvv_my, city_my],
            color='white', lw=0.65, alpha=0.45, zorder=5,
            transform=ax.transData, solid_capstyle='round')

# ── City glowing dots (at actual geography) ───────────────────────────────────
for abbr, lat, lon in CLUBS:
    if abbr == "STVV":
        continue
    city_mx, city_my = ll2merc(lat, lon)
    color = COLORS.get(abbr, "#AAAAAA")
    for r_m, a in [(55000,0.20),(35000,0.40),(18000,0.75)]:
        ax.add_patch(MplCircle((city_mx, city_my), r_m, color=color,
                                alpha=a, zorder=6, transform=ax.transData))
    ax.add_patch(MplCircle((city_mx, city_my), 8000, color='white',
                            zorder=7, transform=ax.transData))

# ── Draw logos at resolved positions ──────────────────────────────────────────
def place_logo(abbr, data_x, data_y, size_px, z=8):
    arr = load_logo(abbr, size_px)
    color = COLORS.get(abbr, "#888888")
    if arr is not None:
        # shadow offset in data units (~15km)
        sh = arr.copy(); sh[..., :3] = 0
        sh[..., 3] = (sh[..., 3] * 0.30).astype(np.uint8)
        ax.add_artist(AnnotationBbox(
            OffsetImage(sh, zoom=1.0, interpolation='lanczos'),
            (data_x + 12000, data_y - 12000),
            frameon=False, zorder=z, xycoords='data',
            box_alignment=(0.5, 0.5)))
        ax.add_artist(AnnotationBbox(
            OffsetImage(arr, zoom=1.0, interpolation='lanczos'),
            (data_x, data_y),
            frameon=False, zorder=z+1, xycoords='data',
            box_alignment=(0.5, 0.5)))
    else:
        # fallback badge
        half = size_px / DPI * 50000   # rough metres
        ax.add_patch(MplCircle((data_x, data_y), half + 8000,
                                color='white', zorder=z, transform=ax.transData))
        ax.add_patch(MplCircle((data_x, data_y), half,
                                color=color, zorder=z+1, transform=ax.transData))
        ax.text(data_x, data_y, abbr[:4], ha='center', va='center',
                fontsize=5, fontweight='bold', color='white', zorder=z+2,
                transform=ax.transData,
                path_effects=[pe.withStroke(linewidth=1, foreground='black')])

for e in others:
    place_logo(e[4], e[2], e[3], LOGO_PX, z=8)

# ── STVV center ───────────────────────────────────────────────────────────────
# Place STVV logo
place_logo("STVV", stvv_mx, stvv_my, STVV_PX, z=12)

# Gold pin above STVV (offset ~70 km north in Mercator metres)
pin_offset_m = 95000
pin_mx, pin_my = stvv_mx, stvv_my + pin_offset_m

pin_r_m = 32000
for pr, pc in [(pin_r_m+10000,'#A07000'),
               (pin_r_m+4000, '#FFD700'),
               (pin_r_m,      '#FDB913')]:
    ax.add_patch(MplCircle((pin_mx, pin_my), pr, color=pc,
                            zorder=13, transform=ax.transData))
ax.add_patch(MplCircle((pin_mx, pin_my), pin_r_m*0.35, color='white',
                        zorder=14, transform=ax.transData))
# Pin tail
tail = [(pin_mx,               stvv_my + 12000),
        (pin_mx - pin_r_m*0.6, pin_my - pin_r_m*0.5),
        (pin_mx + pin_r_m*0.6, pin_my - pin_r_m*0.5)]
ax.add_patch(MplPoly(tail, closed=True, facecolor='#FDB913',
                      edgecolor='#A07000', lw=1.2,
                      zorder=13, transform=ax.transData))

# "STVV" label
ax.annotate("STVV",
            xy=(stvv_mx, stvv_my),
            xycoords='data',
            xytext=(0, -(STVV_PX // 2 + 12)),
            textcoords='offset pixels',
            ha='center', va='top',
            fontsize=12, fontweight='bold', color='white',
            annotation_clip=False,
            path_effects=[pe.withStroke(linewidth=3, foreground='#333333')],
            zorder=15)

# ── Title ─────────────────────────────────────────────────────────────────────
ax.text(0.013, 0.980,
        "2025−2026シーズンに\nスカウトに来たクラブ",
        transform=ax.transAxes,
        ha='left', va='top',
        fontsize=20, fontweight='bold',
        color='#1A2A4A',
        fontfamily='Noto Sans CJK JP',
        zorder=20,
        bbox=dict(boxstyle='round,pad=0.35',
                  facecolor='white', edgecolor='none', alpha=0.88),
        linespacing=1.35)

# ── Save ──────────────────────────────────────────────────────────────────────
ax.set_axis_off()
plt.savefig(OUT_FILE, dpi=DPI, bbox_inches='tight', pad_inches=0,
            facecolor='#4FAAD5')
plt.close()
print(f"Saved → {OUT_FILE}")
