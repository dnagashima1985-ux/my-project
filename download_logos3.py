#!/usr/bin/env python3
"""
Targeted download for remaining 5 clubs using specific Wikimedia file names.
"""
import os, json, time, random, urllib.request, urllib.parse, urllib.error, io
from PIL import Image

LOGO_DIR = "/home/user/my-project/logos"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) ScoutMapBot/1.0",
    "Accept": "image/*,*/*",
}

def fetch_url(url, timeout=20):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()

# Manual Wikimedia Commons file references for difficult clubs
MANUAL = {
    "SRFC": "https://upload.wikimedia.org/wikipedia/en/thumb/d/d7/Stade_Rennais_FC_%28logo%29.svg/200px-Stade_Rennais_FC_%28logo%29.svg.png",
    "HVR":  "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f5/Hellas_Verona_FC_Logo_2020.svg/200px-Hellas_Verona_FC_Logo_2020.svg.png",
    "INTER":"https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/FC_Internazionale_Milano_2021.svg/200px-FC_Internazionale_Milano_2021.svg.png",
    "ACM":  "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d0/Logo_of_AC_Milan.svg/200px-Logo_of_AC_Milan.svg.png",
    "RSPG": "https://upload.wikimedia.org/wikipedia/en/thumb/1/1b/Sporting_de_Gij%C3%B3n_logo.svg/200px-Sporting_de_Gij%C3%B3n_logo.svg.png",
}

# Also try via imageinfo API
def get_via_imageinfo(file_title, thumb_px=200):
    api = (
        "https://commons.wikimedia.org/w/api.php"
        f"?action=query&titles={urllib.parse.quote(file_title)}"
        f"&prop=imageinfo&iiprop=url&iiurlwidth={thumb_px}&format=json"
    )
    req = urllib.request.Request(api, headers={"User-Agent": HEADERS["User-Agent"], "Accept": "application/json"})
    data = json.loads(urllib.request.urlopen(req, timeout=15).read())
    pages = data.get("query", {}).get("pages", {})
    for page in pages.values():
        info = page.get("imageinfo", [])
        if info:
            return info[0].get("thumburl") or info[0].get("url")
    return None

# Commons file names for fallback
COMMONS_FILES = {
    "SRFC": "File:Stade Rennais FC (logo).svg",
    "HVR":  "File:Hellas Verona FC Logo 2020.svg",
    "INTER":"File:FC Internazionale Milano 2021.svg",
    "ACM":  "File:Logo of AC Milan.svg",
    "RSPG": "File:Sporting de Gijón logo.svg",
}

for abbr in ["SRFC", "HVR", "INTER", "ACM", "RSPG"]:
    out = os.path.join(LOGO_DIR, f"{abbr}.png")
    if os.path.exists(out):
        print(f"[ALREADY EXISTS] {abbr}")
        continue

    # Try manual URL first
    url = MANUAL.get(abbr)
    success = False
    if url:
        try:
            data = fetch_url(url)
            img = Image.open(io.BytesIO(data)).convert("RGBA")
            img.save(out)
            print(f"[OK-manual] {abbr}")
            success = True
        except Exception as e:
            print(f"  manual fail {abbr}: {e}")

    if not success:
        # Try commons imageinfo
        cf = COMMONS_FILES.get(abbr)
        if cf:
            try:
                url2 = get_via_imageinfo(cf, thumb_px=200)
                if url2:
                    data = fetch_url(url2)
                    img = Image.open(io.BytesIO(data)).convert("RGBA")
                    img.save(out)
                    print(f"[OK-commons] {abbr}")
                    success = True
            except Exception as e:
                print(f"  commons fail {abbr}: {e}")

    if not success:
        print(f"[FAIL] {abbr}")

    time.sleep(1.5 + random.random())

print("\nDone.")
# List what we have
logos = os.listdir(LOGO_DIR)
print(f"Total logos in dir: {len(logos)}")
