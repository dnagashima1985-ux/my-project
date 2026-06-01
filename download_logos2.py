#!/usr/bin/env python3
"""
Download club logos using alternative Wikipedia/Wikimedia API methods.
For clubs that failed with pithumbsize, try:
1. prop=pageimages with piprop=original
2. prop=images to get image list, then find logo file
3. Wikimedia Commons direct URL construction
"""
import os
import sys
import json
import time
import random
import urllib.request
import urllib.parse
import urllib.error
import io
from PIL import Image

LOGO_DIR = "/home/user/my-project/logos"
os.makedirs(LOGO_DIR, exist_ok=True)

# Only clubs that still need logos
CLUBS_NEEDED = [
    ("STVV",  "Sint-Truidense_VV"),
    ("FCSP",  "FC_St._Pauli"),
    ("D98",   "SV_Darmstadt_98"),
    ("B04",   "Bayer_04_Leverkusen"),
    ("SVW",   "Werder_Bremen"),
    ("RBL",   "RB_Leipzig"),
    ("SGE",   "Eintracht_Frankfurt"),
    ("SCF",   "SC_Freiburg"),
    ("FCA",   "FC_Augsburg"),
    ("AZ",    "AZ_(football_club)"),
    ("PSV",   "PSV_Eindhoven"),
    ("FCT",   "FC_Twente"),
    ("SFC",   "Southampton_F.C."),
    ("COV",   "Coventry_City_F.C."),
    ("OXF",   "Oxford_United_F.C."),
    ("MIL",   "Millwall_F.C."),
    ("NUFC",  "Newcastle_United_F.C."),
    ("MUFC",  "Manchester_United_F.C."),
    ("WHU",   "West_Ham_United_F.C."),
    ("THFC",  "Tottenham_Hotspur_F.C."),
    ("LCFC",  "Leicester_City_F.C."),
    ("LUFC",  "Leeds_United_F.C."),
    ("BFC",   "Burnley_F.C."),
    ("WAT",   "Watford_F.C."),
    ("PNE",   "Preston_North_End_F.C."),
    ("RFC",   "Rangers_F.C."),
    ("AJA",   "AJ_Auxerre"),
    ("LOSC",  "Lille_OSC"),
    ("PSG",   "Paris_Saint-Germain_F.C."),
    ("PFC",   "Paris_FC"),
    ("SRFC",  "Stade_Rennais_F.C."),
    ("FCL",   "FC_Lorient"),
    ("OL",    "Olympique_Lyonnais"),
    ("CF63",  "Clermont_Foot_63"),
    ("TFC",   "Toulouse_FC"),
    ("TOR",   "Torino_F.C."),
    ("SASU",  "U.S._Sassuolo_Calcio"),
    ("BOL",   "Bologna_F.C._1909"),
    ("HVR",   "Hellas_Verona_F.C."),
    ("ATA",   "Atalanta_B.C."),
    ("INTER", "FC_Internazionale_Milano"),
    ("ACM",   "A.C._Milan"),
    ("CREM",  "U.S._Cremonese"),
    ("GEN",   "Genoa_C.F.C."),
    ("MON",   "A.C._Monza"),
    ("CAG",   "Cagliari_Calcio"),
    ("LEV",   "Levante_UD"),
    ("BETIS", "Real_Betis"),
    ("RSO",   "Real_Sociedad"),
    ("RSPG",  "Real_Sporting_de_Gijón"),
    ("FKP",   "FC_Viktoria_Plzeň"),
    ("CZV",   "FK_Crvena_zvezda"),
    ("FCK2",  "FC_Copenhagen"),
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 ScoutMapBot/1.0",
    "Accept": "application/json,*/*",
}

def fetch_url(url, timeout=20, retries=3, extra_headers=None):
    headers = dict(HEADERS)
    if extra_headers:
        headers.update(extra_headers)
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read()
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = 8 + attempt * 8 + random.random() * 4
                print(f"    Rate limited (429), waiting {wait:.0f}s...")
                time.sleep(wait)
            elif e.code in (403, 404):
                raise
            else:
                wait = 3 + attempt * 3
                time.sleep(wait)
        except Exception:
            if attempt < retries - 1:
                time.sleep(3)
            else:
                raise
    raise Exception(f"Failed after {retries} attempts")

def method1_original(wiki_page):
    """Try prop=pageimages with piprop=original."""
    api = (
        "https://en.wikipedia.org/w/api.php"
        f"?action=query&titles={urllib.parse.quote(wiki_page)}"
        f"&prop=pageimages&format=json&piprop=original"
    )
    data = json.loads(fetch_url(api))
    pages = data.get("query", {}).get("pages", {})
    for page in pages.values():
        orig = page.get("original", {})
        if orig:
            return orig.get("source")
    return None

def method2_images_list(wiki_page):
    """Get list of images on page, find the logo SVG/PNG."""
    api = (
        "https://en.wikipedia.org/w/api.php"
        f"?action=query&titles={urllib.parse.quote(wiki_page)}"
        f"&prop=images&format=json&imlimit=20"
    )
    data = json.loads(fetch_url(api))
    pages = data.get("query", {}).get("pages", {})
    candidates = []
    for page in pages.values():
        images = page.get("images", [])
        for img in images:
            title = img.get("title", "")
            tl = title.lower()
            # Prioritize logo/crest images
            if any(kw in tl for kw in ["logo", "crest", "badge", "wappen", "emblem", "shield"]):
                candidates.insert(0, title)
            elif title.endswith(".svg") or title.endswith(".png"):
                candidates.append(title)
    return candidates

def method3_wikimedia_file_url(file_title, thumb_px=200):
    """Get thumbnail URL for a File: title via Wikimedia API."""
    api = (
        "https://en.wikipedia.org/w/api.php"
        f"?action=query&titles={urllib.parse.quote(file_title)}"
        f"&prop=imageinfo&iiprop=url&iiurlwidth={thumb_px}&format=json"
    )
    data = json.loads(fetch_url(api))
    pages = data.get("query", {}).get("pages", {})
    for page in pages.values():
        info = page.get("imageinfo", [])
        if info:
            return info[0].get("thumburl") or info[0].get("url")
    return None

def download_logo(abbr, wiki_page):
    out_path = os.path.join(LOGO_DIR, f"{abbr}.png")
    if os.path.exists(out_path):
        print(f"  [CACHED] {abbr}")
        return out_path

    img_url = None

    # Method 1: piprop=original
    try:
        img_url = method1_original(wiki_page)
        if img_url:
            print(f"    M1 found URL for {abbr}")
    except Exception as e:
        print(f"    M1 failed for {abbr}: {e}")

    time.sleep(0.8)

    # Method 2: scan images list for logo
    if not img_url:
        try:
            candidates = method2_images_list(wiki_page)
            if candidates:
                print(f"    M2 candidates for {abbr}: {candidates[:3]}")
                img_url = method3_wikimedia_file_url(candidates[0], thumb_px=200)
                if img_url:
                    print(f"    M2+M3 found URL for {abbr}")
        except Exception as e:
            print(f"    M2 failed for {abbr}: {e}")

        time.sleep(0.8)

    if not img_url:
        print(f"  [FAIL-NO-URL] {abbr}")
        return None

    # Download the image
    try:
        # For SVG thumbnails from Wikimedia, we may need different headers
        img_data = fetch_url(img_url, extra_headers={"Accept": "image/*,*/*"})
        img = Image.open(io.BytesIO(img_data)).convert("RGBA")
        img.save(out_path)
        print(f"  [OK] {abbr}")
        return out_path
    except Exception as e:
        print(f"  [FAIL-DL] {abbr}: {e}")
        return None

failed = []
ok = []

for abbr, wiki_page in CLUBS_NEEDED:
    result = download_logo(abbr, wiki_page)
    if result:
        ok.append(abbr)
    else:
        failed.append(abbr)
    time.sleep(2.0 + random.random() * 1.5)

print(f"\nOK: {len(ok)}, Failed: {len(failed)}")
if failed:
    print(f"Failed: {failed}")
