#!/usr/bin/env python3
"""
Download club logos from Wikimedia Commons via Wikipedia API.
Uses session persistence, longer delays, and retry logic.
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

CLUBS = [
    ("STVV",  "Sint-Truidense_VV"),
    ("HSV",   "Hamburger_SV"),
    ("FCSP",  "FC_St._Pauli"),
    ("D98",   "SV_Darmstadt_98"),
    ("B04",   "Bayer_04_Leverkusen"),
    ("KÖN",   "1._FC_Köln"),
    ("F95",   "Fortuna_Düsseldorf"),
    ("BMG",   "Borussia_Mönchengladbach"),
    ("S04",   "FC_Schalke_04"),
    ("BVB",   "Borussia_Dortmund"),
    ("WOB",   "VfL_Wolfsburg"),
    ("SVW",   "Werder_Bremen"),
    ("KSC",   "Karlsruher_SC"),
    ("FCK",   "1._FC_Kaiserslautern"),
    ("FCN",   "1._FC_Nürnberg"),
    ("RBL",   "RB_Leipzig"),
    ("SGE",   "Eintracht_Frankfurt"),
    ("SCF",   "SC_Freiburg"),
    ("TSG",   "TSG_1899_Hoffenheim"),
    ("FCA",   "FC_Augsburg"),
    ("FCU",   "1._FC_Union_Berlin"),
    ("BSC",   "Hertha_BSC"),
    ("VFB",   "VfB_Stuttgart"),
    ("AJX",   "AFC_Ajax"),
    ("FCU2",  "FC_Utrecht"),
    ("AZ",    "AZ_(football_club)"),
    ("FEY",   "Feyenoord"),
    ("PSV",   "PSV_Eindhoven"),
    ("FCT",   "FC_Twente"),
    ("SFC",   "Southampton_F.C."),
    ("COV",   "Coventry_City_F.C."),
    ("OXF",   "Oxford_United_F.C."),
    ("QPR",   "Queens_Park_Rangers_F.C."),
    ("MIL",   "Millwall_F.C."),
    ("NUFC",  "Newcastle_United_F.C."),
    ("MUFC",  "Manchester_United_F.C."),
    ("WHU",   "West_Ham_United_F.C."),
    ("THFC",  "Tottenham_Hotspur_F.C."),
    ("WWFC",  "Wolverhampton_Wanderers_F.C."),
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
    ("SDR",   "Stade_de_Reims"),
    ("TFC",   "Toulouse_FC"),
    ("COM",   "Como_1907"),
    ("TOR",   "Torino_F.C."),
    ("SASU",  "U.S._Sassuolo_Calcio"),
    ("BOL",   "Bologna_F.C._1909"),
    ("HVR",   "Hellas_Verona_F.C."),
    ("FIOR",  "ACF_Fiorentina"),
    ("ATA",   "Atalanta_B.C."),
    ("INTER", "FC_Internazionale_Milano"),
    ("ACM",   "A.C._Milan"),
    ("CREM",  "U.S._Cremonese"),
    ("PAR",   "Parma_Calcio_1913"),
    ("GEN",   "Genoa_C.F.C."),
    ("MON",   "A.C._Monza"),
    ("CAG",   "Cagliari_Calcio"),
    ("LEV",   "Levante_UD"),
    ("BETIS", "Real_Betis"),
    ("RSO",   "Real_Sociedad"),
    ("OSA",   "CA_Osasuna"),
    ("RSPG",  "Real_Sporting_de_Gijón"),
    ("RAPID", "SK_Rapid_Wien"),
    ("SLA",   "SK_Slavia_Prague"),
    ("FKP",   "FC_Viktoria_Plzeň"),
    ("CZV",   "FK_Crvena_zvezda"),
    ("FCK2",  "FC_Copenhagen"),
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; ScoutMapBot/1.0; +https://example.com/bot) Python-urllib/3.x",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
}

def fetch_url(url, timeout=20, retries=3):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read()
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = 5 + attempt * 5 + random.random() * 3
                print(f"    Rate limited, waiting {wait:.1f}s...")
                time.sleep(wait)
            elif e.code in (403, 404):
                raise
            else:
                wait = 2 + attempt * 2
                time.sleep(wait)
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2)
            else:
                raise
    raise Exception(f"Failed after {retries} attempts")

def get_wiki_logo_url(wiki_page, thumb_size=200):
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
        print(f"  [OK] {abbr}")
        return out_path
    except Exception as e:
        print(f"  [FAIL] {abbr}: {e}")
        return None

failed = []
ok = []

for abbr, wiki_page in CLUBS:
    result = download_logo(abbr, wiki_page)
    if result:
        ok.append(abbr)
    else:
        failed.append(abbr)
    # polite delay between requests
    time.sleep(1.5 + random.random())

print(f"\nOK: {len(ok)}, Failed: {len(failed)}")
if failed:
    print(f"Failed: {failed}")
