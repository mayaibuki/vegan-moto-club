"""
fix_product_photos.py
Replace single lifestyle/banner photos with the full clean REV'IT! studio gallery.

For every REV'IT! product in Notion with <=1 photo, fetch the per-product Shopify
endpoint (.../products/{handle}.json) whose product.images array is the clean
studio gallery, HEAD-check each image, and overwrite the Photos field with the
full set. Non-REV'IT single-photo products are only listed for manual review.

Dry-run unless APPLY=1.
"""
import os, re, json, time, urllib.request
from notion_client import Client

H = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'}

n = Client(auth=os.environ["NOTION_API_KEY"])
DB = os.environ["NOTION_PRODUCTS_DB_ID"]
DS = n.databases.retrieve(DB)["data_sources"][0]["id"]
APPLY = os.environ.get("APPLY") == "1"

BAD_IMG = re.compile(r'(display|lifestyle|banner|\d{3,4}x\d{3,4})', re.I)

def handle_from_url(url):
    m = re.search(r'/products/([^/?#]+)', url or '')
    return m.group(1) if m else ""

def fetch_gallery(handle):
    u = f'https://revitsport.com/en-us/products/{handle}.json'
    d = json.load(urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=30))
    return [im['src'] for im in d['product'].get('images', [])]

def head_ok(url):
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=H, method='HEAD'), timeout=20)
        return r.status == 200
    except Exception:
        return False

# paginate full DB
rows, cursor = [], None
while True:
    kw = {"data_source_id": DS, "page_size": 100}
    if cursor: kw["start_cursor"] = cursor
    r = n.data_sources.query(**kw)
    rows += r["results"]
    if not r.get("has_more"): break
    cursor = r["next_cursor"]

print(f"Total rows: {len(rows)}")

updated = skipped = 0
non_revit = []

for row in rows:
    p = row["properties"]
    t = p["Name of product"]["title"]
    name = t[0]["plain_text"] if t else ""
    brand = (p.get("Brand", {}).get("select") or {}).get("name", "")
    url = p.get("URL", {}).get("url") or ""
    photos = p.get("Photos", {}).get("files", [])
    is_revit = brand == "REV'IT!" or "revitsport" in url
    if len(photos) > 1:
        continue

    if not is_revit:
        non_revit.append((name, len(photos), url))
        continue

    handle = handle_from_url(url)
    if not handle:
        print(f"  [SKIP] {name}: no handle in URL"); skipped += 1; continue
    try:
        imgs = fetch_gallery(handle)
    except Exception as e:
        print(f"  [SKIP] {name} ({handle}): fetch failed {e}"); skipped += 1; continue

    # filter out lifestyle/banner shots
    clean = [s for s in imgs if not BAD_IMG.search(s.split('/files/')[-1].split('?')[0])]
    # HEAD-check
    good = [s for s in clean if head_ok(s)]
    if len(good) < 2:
        print(f"  [SKIP] {name} ({handle}): only {len(good)} usable studio image(s), leaving as-is")
        skipped += 1
        time.sleep(0.3)
        continue

    print(f"  [{'UPDATE' if APPLY else 'WOULD'}] {name:24} ({handle})  {len(photos)} -> {len(good)} photos")
    if APPLY:
        props = {"Photos": {"files": [
            {"type": "external", "name": name, "external": {"url": s}} for s in good]}}
        n.pages.update(page_id=row["id"], properties=props)
        time.sleep(0.4)
    updated += 1
    time.sleep(0.3)

print(f"\n{'APPLIED' if APPLY else 'DRY-RUN'}: {updated} REV'IT updated, {skipped} skipped")
print(f"\n--- NON-REV'IT single-photo (manual review): {len(non_revit)} ---")
for nm, cnt, url in non_revit:
    print(f"  [{cnt}] {nm}  {url}")
