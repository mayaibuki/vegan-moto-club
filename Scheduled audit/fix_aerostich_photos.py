"""
fix_aerostich_photos.py
The two Aerostich R-3 one-piece suits in Notion have 0 photos / a logo image.
Aerostich migrated to Shopify, so pull clean studio product shots from the
per-product .json, filter out feature-diagram PNGs and comparison/detail charts,
cap at 8, HEAD-check, and update Photos + the (now-dead) URL.
Dry-run unless APPLY=1.
"""
import os, re, json, time, urllib.request
from notion_client import Client

H = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'}

n = Client(auth=os.environ["NOTION_API_KEY"])
DB = os.environ["NOTION_PRODUCTS_DB_ID"]
DS = n.databases.retrieve(DB)["data_sources"][0]["id"]
APPLY = os.environ.get("APPLY") == "1"

# Notion name -> Shopify product handle/URL
TARGETS = {
    "R-3 One piece suite Men":   "mens-r-3-one-piece-suit",
    "R-3 One piece suite Women": "womens-r-3-one-piece-suit",
}

# keep core studio gallery shots of the suit; drop logos/diagrams/charts/variants
KEEP = re.compile(r'520_1[a-z]_', re.I)

def gallery(handle):
    u = f'https://www.aerostich.com/products/{handle}.json'
    d = json.load(urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=30))['product']
    imgs = [im['src'] for im in d['images']]
    keep = [s for s in imgs if KEEP.search(s.split('/files/')[-1])]
    return keep[:8], f'https://www.aerostich.com/products/{handle}'

def head_ok(url):
    try:
        return urllib.request.urlopen(urllib.request.Request(url, headers=H, method='HEAD'), timeout=20).status == 200
    except Exception:
        return False

def find_row(title):
    r = n.data_sources.query(data_source_id=DS, filter={
        "property": "Name of product", "title": {"equals": title}})
    return r["results"][0] if r["results"] else None

for name, handle in TARGETS.items():
    imgs, url = gallery(handle)
    good = [s for s in imgs if head_ok(s)]
    row = find_row(name)
    if not row:
        print(f"  [SKIP] '{name}' not found in Notion"); continue
    print(f"  [{'UPDATE' if APPLY else 'WOULD'}] {name}: -> {len(good)} photos, url={url}")
    for s in good: print("       ", s.split('/files/')[-1].split('?')[0])
    if APPLY and good:
        props = {
            "URL": {"url": url},
            "Photos": {"files": [{"type": "external", "name": name, "external": {"url": s}} for s in good]},
        }
        n.pages.update(page_id=row["id"], properties=props)
        time.sleep(0.4)

print(f"\n{'APPLIED' if APPLY else 'DRY-RUN'}")
