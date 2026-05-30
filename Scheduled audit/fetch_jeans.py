"""
fetch_jeans.py
Fetch REV'IT! men's + women's jeans, dedup by base name, visit each product
page and check the Sustainability tab for the explicit <h2>Vegan</h2> marker.
"""
import requests, re, os, json, time, sys
from html.parser import HTMLParser

H = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'}

class Strip(HTMLParser):
    def __init__(self): super().__init__(); self.parts=[]
    def handle_data(self, d): self.parts.append(d)
    def text(self): return re.sub(r'\s+', ' ', ' '.join(self.parts)).strip()

def clean(html):
    s = Strip(); s.feed(html or ''); return s.text()

VEGAN_RE = re.compile(r'<h2>\s*Vegan\s*</h2>', re.I)

COLLECTIONS = {
    'men':   'https://revitsport.com/en-us/collections/men-motorcycle-jeans/products.json',
    'women': 'https://revitsport.com/en-us/collections/women-motorcycle-jeans/products.json',
}

def process(gender, url):
    r = requests.get(url, params={'limit': 250}, headers=H, timeout=30)
    try:
        prods = r.json()['products']
    except Exception:
        print(f'[{gender}] collection fetch failed ({r.status_code})'); return []
    print(f'[{gender}] raw products: {len(prods)}')
    seen, unique = set(), []
    for p in prods:
        base = re.sub(r'\s+', ' ', re.sub(r'\s*\|\s*.*$', '', p['title'])).strip()
        if base in seen: continue
        seen.add(base); unique.append((base, p))
    print(f'[{gender}] unique jeans: {len(unique)}')
    out = []
    for base, p in unique:
        handle = p.get('handle', '')
        purl = f'https://revitsport.com/en-us/products/{handle}'
        try:
            pr = requests.get(purl, headers=H, timeout=30)
            is_vegan = bool(VEGAN_RE.search(pr.text))
            any_hit = len(re.findall(r'vegan', pr.text, re.I))
        except Exception as e:
            print(f'  [ERR] {base}: {e}'); continue
        print(f'  [{gender}] [{"VEGAN" if is_vegan else "  -  "}] {base}  (raw vegan hits={any_hit})')
        if is_vegan:
            images = p.get('images') or []
            out.append({
                'gender': gender, 'name': base, 'handle': handle, 'url': purl,
                'tags': p.get('tags', []), 'body': clean(p.get('body_html', '')),
                'img': images[0].get('src', '') if images else '',
            })
        time.sleep(0.3)
    return out

allv = []
for g, u in COLLECTIONS.items():
    allv += process(g, u)

out = os.path.join(os.path.dirname(__file__), 'jeans.json')
with open(out, 'w') as f:
    json.dump(allv, f, indent=2, ensure_ascii=False)
print(f'\nVegan jeans total: {len(allv)} -> {out}')
