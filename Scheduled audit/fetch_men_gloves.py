"""
fetch_men_gloves.py
Fetch REV'IT! men's gloves, dedup by base name, then visit each product
page and check the Sustainability tab for the explicit <h2>Vegan</h2> marker.
Output vegan gloves with name/url/tags/body/img to men_gloves.json.
"""
import requests, re, os, json, time
from html.parser import HTMLParser

H = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'}

class Strip(HTMLParser):
    def __init__(self): super().__init__(); self.parts=[]
    def handle_data(self, d): self.parts.append(d)
    def text(self): return re.sub(r'\s+', ' ', ' '.join(self.parts)).strip()

def clean(html):
    s = Strip(); s.feed(html or ''); return s.text()

VEGAN_RE = re.compile(r'<h2>\s*Vegan\s*</h2>', re.I)

r = requests.get(
    'https://revitsport.com/en-us/collections/men-motorcycle-gloves/products.json',
    params={'limit': 250}, headers=H, timeout=30
)
prods = r.json()['products']
print(f'Raw products: {len(prods)}')

seen = {}
unique = []
for p in prods:
    base = re.sub(r'\s*\|\s*.*$', '', p['title']).strip()
    base = re.sub(r'\s+', ' ', base).strip()
    if base in seen:
        continue
    seen[base] = True
    unique.append((base, p))
print(f'Unique gloves: {len(unique)}')

vegan = []
for i, (base, p) in enumerate(unique):
    handle = p.get('handle', '')
    url = f'https://revitsport.com/en-us/products/{handle}'
    try:
        pr = requests.get(url, headers=H, timeout=30)
        is_vegan = bool(VEGAN_RE.search(pr.text))
    except Exception as e:
        print(f'  [ERR] {base}: {e}')
        is_vegan = False
    flag = 'VEGAN' if is_vegan else '  -  '
    print(f'  [{flag}] {base}')
    if is_vegan:
        images = p.get('images') or []
        hero_img = images[0].get('src', '') if images else ''
        vegan.append({
            'name': base,
            'handle': handle,
            'url': url,
            'tags': p.get('tags', []),
            'body': clean(p.get('body_html', '')),
            'img': hero_img,
        })
    time.sleep(0.3)

out = os.path.join(os.path.dirname(__file__), 'men_gloves.json')
with open(out, 'w') as f:
    json.dump(vegan, f, indent=2, ensure_ascii=False)
print(f'\nVegan gloves: {len(vegan)} -> {out}')
