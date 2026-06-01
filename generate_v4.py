#!/usr/bin/env python3
"""
STVV Scout Map 2025-2026 — v4
Tile-based background (CartoDB) + large logos + reference-style design
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.font_manager as _fm
_fm.fontManager.addfont("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc")

import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.patches import Circle, Polygon as MplPoly, FancyBboxPatch
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
import matplotlib.colors as mc
import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance
import os, io

LOGOS_DIR = "/home/user/my-project/logos"
OUT_FILE  = "/home/user/my-project/scout_map_v4.png"
DPI  = 160
FW, FH = 22.0, 12.375   # 16:9

EXTENT   = [-11.5, 27.5, 34.5, 60.5]   # lon_min lon_max lat_min lat_max
PROJ     = ccrs.Mercator()
PC       = ccrs.PlateCarree()

STVV_LAT, STVV_LON = 50.815, 5.168

# ── Club list (abbr, lat, lon) ────────────────────────────────────────────────
CLUBS = [
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
    ("RFC",   55.851, -4.309),
    ("NUFC",  54.976, -1.622),
    ("LUFC",  53.778, -1.572),
    ("BFC",   53.789, -2.230),
    ("PNE",   53.771, -2.687),
    ("MUFC",  53.463, -2.291),
    ("WWFC",  52.590, -2.130),
    ("COV",   52.408, -1.504),
    ("LCFC",  52.620, -1.142),
    ("OXF",   51.739, -1.247),
    ("SFC",   50.906, -1.391),
    ("WAT",   51.650, -0.402),
    ("THFC",  51.604, -0.066),
    ("QPR",   51.509, -0.232),
    ("WHU",   51.538,  0.017),
    ("MIL",   51.486, -0.050),
    # France
    ("FCL",   47.750, -3.367),
    ("SRFC",  48.107, -1.712),
    ("AJA",   47.795,  3.564),
    ("LOSC",  50.612,  3.130),
    ("SDR",   49.234,  4.026),
    ("PSG",   48.841,  2.253),
    ("PFC",   48.827,  2.404),
    ("CF63",  45.778,  3.117),
    ("OL",    45.765,  4.982),
    ("TFC",   43.582,  1.434),
    # Italy
    ("TOR",   45.109,  7.641),
    ("GEN",   44.416,  8.951),
    ("COM",   45.815,  9.085),
    ("ATA",   45.709,  9.680),
    ("MON",   45.586,  9.274),
    ("INTER", 45.478,  9.124),
    ("ACM",   45.478,  9.124),
    ("CREM",  45.120, 10.030),
    ("SASU",  44.549, 10.791),
    ("HVR",   45.439, 10.992),
    ("BOL",   44.492, 11.313),
    ("FIOR",  43.781, 11.283),
    ("PAR",   44.800, 10.336),
    ("CAG",   39.214,  9.137),
    # Spain
    ("RSPG",  43.540, -5.635),
    ("RSO",   43.301, -2.015),
    ("OSA",   42.796, -1.637),
    ("LEV",   39.474, -0.358),
    ("BETIS", 37.357, -5.982),
    # Others
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
    "FCT":"#E2001A","RFC":"#0000CC","NUFC":"#111111","LUFC":"#1D428A",
    "BFC":"#6C1D45","PNE":"#888888","MUFC":"#DA020E","WWFC":"#FDB913",
    "COV":"#75AADB","LCFC":"#003090","OXF":"#FFD700","SFC":"#D71920",
    "WAT":"#FBEE23","THFC":"#132257","QPR":"#1D5BA4","WHU":"#7A263A",
    "MIL":"#001D5E","FCL":"#F47920","SRFC":"#111111","AJA":"#888888",
    "LOSC":"#E31E25","SDR":"#E30613","PSG":"#004170","PFC":"#002D5E",
    "CF63":"#AB192B","OL":"#002855","TFC":"#7B2D8B","TOR":"#8B1A1A",
    "GEN":"#CC0000","COM":"#0033A0","ATA":"#1E3E85","MON":"#CC0000",
    "INTER":"#0068A8","ACM":"#FB090B","CREM":"#9B1730","SASU":"#2D6741",
    "HVR":"#FFD700","BOL":"#003591","FIOR":"#4C247D","PAR":"#0058A0",
    "CAG":"#003595","RSPG":"#CC0000","RSO":"#0067B1","OSA":"#CC0000",
    "LEV":"#0047AB","BETIS":"#00833F","RAPID":"#007A3D","SLA":"#CC0000",
    "FKP":"#002D62","CZV":"#CC0000","FCK2":"#0B479D",
}

# ── Logo loading ──────────────────────────────────────────────────────────────
def load_logo(abbr, px):
    path = os.path.join(LOGOS_DIR, f"{abbr}.png")
    if not os.path.exists(path) or os.path.getsize(path) < 500:
        return None
    try:
        img = Image.open(path).convert("RGBA")
        w, h = img.size
        # Reject panoramic / stadium photos
        if max(w,h)/min(w,h) > 2.2:
            return None
        # Reject images with very little transparency (likely photos)
        arr0 = np.array(img)
        transparent_ratio = (arr0[..., 3] < 200).mean()
        if transparent_ratio < 0.08:   # almost no transparent pixels → photo
            return None
        s = px / max(w, h)
        img = img.resize((max(1,int(w*s)), max(1,int(h*s))), Image.LANCZOS)
        return np.array(img)
    except:
        return None

def ll2merc(lat, lon):
    return PROJ.transform_point(lon, lat, PC)

stvv_mx, stvv_my = ll2merc(STVV_LAT, STVV_LON)

# ── Figure ────────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(FW, FH), dpi=DPI)
ax  = fig.add_subplot(1, 1, 1, projection=PROJ)
ax.set_extent(EXTENT, crs=PC)
plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

# ── Tile background ───────────────────────────────────────────────────────────
# Use CartoDB Voyager — clean, light terrain-style, great colours
try:
    tiles = cimgt.GoogleTiles(style='satellite')
    ax.add_image(tiles, 5)   # zoom 5 → continental scale
    print("Satellite tiles loaded")
except Exception as e:
    print(f"Tile fallback: {e}")
    # Fallback: custom styled map via OSM
    try:
        tiles2 = cimgt.OSM()
        ax.add_image(tiles2, 5)
        print("OSM tiles loaded")
    except Exception as e2:
        print(f"OSM also failed: {e2}")
        # Plain cartopy
        import cartopy.feature as cfeature
        ax.add_feature(cfeature.OCEAN.with_scale('50m'), facecolor='#4FAAD5')
        ax.add_feature(cfeature.LAND.with_scale('50m'),  facecolor='#CEDE8E',
                       edgecolor='#7AA045', lw=0.5)
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), lw=0.7, edgecolor='#5A8832')
        ax.add_feature(cfeature.BORDERS.with_scale('50m'),   lw=0.4, edgecolor='#7AA045', ls='--')

# Apply a colour grade overlay to match reference (bright blue sea, light green land)
# Stretch a gradient across the whole canvas
from matplotlib.patches import Rectangle
# Subtle blue tint over the whole map
ax.add_patch(Rectangle((ax.get_xlim()[0] if hasattr(ax,'get_xlim') else -1.3e7,
                          -1e7), 3e7, 3e7,
              facecolor='none', edgecolor='none', zorder=0))

# ── Starburst ─────────────────────────────────────────────────────────────────
RAY = 1.3e7
for i in range(40):
    a = np.radians(i * 9)
    lw, al = (7, 0.28) if i%2==0 else (3.5, 0.15)
    ax.plot([stvv_mx, stvv_mx + RAY*np.cos(a)],
            [stvv_my, stvv_my + RAY*np.sin(a)],
            color='white', lw=lw, alpha=al, zorder=4,
            transform=ax.transData, solid_capstyle='round')

# Inner glow
for r, a in [(500000,0.07),(300000,0.15),(160000,0.25),(80000,0.40)]:
    ax.add_patch(Circle((stvv_mx, stvv_my), r, color='white',
                         alpha=a, zorder=5, transform=ax.transData))

# ── Initialise display transforms ─────────────────────────────────────────────
fig.canvas.draw()
inv = ax.transData.inverted()

# Build entry list in display pixels
LOGO_PX   = 72
STVV_PX   = 160

entries = []
for abbr, lat, lon in CLUBS:
    mx, my = ll2merc(lat, lon)
    px, py = ax.transData.transform((mx, my))
    entries.append([px, py, mx, my, abbr])

stvv_px, stvv_py = next((e[0],e[1]) for e in entries if e[4]=="STVV")
others = [e for e in entries if e[4]!="STVV"]

# ── Overlap resolution (display pixels) ───────────────────────────────────────
origins = [(e[0],e[1]) for e in others]
need = LOGO_PX + 6

for _ in range(2500):
    moved = False
    for i in range(len(others)):
        for j in range(i+1, len(others)):
            dx = others[i][0]-others[j][0]
            dy = others[i][1]-others[j][1]
            d  = (dx*dx+dy*dy)**0.5
            if d < need and d > 0.1:
                push = (need-d)/2.1
                nx,ny = dx/d, dy/d
                others[i][0] += nx*push; others[i][1] += ny*push
                others[j][0] -= nx*push; others[j][1] -= ny*push
                moved = True
    # Clamp drift
    for i,e in enumerate(others):
        ox,oy = origins[i]
        ddx,ddy = e[0]-ox, e[1]-oy
        drift = (ddx*ddx+ddy*ddy)**0.5
        MAX = 230
        if drift > MAX:
            s = MAX/drift
            e[0] = ox+ddx*s; e[1] = oy+ddy*s
    if not moved:
        break

# Convert back to Mercator data coords
for e in others:
    e[2], e[3] = inv.transform((e[0], e[1]))

# ── Lines from STVV to each city ──────────────────────────────────────────────
for abbr, lat, lon in CLUBS:
    if abbr == "STVV": continue
    cmx, cmy = ll2merc(lat, lon)
    ax.plot([stvv_mx, cmx], [stvv_my, cmy],
            color='white', lw=0.8, alpha=0.55, zorder=6,
            transform=ax.transData, solid_capstyle='round')

# ── City glow dots (actual geographic position) ───────────────────────────────
for abbr, lat, lon in CLUBS:
    if abbr == "STVV": continue
    cmx, cmy = ll2merc(lat, lon)
    c = COLORS.get(abbr, "#AAAAAA")
    for r,a in [(65000,0.18),(40000,0.38),(20000,0.72)]:
        ax.add_patch(Circle((cmx,cmy), r, color=c, alpha=a,
                             zorder=7, transform=ax.transData))
    ax.add_patch(Circle((cmx,cmy), 9000, color='white',
                         zorder=8, transform=ax.transData))

# ── Place logos ───────────────────────────────────────────────────────────────
def place(abbr, data_x, data_y, px, z=9):
    arr = load_logo(abbr, px)
    c   = COLORS.get(abbr, "#888")
    if arr is not None:
        # drop shadow
        sh = arr.copy()
        sh[..., :3] = 0
        sh[..., 3] = (sh[..., 3] * 0.30).astype(np.uint8)
        ax.add_artist(AnnotationBbox(
            OffsetImage(sh, zoom=1.0, interpolation='lanczos'),
            (data_x+15000, data_y-15000),
            frameon=False, zorder=z, xycoords='data', box_alignment=(.5,.5)))
        ax.add_artist(AnnotationBbox(
            OffsetImage(arr, zoom=1.0, interpolation='lanczos'),
            (data_x, data_y),
            frameon=False, zorder=z+1, xycoords='data', box_alignment=(.5,.5)))
    else:
        # fallback badge
        R = px/DPI * 55000
        ax.add_patch(Circle((data_x,data_y), R+9000, color='white',
                             zorder=z, transform=ax.transData))
        ax.add_patch(Circle((data_x,data_y), R, color=c,
                             zorder=z+1, transform=ax.transData))
        ax.text(data_x, data_y, abbr[:4], ha='center', va='center',
                fontsize=6, fontweight='bold', color='white',
                zorder=z+2, transform=ax.transData,
                path_effects=[pe.withStroke(linewidth=1.2, foreground='black')])

for e in others:
    place(e[4], e[2], e[3], LOGO_PX)

# ── STVV (center, large) ─────────────────────────────────────────────────────
place("STVV", stvv_mx, stvv_my, STVV_PX, z=14)

# Gold location pin
PIN_Y_OFF = 120000   # metres above centre
pin_r     = 42000
pin_mx, pin_my = stvv_mx, stvv_my + PIN_Y_OFF
for pr, pc in [(pin_r+12000,'#A07000'),(pin_r+5000,'#FFD700'),(pin_r,'#FDB913')]:
    ax.add_patch(Circle((pin_mx,pin_my), pr, color=pc,
                         zorder=15, transform=ax.transData))
ax.add_patch(Circle((pin_mx,pin_my), pin_r*0.38, color='white',
                     zorder=16, transform=ax.transData))
# Tail
tail = [(pin_mx, stvv_my+18000),
        (pin_mx-pin_r*0.65, pin_my-pin_r*0.5),
        (pin_mx+pin_r*0.65, pin_my-pin_r*0.5)]
ax.add_patch(MplPoly(tail, closed=True, facecolor='#FDB913',
                      edgecolor='#A07000', lw=1.5,
                      zorder=15, transform=ax.transData))

# "STVV" label
ax.annotate("STVV", xy=(stvv_mx, stvv_my),
            xytext=(0, -(STVV_PX//2+16)), textcoords='offset pixels',
            ha='center', va='top', fontsize=13, fontweight='bold',
            color='white', annotation_clip=False, zorder=17,
            path_effects=[pe.withStroke(linewidth=3.5, foreground='#222222')])

# ── Title (top-left) ─────────────────────────────────────────────────────────
ax.text(0.012, 0.978,
        "2025−2026シーズンに\nスカウトに来たクラブ",
        transform=ax.transAxes, ha='left', va='top',
        fontsize=22, fontweight='bold', color='#1A2A4A',
        fontfamily='Noto Sans CJK JP', zorder=20,
        linespacing=1.30,
        bbox=dict(boxstyle='round,pad=0.40',
                  facecolor='white', edgecolor='none', alpha=0.90))

ax.set_axis_off()
plt.savefig(OUT_FILE, dpi=DPI, bbox_inches='tight', pad_inches=0,
            facecolor='#4FAAD5')
plt.close()
print(f"Saved → {OUT_FILE}")
