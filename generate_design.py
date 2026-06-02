#!/usr/bin/env python3
"""
STVV Scout Map 2025-2026 — REDESIGN
Design-focused: vivid colours, white-bordered logos, glow effects
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.font_manager as _fm
_fm.fontManager.addfont("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc")

import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.patches import Circle, Polygon as MplPoly, FancyBboxPatch
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw
from pyproj import Transformer
import contextily as ctx
import os

LOGOS_DIR = "/home/user/my-project/logos"
OUT_FILE  = "/home/user/my-project/scout_map_design.png"
DPI  = 160
FW, FH = 22.0, 12.375

W_LON, E_LON = -11.5, 27.5
S_LAT, N_LAT =  34.5, 60.5
STVV_LAT, STVV_LON = 50.815, 5.168

_to_merc = Transformer.from_crs("EPSG:4326","EPSG:3857",always_xy=True)
def ll2web(lat,lon): return _to_merc.transform(lon,lat)
xmin,ymin = ll2web(S_LAT,W_LON)
xmax,ymax = ll2web(N_LAT,E_LON)
stvv_wx,stvv_wy = ll2web(STVV_LAT,STVV_LON)

CLUBS = [
    ("STVV",  50.815,  5.168),
    ("HSV",   53.587,  9.900), ("FCSP",  53.554, 10.023),
    ("D98",   49.864,  8.648), ("B04",   51.038,  7.002),
    ("KOL",   50.934,  6.875), ("F95",   51.257,  6.734),
    ("BMG",   51.175,  6.385), ("S04",   51.554,  7.068),
    ("BVB",   51.493,  7.452), ("WOB",   52.432, 10.804),
    ("SVW",   53.066,  8.838), ("KSC",   49.023,  8.413),
    ("FCK",   49.434,  7.776), ("FCN",   49.424, 11.123),
    ("RBL",   51.346, 12.348), ("SGE",   50.069,  8.645),
    ("SCF",   47.987,  7.889), ("TSG",   49.238,  8.889),
    ("FCA",   48.323, 10.886), ("FCU",   52.457, 13.567),
    ("BSC",   52.514, 13.402), ("VFB",   48.792,  9.232),
    ("AJX",   52.314,  4.942), ("FCU2",  52.079,  5.116),
    ("AZ",    52.627,  4.749), ("FEY",   51.894,  4.523),
    ("PSV",   51.442,  5.467), ("FCT",   52.239,  6.803),
    ("RFC",   55.851, -4.309), ("NUFC",  54.976, -1.622),
    ("LUFC",  53.778, -1.572), ("BFC",   53.789, -2.230),
    ("PNE",   53.771, -2.687), ("MUFC",  53.463, -2.291),
    ("WWFC",  52.590, -2.130), ("COV",   52.408, -1.504),
    ("LCFC",  52.620, -1.142), ("OXF",   51.739, -1.247),
    ("SFC",   50.906, -1.391), ("WAT",   51.650, -0.402),
    ("THFC",  51.604, -0.066), ("QPR",   51.509, -0.232),
    ("WHU",   51.538,  0.017), ("MIL",   51.486, -0.050),
    ("FCL",   47.750, -3.367), ("SRFC",  48.107, -1.712),
    ("AJA",   47.795,  3.564), ("LOSC",  50.612,  3.130),
    ("SDR",   49.234,  4.026), ("PSG",   48.841,  2.253),
    ("PFC",   48.827,  2.404), ("CF63",  45.778,  3.117),
    ("OL",    45.765,  4.982), ("TFC",   43.582,  1.434),
    ("TOR",   45.109,  7.641), ("GEN",   44.416,  8.951),
    ("COM",   45.815,  9.085), ("ATA",   45.709,  9.680),
    ("MON",   45.586,  9.274), ("INTER", 45.478,  9.124),
    ("ACM",   45.478,  9.124), ("CREM",  45.120, 10.030),
    ("SASU",  44.549, 10.791), ("HVR",   45.439, 10.992),
    ("BOL",   44.492, 11.313), ("FIOR",  43.781, 11.283),
    ("PAR",   44.800, 10.336), ("CAG",   39.214,  9.137),
    ("RSPG",  43.540, -5.635), ("RSO",   43.301, -2.015),
    ("OSA",   42.796, -1.637), ("LEV",   39.474, -0.358),
    ("BETIS", 37.357, -5.982), ("RAPID", 48.196, 16.260),
    ("SLA",   50.068, 14.472), ("FKP",   49.744, 13.386),
    ("CZV",   44.786, 20.462), ("FCK2",  55.703, 12.576),
]

COLORS = {
    "STVV":"#FFDD00","HSV":"#009EE0","FCSP":"#824F20","D98":"#3D52B2",
    "B04":"#E32221","KOL":"#FF2000","F95":"#D2000B","BMG":"#444444",
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

# ── Logo loader with white-border framing ─────────────────────────────────────
def load_logo(abbr, inner_px, border=5):
    """Load logo, paste onto white circle with drop-shadow. Returns RGBA array."""
    path = os.path.join(LOGOS_DIR, f"{abbr}.png")
    ok = os.path.exists(path) and os.path.getsize(path) > 500
    total_px = inner_px + border * 2 + 4   # total badge size

    # Background circle (white disc)
    bg = Image.new("RGBA", (total_px, total_px), (0,0,0,0))
    draw = ImageDraw.Draw(bg)
    draw.ellipse([0,0,total_px-1,total_px-1], fill=(255,255,255,230))

    if ok:
        try:
            img = Image.open(path).convert("RGBA")
            w,h = img.size
            if max(w,h)/min(w,h) > 2.2: raise ValueError("panoramic")
            arr0 = np.array(img)
            if (arr0[...,3] < 200).mean() < 0.08: raise ValueError("photo")
            # Resize to fit inner circle
            s = inner_px / max(w,h)
            img = img.resize((max(1,int(w*s)), max(1,int(h*s))), Image.LANCZOS)
            # Centre-paste onto white circle
            pw, ph = img.size
            ox = (total_px - pw)//2
            oy = (total_px - ph)//2
            bg.paste(img, (ox, oy), img)
        except Exception:
            ok = False

    if not ok:
        # Coloured fallback circle with abbreviation
        c = COLORS.get(abbr, "#888888")
        r,g,b = int(c[1:3],16),int(c[3:5],16),int(c[5:7],16)
        draw.ellipse([border,border,total_px-border-1,total_px-border-1],
                     fill=(r,g,b,230))

    # Thin dark border ring
    draw.ellipse([1,1,total_px-2,total_px-2],
                 outline=(80,80,80,160), width=1)

    # Drop shadow (blurred dark copy below-right)
    shadow = Image.new("RGBA", (total_px+6, total_px+6), (0,0,0,0))
    sh_draw = ImageDraw.Draw(shadow)
    sh_draw.ellipse([3,3,total_px+2,total_px+2], fill=(0,0,0,70))
    shadow = shadow.filter(ImageFilter.GaussianBlur(3))

    canvas = Image.new("RGBA", (total_px+6, total_px+6), (0,0,0,0))
    canvas.paste(shadow, (0,0), shadow)
    canvas.paste(bg, (0,0), bg)
    return np.array(canvas)

# ── Figure ────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(FW, FH), dpi=DPI)
plt.subplots_adjust(left=0,right=1,top=1,bottom=0)
ax.set_xlim(xmin,xmax); ax.set_ylim(ymin,ymax)
ax.set_aspect('equal'); ax.axis('off')

# ── Background tile + strong colour grade ─────────────────────────────────────
print("Downloading tiles…")
tile_img, tile_ext = ctx.bounds2img(xmin,ymin,xmax,ymax,zoom=5,
    source=ctx.providers.Esri.WorldPhysical, ll=False)

pil = Image.fromarray(tile_img[...,:3])
pil = ImageEnhance.Color(pil).enhance(1.6)       # vivid colours
pil = ImageEnhance.Brightness(pil).enhance(1.12)
pil = ImageEnhance.Contrast(pil).enhance(1.10)
ax.imshow(np.array(pil), extent=tile_ext, origin='upper', aspect='auto', zorder=0)
print("Tiles OK")

# ── Starburst ─────────────────────────────────────────────────────────────────
RAY = 1.5e7
for i in range(48):
    a  = np.radians(i * 7.5)
    lw = 10 if i%3==0 else (5 if i%3==1 else 2.5)
    al = 0.32 if i%3==0 else (0.18 if i%3==1 else 0.09)
    ax.plot([stvv_wx, stvv_wx+RAY*np.cos(a)],
            [stvv_wy, stvv_wy+RAY*np.sin(a)],
            color='white', lw=lw, alpha=al, zorder=3,
            solid_capstyle='round')

# Central glow
for r,a in [(600000,0.06),(380000,0.13),(220000,0.24),(110000,0.40),(50000,0.55)]:
    ax.add_patch(Circle((stvv_wx,stvv_wy), r, color='white',
                         alpha=a, zorder=4))

# ── Init display transform ────────────────────────────────────────────────────
fig.canvas.draw()
inv = ax.transData.inverted()

LOGO_PX  = 46
STVV_PX  = 148
BORDER   = 6
NEED     = LOGO_PX + BORDER*2 + 8   # clear gap between badge outer edges

entries = []
for abbr,lat,lon in CLUBS:
    wx,wy = ll2web(lat,lon)
    px,py = ax.transData.transform((wx,wy))
    entries.append([px,py,wx,wy,abbr])

stvv_e = next(e for e in entries if e[4]=="STVV")
stvv_px_x, stvv_px_y = stvv_e[0], stvv_e[1]
others = [e for e in entries if e[4]!="STVV"]

# ── Greedy no-overlap placement ───────────────────────────────────────────────
HALF_B = (LOGO_PX + BORDER*2 + 4) // 2
MARGIN = HALF_B + 4
PX_MIN, PX_MAX = MARGIN, FW*DPI - MARGIN
PY_MIN, PY_MAX = MARGIN, FH*DPI - MARGIN
MIN_STVV = STVV_PX * 0.60

def ok(cx,cy,placed):
    if not (PX_MIN<=cx<=PX_MAX and PY_MIN<=cy<=PY_MAX): return False
    if (cx-stvv_px_x)**2+(cy-stvv_px_y)**2 < MIN_STVV**2: return False
    for px2,py2 in placed:
        if (cx-px2)**2+(cy-py2)**2 < NEED**2: return False
    return True

others_sorted = sorted(others,
    key=lambda e: -((e[0]-stvv_px_x)**2+(e[1]-stvv_px_y)**2)**0.5)

placed = []
for e in others_sorted:
    ox,oy = e[0],e[1]
    bearing = np.arctan2(oy-stvv_px_y, ox-stvv_px_x)
    found = False
    for dist in range(0, 750, 3):
        offsets = [0]
        for k in range(1, 36):
            offsets += [k*10, -k*10]
        for a_off in offsets:
            cx = ox + dist*np.cos(bearing+np.radians(a_off))
            cy = oy + dist*np.sin(bearing+np.radians(a_off))
            if ok(cx,cy,placed):
                e[0],e[1] = cx,cy
                placed.append((cx,cy))
                found = True; break
        if found: break
    if not found:
        placed.append((ox,oy))

overlaps = sum(1 for i in range(len(others)) for j in range(i+1,len(others))
               if ((others[i][0]-others[j][0])**2+(others[i][1]-others[j][1])**2)**0.5<NEED)
print(f"Overlaps: {overlaps}")

# Convert back to Web Mercator
for e in others:
    e[2],e[3] = inv.transform((e[0],e[1]))

# ── Lines from STVV to city dots ──────────────────────────────────────────────
for abbr,lat,lon in CLUBS:
    if abbr=="STVV": continue
    cwx,cwy = ll2web(lat,lon)
    ax.plot([stvv_wx,cwx],[stvv_wy,cwy],
            color='white',lw=0.6,alpha=0.45,zorder=5,solid_capstyle='round')

# ── Glowing city dots ─────────────────────────────────────────────────────────
for abbr,lat,lon in CLUBS:
    if abbr=="STVV": continue
    cwx,cwy = ll2web(lat,lon)
    c = COLORS.get(abbr,"#AAAAAA")
    for r,a in [(65000,0.18),(40000,0.40),(18000,0.80)]:
        ax.add_patch(Circle((cwx,cwy),r,color=c,alpha=a,zorder=6))
    ax.add_patch(Circle((cwx,cwy),8000,color='white',zorder=7))

# ── Place logos ───────────────────────────────────────────────────────────────
def place(abbr, wx, wy, inner_px, z=8):
    arr = load_logo(abbr, inner_px, border=BORDER)
    ab = AnnotationBbox(
        OffsetImage(arr, zoom=1.0, interpolation='lanczos'),
        (wx, wy), frameon=False, zorder=z, xycoords='data',
        box_alignment=(0.5, 0.5))
    ax.add_artist(ab)

for e in others:
    place(e[4], e[2], e[3], LOGO_PX)

# ── STVV centre ───────────────────────────────────────────────────────────────
place("STVV", stvv_wx, stvv_wy, STVV_PX, z=14)

# Gold pin above STVV
PIN_OFF = 120000
pin_r   = 48000
pin_wx, pin_wy = stvv_wx, stvv_wy + PIN_OFF
for pr,pc in [(pin_r+16000,'#8B6914'),(pin_r+7000,'#FFD700'),(pin_r,'#FDB913')]:
    ax.add_patch(Circle((pin_wx,pin_wy),pr,color=pc,zorder=15))
ax.add_patch(Circle((pin_wx,pin_wy),pin_r*0.38,color='white',zorder=16))
tail=[(pin_wx, stvv_wy+22000),
      (pin_wx-pin_r*0.65, pin_wy-pin_r*0.55),
      (pin_wx+pin_r*0.65, pin_wy-pin_r*0.55)]
ax.add_patch(MplPoly(tail,closed=True,facecolor='#FDB913',
                      edgecolor='#8B6914',lw=1.5,zorder=15))

ax.annotate("STVV", xy=(stvv_wx,stvv_wy),
            xytext=(0,-(STVV_PX//2+BORDER+18)), textcoords='offset pixels',
            ha='center', va='top', fontsize=13, fontweight='bold',
            color='white', annotation_clip=False, zorder=17,
            path_effects=[pe.withStroke(linewidth=4,foreground='#1a1a1a')])

# ── Title banner (top-left gradient box) ─────────────────────────────────────
# Gradient bar using a rectangle image
bar_w_ax = 0.30
bar_h_ax = 0.115
bar_x, bar_y = 0.008, 0.870   # axes fractions (bottom-left of bar)

# Dark blue gradient rectangle
grad = np.zeros((80, 400, 4), dtype=np.uint8)
for col in range(400):
    alpha = int(220 - col * 0.38)
    grad[:, col] = [15, 40, 90, max(0, alpha)]
ax.imshow(grad, extent=[
    xmin + (xmax-xmin)*bar_x,
    xmin + (xmax-xmin)*(bar_x+bar_w_ax),
    ymin + (ymax-ymin)*bar_y,
    ymin + (ymax-ymin)*(bar_y+bar_h_ax),
], origin='upper', aspect='auto', zorder=19, alpha=1)

ax.text(bar_x + 0.008, bar_y + bar_h_ax*0.88,
        "2025−2026シーズンに",
        transform=ax.transAxes, ha='left', va='top',
        fontsize=19, fontweight='bold', color='white',
        fontfamily='Noto Sans CJK JP', zorder=20,
        path_effects=[pe.withStroke(linewidth=2,foreground='#0a1e5e')])
ax.text(bar_x + 0.008, bar_y + bar_h_ax*0.40,
        "スカウトに来たクラブ",
        transform=ax.transAxes, ha='left', va='top',
        fontsize=19, fontweight='bold', color='#FFD700',
        fontfamily='Noto Sans CJK JP', zorder=20,
        path_effects=[pe.withStroke(linewidth=2,foreground='#0a1e5e')])

# Yellow accent bar at left edge of title
ax.add_patch(FancyBboxPatch(
    (xmin+(xmax-xmin)*(bar_x-0.003),
     ymin+(ymax-ymin)*bar_y),
    (xmax-xmin)*0.003,
    (ymax-ymin)*bar_h_ax,
    boxstyle='square,pad=0', facecolor='#FFD700', edgecolor='none',
    zorder=20))

plt.savefig(OUT_FILE, dpi=DPI, bbox_inches='tight', pad_inches=0)
plt.close()
print(f"Saved → {OUT_FILE}")
