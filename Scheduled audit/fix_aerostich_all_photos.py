"""
fix_aerostich_all_photos.py
Re-pull clean studio photos for ALL Aerostich rows in Notion.

The prior filters (^\\d{3}_ allow-list) both dropped real studio shots
(file_6_2.jpg, 120greyblack2.jpg) and let trailing/lifestyle shots through.
The Shopify product.images array is already the merchant-curated studio gallery
in order, so we now KEEP images in array order and only SUBTRACT non-product
assets: .png/.gif/.webp diagrams, camera-date-named files, and person/logo shots.

Selects every row with Brand = AeroStitch, derives the handle from its URL,
HEAD-checks each kept image, caps at 8, and overwrites Photos.

Dry-run unless APPLY=1.
"""
import os, re, json, time, urllib.request
from notion_client import Client

H = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'}
n = Client(auth=os.environ["NOTION_API_KEY"])
DB = os.environ["NOTION_PRODUCTS_DB_ID"]
DS = n.databases.retrieve(DB)["data_sources"][0]["id"]
APPLY = os.environ.get("APPLY") == "1"

# keep .jpg studio shots; drop diagrams + lifestyle/logo + date-named
DROP_EXT = re.compile(r'\.(png|gif|webp)$', re.I)
DATE = re.compile(r'^\d{4}[-_]\d{2}[-_]\d{2}')
BAD = re.compile(r'(aerostitch|copy|feature|jscott|jb_cadillac|sharonhiers|ayodeji|axel|ericdue|^dsc\d)', re.I)


def gallery(handle, cap=8):
    u = f'https://www.aerostich.com/products/{handle}.json'
    d = json.load(urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=30))['product']
    out = []
    for im in d['images']:
        fn = im['src'].split('/files/')[-1].split('?')[0]
        if DROP_EXT.search(fn) or DATE.search(fn) or BAD.search(fn):
            continue
        s = im['src']
        try:
            if urllib.request.urlopen(urllib.request.Request(s, headers=H, method='HEAD'), timeout=20).status == 200:
                out.append(s)
        except Exception:
            pass
        if len(out) >= cap:
            break
    return out


def handle_from_url(url):
    m = re.search(r'/products/([^/?#]+)', url or '')
    return m.group(1) if m else ""


# paginate all rows, filter Brand == AeroStitch
rows, cursor = [], None
while True:
    kw = {"data_source_id": DS, "page_size": 100}
    if cursor:
        kw["start_cursor"] = cursor
    r = n.data_sources.query(**kw)
    rows += r["results"]
    if not r.get("has_more"):
        break
    cursor = r["next_cursor"]

aero = [row for row in rows
        if (row["properties"].get("Brand", {}).get("select") or {}).get("name") == "Aerostitch"]
print(f"Aerostich rows: {len(aero)}")

updated = skipped = 0
for row in aero:
    p = row["properties"]
    t = p["Name of product"]["title"]
    name = t[0]["plain_text"] if t else "(untitled)"
    url = p.get("URL", {}).get("url") or ""
    handle = handle_from_url(url)
    if not handle:
        print(f"  [SKIP] {name}: no handle in URL ({url})")
        skipped += 1
        continue
    try:
        imgs = gallery(handle)
    except Exception as e:
        print(f"  [SKIP] {name} ({handle}): fetch failed {e}")
        skipped += 1
        continue
    if not imgs:
        print(f"  [SKIP] {name} ({handle}): 0 usable studio images")
        skipped += 1
        continue
    print(f"  [{'UPDATE' if APPLY else 'WOULD'}] {name:42} ({handle})  -> {len(imgs)} photos")
    for s in imgs:
        print("        ", s.split('/files/')[-1].split('?')[0])
    if APPLY:
        n.pages.update(page_id=row["id"], properties={
            "Photos": {"files": [{"type": "external", "name": name, "external": {"url": s}} for s in imgs]}})
        time.sleep(0.4)
    updated += 1

print(f"\n{'APPLIED' if APPLY else 'DRY-RUN'}: {updated} updated, {skipped} skipped")
