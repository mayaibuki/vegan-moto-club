"""
fetch_women_revit.py
Fetch REV'IT! women's jacket collection data, filter leather,
skip men's-only items, output JSON with name/url/tags/body/img.
"""
import requests, re, os, json
from html.parser import HTMLParser

H = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'}

class Strip(HTMLParser):
    def __init__(self): super().__init__(); self.parts=[]
    def handle_data(self, d): self.parts.append(d)
    def text(self): return re.sub(r'\s+', ' ', ' '.join(self.parts)).strip()

def clean(html):
    s = Strip(); s.feed(html or ''); return s.text()

r = requests.get(
    'https://revitsport.com/en-us/collections/women-motorcycle-jackets/products.json',
    params={'limit': 250}, headers=H, timeout=30
)
prods = r.json()['products']

# Men's-only products appearing in women's collection — already covered by men's entries
SKIP = {'jacket component 3 h2o', 'jacket territory 2', 'jersey sierra 2', 'smock blackwater 3 h2o'}

seen = {}
results = []
for p in prods:
    base = re.sub(r'\s*\|\s*.*$', '', p['title']).strip()
    base = re.sub(r'\s+', ' ', base).strip()
    if base in seen:
        continue
    if base.lower() in SKIP:
        seen[base] = 'skip'
        continue
    tags = [t.lower() for t in (p.get('tags') or [])]
    if 'leather' in tags:
        seen[base] = 'leather'
        continue
    body = clean(p.get('body_html', ''))
    if any(x in body.lower() for x in ['full grain leather', 'full-grain leather', 'genuine leather', 'cowhide']):
        seen[base] = 'leather'
        continue
    if "men's" in tags and 'women' not in ' '.join(tags).lower() and 'ladies' not in base.lower():
        seen[base] = 'mens-only'
        continue

    handle = p.get('handle', '')
    url = f'https://revitsport.com/en-us/products/{handle}'
    images = p.get('images') or []
    hero_img = images[0].get('src', '') if images else ''

    results.append({
        'name': base,
        'handle': handle,
        'url': url,
        'tags': p.get('tags', []),
        'body': body,
        'img': hero_img
    })
    seen[base] = 'ok'

out = os.path.join(os.path.dirname(__file__), 'women_revit.json')
with open(out, 'w') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f'Exported {len(results)} women\'s jacket candidates to {out}')
for x in results:
    print(f"  {x['name']}")
    print(f"    url: {x['url']}")
    print(f"    tags: {', '.join(x['tags'])[:100]}")
