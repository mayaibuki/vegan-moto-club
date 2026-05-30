"""
fix_aerostich_dedup.py
Resolve Aerostich duplicates + fix outdated listings.

6 rows -> 4 distinct products:
  - Archive 2 "User Suggestion" rows that duplicate the proper R-3 Men/Women rows.
  - Fix the 2 proper R-3 rows: name typo (suite->suit), price (->1967),
    waterproof (Gore-tex -> plain Waterproof; the R-3 is NOT Gore-Tex), add Commute/Street.
  - Build out the 2 "User Suggestion" R-3 Light Tactical rows into real listings
    (name, price 1787, clean studio photos, correct materials/description).

Dry-run unless APPLY=1.
"""
import os, re, json, time, urllib.request
from notion_client import Client

H = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'}
n = Client(auth=os.environ["NOTION_API_KEY"])
APPLY = os.environ.get("APPLY") == "1"

# clean studio shots: 520_1x / 239_1x / 239_2x (one letter then underscore), skip lifestyle/diagrams
KEEP = re.compile(r'^\d{3}_[12][a-z]_', re.I)
WP = "Waterproof"
CORDURA = "Cordura® (Synhtetic fabric)"
RIDING = ["Commute / Street", "Adventure / Touring"]
RACING = ["Racing Suits"]

ARCHIVE = {  # duplicate suggestion rows -> trash
    "SUG men R3 (dup)":   "36f439de-397b-81f5-9910-e521f7d09108",
    "SUG women R3 (dup)": "36f439de-397b-8136-815f-e91c2386e33c",
}

def gallery(handle, cap=8):
    u = f'https://www.aerostich.com/products/{handle}.json'
    d = json.load(urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=30))['product']
    keep = [im['src'] for im in d['images'] if KEEP.search(im['src'].split('/files/')[-1])]
    out = []
    for s in keep:
        try:
            if urllib.request.urlopen(urllib.request.Request(s, headers=H, method='HEAD'), timeout=20).status == 200:
                out.append(s)
        except Exception:
            pass
        if len(out) >= cap: break
    return out

def files(name, urls):
    return {"files": [{"type": "external", "name": name, "external": {"url": u}} for u in urls]}

R3_DESC_M = ("The R-3 (Roadcrafter 3) is Aerostich's third-generation one-piece suit, built to pull on over "
 "your street clothes in seconds through a full-length waterproof zipper. It's 100% waterproof yet unlined "
 "for airflow, made from mil-spec 500-denier Cordura with impact armor at the shoulders, elbows, hips and "
 "knees. The classic all-weather commuter's suit — made in the USA.")
R3_DESC_W = R3_DESC_M + " Cut for a women's fit."
LT_DESC_M = ("The R-3 Light Tactical is the ultralight take on Aerostich's one-piece Roadcrafter. It drops the "
 "double-layer abrasion panels at the shoulders, elbows and knees, so it wears noticeably cooler and packs "
 "lighter while keeping the same 100% waterproof, pull-on-over-your-clothes design and impact armor. A little "
 "less abrasion coverage in trade for hot-weather comfort — made in the USA.")
LT_DESC_W = LT_DESC_M + " Cut for a women's fit."

# rows to fully (re)write: id -> dict
def base_props(name, gender, price, prot, season, desc, url):
    return {
        "Name of product": {"title": [{"text": {"content": name}}]},
        "URL": {"url": url},
        "Gender": {"multi_select": [{"name": gender}]},
        "Category": {"multi_select": [{"name": c} for c in RACING]},
        "Level of Protection": {"select": {"name": prot}},
        "Level of Waterproof": {"select": {"name": WP}},
        "Riding style": {"multi_select": [{"name": r} for r in RIDING]},
        "Season": {"multi_select": [{"name": s} for s in season]},
        "Materials": {"multi_select": [{"name": CORDURA}]},
        "Price": {"number": price},
        "Description": {"rich_text": [{"text": {"content": desc}}]},
    }

ALLSEASON = ["☀️ Summer", "🌦 Mid season", "❄️ Winter"]
LIGHT_SEASON = ["☀️ Summer", "🌦 Mid season"]

# proper rows: only patch the fields that were wrong (keep their 8 photos)
PATCH = {
    "63720667-359e-45b9-94eb-12233a1c2de2": dict(  # proper men R3
        name="R-3 One Piece Suit", gender="Men", price=1967, prot="Highly protective",
        season=ALLSEASON, desc=R3_DESC_M, url="https://www.aerostich.com/products/mens-r-3-one-piece-suit"),
    "7b39b143-a1f0-4695-aecb-7dceaff2a423": dict(  # proper women R3
        name="R-3 One Piece Suit Women", gender="Women", price=1967, prot="Highly protective",
        season=ALLSEASON, desc=R3_DESC_W, url="https://www.aerostich.com/products/womens-r-3-one-piece-suit"),
}

# light tactical rows: full build incl. fresh photos
BUILD = {
    "36f439de-397b-8186-b5e9-f08a56b3bb5f": dict(  # men light tactical
        name="R-3 Light Tactical One Piece Suit", gender="Men", price=1787, prot="Moderately protective",
        season=LIGHT_SEASON, desc=LT_DESC_M, handle="mens-r-3-light-tactical-one-piece",
        url="https://www.aerostich.com/products/mens-r-3-light-tactical-one-piece"),
    "36f439de-397b-815a-9c2e-fbd3b3614fc1": dict(  # women light tactical
        name="R-3 Light Tactical One Piece Suit Women", gender="Women", price=1787, prot="Moderately protective",
        season=LIGHT_SEASON, desc=LT_DESC_W, handle="womens-r-3-light-tactical-one-piece",
        url="https://www.aerostich.com/products/womens-r-3-light-tactical-one-piece"),
}

# 1) archive duplicates
for lbl, rid in ARCHIVE.items():
    print(f"[ARCHIVE] {lbl}  {rid}")
    if APPLY:
        n.pages.update(page_id=rid, archived=True); time.sleep(0.4)

# 2) patch proper rows
for rid, d in PATCH.items():
    print(f"[PATCH]  {d['name']}  price->{d['price']}  wp->{WP}")
    if APPLY:
        n.pages.update(page_id=rid, properties=base_props(
            d['name'], d['gender'], d['price'], d['prot'], d['season'], d['desc'], d['url']))
        time.sleep(0.4)

# 3) build out light tactical rows
for rid, d in BUILD.items():
    imgs = gallery(d['handle'])
    print(f"[BUILD]  {d['name']}  price->{d['price']}  photos->{len(imgs)}")
    props = base_props(d['name'], d['gender'], d['price'], d['prot'], d['season'], d['desc'], d['url'])
    if imgs:
        props["Photos"] = files(d['name'], imgs)
    if APPLY:
        n.pages.update(page_id=rid, properties=props); time.sleep(0.4)

print(f"\n{'APPLIED' if APPLY else 'DRY-RUN'}: 2 archived, 2 patched, 2 built")
