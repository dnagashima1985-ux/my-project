#!/usr/bin/env python3
"""Try to download the final 5 logos with direct Wikimedia URLs."""
import requests, io, os, time
from PIL import Image

LOGO_DIR = '/home/user/my-project/logos'
s = requests.Session()
s.headers.update({
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0',
    'Accept': 'image/webp,image/png,image/*,*/*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Referer': 'https://en.wikipedia.org/',
})

DIRECT_URLS = {
    'SRFC':  'https://upload.wikimedia.org/wikipedia/en/thumb/d/d7/Stade_Rennais_FC_%28logo%29.svg/150px-Stade_Rennais_FC_%28logo%29.svg.png',
    'HVR':   'https://upload.wikimedia.org/wikipedia/commons/thumb/f/f5/Hellas_Verona_FC_Logo_2020.svg/150px-Hellas_Verona_FC_Logo_2020.svg.png',
    'INTER': 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/FC_Internazionale_Milano_2021.svg/150px-FC_Internazionale_Milano_2021.svg.png',
    'ACM':   'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d0/Logo_of_AC_Milan.svg/150px-Logo_of_AC_Milan.svg.png',
    'RSPG':  'https://upload.wikimedia.org/wikipedia/en/thumb/1/1b/Sporting_de_Gij%C3%B3n_logo.svg/150px-Sporting_de_Gij%C3%B3n_logo.svg.png',
}

# Wait first to clear rate limit
time.sleep(10)

for abbr, url in DIRECT_URLS.items():
    out = f'{LOGO_DIR}/{abbr}.png'
    if os.path.exists(out):
        print(f'[SKIP] {abbr}')
        continue
    try:
        r = s.get(url, timeout=20)
        r.raise_for_status()
        img = Image.open(io.BytesIO(r.content)).convert('RGBA')
        img.save(out)
        print(f'[OK] {abbr} ({img.size})')
    except Exception as e:
        print(f'[FAIL] {abbr}: {e}')
    time.sleep(3)

print('Done')
print(f'Total logos: {len(os.listdir(LOGO_DIR))}')
