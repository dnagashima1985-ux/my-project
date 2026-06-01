#!/usr/bin/env python3
"""
STVV Scout Map 2025-2026 — v5
NatGeo / Esri tile background + proper logo placement
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.font_manager as _fm
_fm.fontManager.addfont("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc")

import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.patches import Circle, Polygon as MplPoly
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
import numpy as np
from PIL import Image
from pyproj import Transformer
import contextily as ctx
import os

LOGOS_DIR = "/home/user/my-project/logos"
OUT_FILE  = "/home/user/my-project/scout_map_v6.png"
DPI  = 160
FW, FH = 22.0, 12.375   # 16:9 inches

# Geographic bounds (WGS84)
W_LON, E_LON =  -11.5, 27.5
S_LAT, N_LAT =   34.5, 60.5

STVV_LAT, STVV_LON = 50.815, 5.168

# ── Coordinate helpers ───────────────────────────────────────────────────────
_to_merc = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)

def ll2web(lat, lon):
    """WGS84 → Web Mercator (EPSG:3857)"""
    x, y = _to_merc.transform(lon, lat)
    return x, y

stvv_wx, stvv_wy = ll2web(STVV_LAT, STVV_LON)

# Bounding box in Web Mercator
xmin, ymin = ll2web(S_LAT, W_LON)
xmax, ymax = ll2web(N_LAT, E_LON)

# ── Club data ─────────────────────────────────────────────────────────────────
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

# ── Logo loader ───────────────────────────────────────────────────────────────
def load_logo(abbr, px):
    path = os.path.join(LOGOS_DIR, f"{abbr}.png")
    if not os.path.exists(path) or os.path.getsize(path) < 500:
        return None
    try:
        img = Image.open(path).convert("RGBA")
        w, h = img.size
        if max(w,h)/min(w,h) > 2.2:
            return None
        arr0 = np.array(img)
        if (arr0[...,3] < 200).mean() < 0.08:
            return None
        s = px / max(w, h)
        img = img.resize((max(1,int(w*s)), max(1,int(h*s))), Image.LANCZOS)
        return np.array(img)
    except:
        return None

# ── Figure (plain matplotlib, no Cartopy) ────────────────────────────────────
fig, ax = plt.subplots(figsize=(FW, FH), dpi=DPI)
plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
ax.set_xlim(xmin, xmax)
ax.set_ylim(ymin, ymax)
ax.set_aspect('equal')
ax.axis('off')

# ── Download and draw NatGeo tile background ──────────────────────────────────
print("Downloading map tiles…")
try:
    tile_img, tile_ext = ctx.bounds2img(
        xmin, ymin, xmax, ymax, zoom=5,
        source=ctx.providers.Esri.WorldPhysical,
        ll=False
    )
    # Brighten the ocean (blue channel boost) for a softer, more vivid look
    from PIL import Image as _PIL
    pil = _PIL.fromarray(tile_img[..., :3])
    import PIL.ImageEnhance as _IE
    pil = _IE.Color(pil).enhance(1.35)   # more saturation
    pil = _IE.Brightness(pil).enhance(1.08)
    tile_img_adj = np.array(pil)
    ax.imshow(tile_img_adj, extent=tile_ext, origin='upper',
              aspect='auto', zorder=0)
    print("WorldPhysical tiles OK")
except Exception as e:
    print(f"Tile failed ({e}), plain bg")
    ax.set_facecolor('#4FAAD5')

# ── Web Mercator helpers ──────────────────────────────────────────────────────
# Figure pixels from Web Mercator coords
def wm2px(wx, wy):
    """Web Mercator → figure pixel (display) coords."""
    fig.canvas.draw()
    return ax.transData.transform((wx, wy))

def px2wm(px_x, px_y):
    """Display pixels → Web Mercator."""
    return ax.transData.inverted().transform((px_x, px_y))

# ── Starburst from STVV ───────────────────────────────────────────────────────
RAY = 1.4e7
for i in range(40):
    a = np.radians(i * 9)
    lw, al = (7, 0.28) if i%2==0 else (3.5, 0.14)
    ax.plot([stvv_wx, stvv_wx+RAY*np.cos(a)],
            [stvv_wy, stvv_wy+RAY*np.sin(a)],
            color='white', lw=lw, alpha=al, zorder=3,
            solid_capstyle='round', transform=ax.transData)

# Glow
for r,a in [(500000,0.07),(300000,0.15),(160000,0.26),(75000,0.42)]:
    ax.add_patch(Circle((stvv_wx,stvv_wy), r, color='white',
                         alpha=a, zorder=4, transform=ax.transData))

# ── Init transforms ───────────────────────────────────────────────────────────
fig.canvas.draw()
inv = ax.transData.inverted()

LOGO_PX = 62
STVV_PX = 152

entries = []
for abbr, lat, lon in CLUBS:
    wx, wy = ll2web(lat, lon)
    px, py = ax.transData.transform((wx, wy))
    entries.append([px, py, wx, wy, abbr])

stvv_entry = next(e for e in entries if e[4]=="STVV")
stvv_px_x, stvv_px_y = stvv_entry[0], stvv_entry[1]
others = [e for e in entries if e[4]!="STVV"]

# ── Overlap resolution ────────────────────────────────────────────────────────
origins = [(e[0],e[1]) for e in others]
need = LOGO_PX + 7

for iteration in range(3000):
    moved = False
    for i in range(len(others)):
        for j in range(i+1, len(others)):
            dx = others[i][0] - others[j][0]
            dy = others[i][1] - others[j][1]
            d  = (dx*dx+dy*dy)**0.5
            if d < need and d > 0.1:
                push = (need-d) / 2.05
                nx, ny = dx/d, dy/d
                others[i][0] += nx*push;  others[i][1] += ny*push
                others[j][0] -= nx*push;  others[j][1] -= ny*push
                moved = True
    # Clamp drift from origin
    for i,e in enumerate(others):
        ox,oy = origins[i]
        ddx,ddy = e[0]-ox, e[1]-oy
        drift = (ddx*ddx+ddy*ddy)**0.5
        MAX_DRIFT = 260
        if drift > MAX_DRIFT:
            s = MAX_DRIFT/drift
            e[0] = ox+ddx*s; e[1] = oy+ddy*s
    if not moved:
        break

# Convert resolved display positions back to Web Mercator
for e in others:
    wx, wy = inv.transform((e[0], e[1]))
    e[2], e[3] = wx, wy

# ── Lines from STVV to city dots ──────────────────────────────────────────────
for abbr, lat, lon in CLUBS:
    if abbr == "STVV": continue
    cwx, cwy = ll2web(lat, lon)
    ax.plot([stvv_wx, cwx], [stvv_wy, cwy],
            color='white', lw=0.75, alpha=0.55, zorder=5,
            solid_capstyle='round')

# ── City glow dots ────────────────────────────────────────────────────────────
for abbr, lat, lon in CLUBS:
    if abbr == "STVV": continue
    cwx, cwy = ll2web(lat, lon)
    c = COLORS.get(abbr, "#AAAAAA")
    for r,a in [(60000,0.20),(38000,0.42),(18000,0.80)]:
        ax.add_patch(Circle((cwx,cwy), r, color=c, alpha=a, zorder=6))
    ax.add_patch(Circle((cwx,cwy), 8000, color='white', zorder=7))

# ── Logo placement ────────────────────────────────────────────────────────────
def place(abbr, wx, wy, px_size, z=8):
    arr = load_logo(abbr, px_size)
    c   = COLORS.get(abbr, "#888888")
    if arr is not None:
        sh = arr.copy(); sh[..., :3] = 0
        sh[..., 3] = (sh[..., 3] * 0.28).astype(np.uint8)
        ax.add_artist(AnnotationBbox(
            OffsetImage(sh, zoom=1.0, interpolation='lanczos'),
            (wx+14000, wy-14000),
            frameon=False, zorder=z, xycoords='data',
            box_alignment=(0.5, 0.5)))
        ax.add_artist(AnnotationBbox(
            OffsetImage(arr, zoom=1.0, interpolation='lanczos'),
            (wx, wy), frameon=False, zorder=z+1, xycoords='data',
            box_alignment=(0.5, 0.5)))
    else:
        R = px_size / DPI * 55000
        ax.add_patch(Circle((wx,wy), R+9000, color='white', zorder=z))
        ax.add_patch(Circle((wx,wy), R, color=c, zorder=z+1))
        ax.text(wx, wy, abbr[:4], ha='center', va='center',
                fontsize=6, fontweight='bold', color='white', zorder=z+2,
                path_effects=[pe.withStroke(linewidth=1.2, foreground='black')])

for e in others:
    place(e[4], e[2], e[3], LOGO_PX)

# ── STVV ─────────────────────────────────────────────────────────────────────
place("STVV", stvv_wx, stvv_wy, STVV_PX, z=14)

# Gold pin
PIN_OFF = 110000
pin_r   = 44000
pin_wx, pin_wy = stvv_wx, stvv_wy + PIN_OFF
for pr, pc in [(pin_r+13000,'#A07000'),(pin_r+5000,'#FFD700'),(pin_r,'#FDB913')]:
    ax.add_patch(Circle((pin_wx,pin_wy), pr, color=pc, zorder=15))
ax.add_patch(Circle((pin_wx,pin_wy), pin_r*0.38, color='white', zorder=16))
tail = [(pin_wx, stvv_wy+20000),
        (pin_wx-pin_r*0.65, pin_wy-pin_r*0.5),
        (pin_wx+pin_r*0.65, pin_wy-pin_r*0.5)]
ax.add_patch(MplPoly(tail, closed=True, facecolor='#FDB913',
                      edgecolor='#A07000', lw=1.5, zorder=15))

ax.annotate("STVV", xy=(stvv_wx, stvv_wy),
            xytext=(0, -(STVV_PX//2+14)), textcoords='offset pixels',
            ha='center', va='top', fontsize=13, fontweight='bold',
            color='white', annotation_clip=False, zorder=17,
            path_effects=[pe.withStroke(linewidth=3.5, foreground='#222')])

# ── Title ─────────────────────────────────────────────────────────────────────
ax.text(0.012, 0.978,
        "2025−2026シーズンに\nスカウトに来たクラブ",
        transform=ax.transAxes, ha='left', va='top',
        fontsize=22, fontweight='bold', color='#1A2A4A',
        fontfamily='Noto Sans CJK JP', zorder=20, linespacing=1.30,
        bbox=dict(boxstyle='round,pad=0.40',
                  facecolor='white', edgecolor='none', alpha=0.90))

plt.savefig(OUT_FILE, dpi=DPI, bbox_inches='tight', pad_inches=0)
plt.close()
print(f"Saved → {OUT_FILE}")
