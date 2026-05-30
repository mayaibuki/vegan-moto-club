"""
fetch_men_boots.py
Fetch REV'IT! men's boots, dedup by base name, then visit each product page
and check the Sustainability tab for the explicit <h2>Vegan</h2> marker.
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
    'https://revitsport.com/en-us/collections/men-motorcycle-boots/products.json',
    params={'limit': 250}, headers=H, timeout=30
)
prods = r.json()['products']
print(f'Raw products: {len(prods)}')

seen, unique = set(), []
for p in prods:
    base = re.sub(r'\s+', ' ', re.sub(r'\s*\|\s*.*$', '', p['title'])).strip()
    if base in seen: continue
    seen.add(base); unique.append((base, p))
print(f'Unique boots: {len(unique)}')

vegan = []
for base, p in unique:
    handle = p.get('handle', '')
    url = f'https://revitsport.com/en-us/products/{handle}'
    try:
        pr = requests.get(url, headers=H, timeout=30)
        is_vegan = bool(VEGAN_RE.search(pr.text))
        any_hit = len(re.findall(r'vegan', pr.text, re.I))
    except Exception as e:
        print(f'  [ERR] {base}: {e}'); continue
    print(f'  [{"VEGAN" if is_vegan else "  -  "}] {base}  (raw vegan hits={any_hit})')
    if is_vegan:
        images = p.get('images') or []
        vegan.append({
            'name': base, 'handle': handle, 'url': url,
            'tags': p.get('tags', []), 'body': clean(p.get('body_html', '')),
            'img': images[0].get('src', '') if images else '',
        })
    time.sleep(0.3)

out = os.path.join(os.path.dirname(__file__), 'men_boots.json')
with open(out, 'w') as f:
    json.dump(vegan, f, indent=2, ensure_ascii=False)
print(f'\nVegan men boots: {len(vegan)} -> {out}')
