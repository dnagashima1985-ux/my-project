#!/usr/bin/env python3
"""Download final 5 logos using Wikipedia API with correct method."""
import requests, io, os, time, json
from PIL import Image

LOGO_DIR = '/home/user/my-project/logos'

s = requests.Session()
s.headers.update({
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) Gecko/20100101 Firefox/120.0',
    'Accept-Language': 'en-US,en;q=0.9',
})

# Use the Wikipedia API with prop=images first, then imageinfo
def get_logo_via_images_api(wiki_page, keyword_hints=('logo', 'crest', 'badge', 'emblem', 'wappen')):
    """Get page images list, find logo, get its URL."""
    api_url = 'https://en.wikipedia.org/w/api.php'

    # Step 1: get images on page
    r = s.get(api_url, params={
        'action': 'query',
        'titles': wiki_page,
        'prop': 'images',
        'imlimit': 30,
        'format': 'json',
    }, timeout=15)
    data = r.json()
    pages = data.get('query', {}).get('pages', {})
    images = []
    for p in pages.values():
        images = [i['title'] for i in p.get('images', [])]

    if not images:
        return None, None

    # Prioritize logo images
    scored = []
    for t in images:
        tl = t.lower()
        score = 0
        for kw in keyword_hints:
            if kw in tl: score += 3
        if t.endswith('.svg'): score += 1
        if t.endswith('.png'): score += 0.5
        scored.append((score, t))
    scored.sort(reverse=True)

    best = [t for _, t in scored if scored[0][0] > 0]
    if not best:
        best = [scored[0][1]] if scored else []

    # Step 2: get URL for best candidate
    for candidate in best[:3]:
        time.sleep(1)
        r2 = s.get(api_url, params={
            'action': 'query',
            'titles': candidate,
            'prop': 'imageinfo',
            'iiprop': 'url',
            'iiurlwidth': 200,
            'format': 'json',
        }, timeout=15)
        data2 = r2.json()
        pages2 = data2.get('query', {}).get('pages', {})
        for p2 in pages2.values():
            info = p2.get('imageinfo', [])
            if info:
                url = info[0].get('thumburl') or info[0].get('url')
                if url:
                    return candidate, url
    return None, None

clubs = [
    ('SRFC', 'Stade_Rennais_F.C.'),
    ('HVR',  'Hellas_Verona_F.C.'),
    ('INTER','FC_Internazionale_Milano'),
    ('ACM',  'A.C._Milan'),
    ('RSPG', 'Real_Sporting_de_Gijón'),
]

time.sleep(5)  # let rate limit cool

for abbr, wiki_page in clubs:
    out = f'{LOGO_DIR}/{abbr}.png'
    if os.path.exists(out):
        print(f'[SKIP] {abbr}')
        continue

    try:
        file_title, url = get_logo_via_images_api(wiki_page)
        if url:
            r = s.get(url, timeout=20, headers={'Accept': 'image/*,*/*'})
            r.raise_for_status()
            img = Image.open(io.BytesIO(r.content)).convert('RGBA')
            img.save(out)
            print(f'[OK] {abbr} via {file_title}')
        else:
            print(f'[NO-URL] {abbr} (file: {file_title})')
    except Exception as e:
        print(f'[FAIL] {abbr}: {e}')

    time.sleep(4)

print(f'\nTotal logos: {len(os.listdir(LOGO_DIR))}')
