"""
revit_maker_vegan.py
Upgrade Vegan Verified to "Confirmed Vegan by maker" for REV'IT! products
whose official product page lists "Vegan" in its Sustainability tab.

REV'IT! exposes a "Sustainability" collapsible tab on each product page. When
the garment is animal-free the maker lists an <h2>Vegan</h2> entry inside that
panel. That is a first-party claim, so it warrants the stronger label than our
own keyword screen ("Verified Vegan by us").

We bound the check to the Sustainability <details> panel and require the exact
<h2>Vegan</h2> heading, so stray "vegan" mentions elsewhere on the page (reviews,
cross-sells) don't trigger a false upgrade.

Matches by NAME across the whole DB (Brand/Category were unreliable after the
audit corrupted some rows). Only UPGRADES to maker-confirmed; never downgrades.

Run: set -a && source ./.env.local && set +a && python3 "Scheduled audit/revit_maker_vegan.py"
"""

import os, re, requests
from notion_client import Client

H = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
n = Client(auth=os.environ["NOTION_API_KEY"])
db = os.environ["NOTION_PRODUCTS_DB_ID"]
DS = n.databases.retrieve(db)["data_sources"][0]["id"]
COLLECTION = "https://revitsport.com/en-us/collections/men-motorcycle-jackets"
TARGET_LABEL = "Confirmed Vegan by maker"

def norm(s):
    return re.sub(r"[^a-z0-9 ]", "", s.lower()).strip()

PREFIX = re.compile(r"^(jacket|smock|jersey|overshirt|hoodie|sweater|one piece)\s+")
def core(s):
    return PREFIX.sub("", norm(s)).strip()

# Capture the Sustainability disclosure panel: from its <summary> to </details>.
SUSTAIN_RE = re.compile(
    r"<summary[^>]*>\s*Sustainability\s*</summary>(.*?)</details>",
    re.IGNORECASE | re.DOTALL,
)
VEGAN_H2_RE = re.compile(r"<h2[^>]*>\s*vegan\s*</h2>", re.IGNORECASE)

def maker_says_vegan(handle):
    """True if the product page's Sustainability tab lists an <h2>Vegan</h2>."""
    try:
        r = requests.get(f"https://revitsport.com/en-us/products/{handle}",
                         headers=H, timeout=20)
        if r.status_code != 200:
            return None
        m = SUSTAIN_RE.search(r.text)
        if not m:
            return False
        return bool(VEGAN_H2_RE.search(m.group(1)))
    except Exception:
        return None

# ── 1. Fetch collection, check each model's Sustainability tab ──────────────
print("Fetching REV'IT! collection…")
prods = requests.get(f"{COLLECTION}/products.json", params={"limit": 250},
                     headers=H, timeout=20).json()["products"]

# one handle per base model (strip "| Color")
model_handle = {}
for p in prods:
    base = re.sub(r"\s*\|\s*.*$", "", p["title"]).strip()
    model_handle.setdefault(norm(base), p["handle"])
print(f"  {len(model_handle)} unique models — checking Sustainability tabs…")

vegan_full = {}   # normalized full name -> True (maker-confirmed vegan)
for name_norm, handle in model_handle.items():
    res = maker_says_vegan(handle)
    if res:
        vegan_full[name_norm] = True
print(f"  {len(vegan_full)} models list 'Vegan' in their Sustainability tab")

# core-name index (skip ambiguous collisions)
vegan_core = {}
for k in vegan_full:
    c = PREFIX.sub("", k).strip()
    vegan_core[c] = None if c in vegan_core else True

# ── 2. Scan DB, upgrade matched products ────────────────────────────────────
print("\nScanning products DB…")
pages, has_more, cursor = [], True, None
while has_more:
    kw = {"data_source_id": DS, "page_size": 100}
    if cursor:
        kw["start_cursor"] = cursor
    resp = n.data_sources.query(**kw)
    pages += resp["results"]
    has_more = resp["has_more"]
    cursor = resp.get("next_cursor")
print(f"  {len(pages)} products scanned")

updated = 0
for pg in pages:
    title = pg["properties"].get("Name of product", {}).get("title", [])
    if not title:
        continue
    name = title[0]["plain_text"]
    if not (vegan_full.get(norm(name)) or vegan_core.get(core(name))):
        continue
    cur = pg["properties"].get("Vegan Verified", {}).get("select") or {}
    if cur.get("name") == TARGET_LABEL:
        continue  # already correct
    n.pages.update(page_id=pg["id"],
                   properties={"Vegan Verified": {"select": {"name": TARGET_LABEL}}})
    updated += 1
    print(f"  ✓ {name:38} {cur.get('name','—')} → {TARGET_LABEL}")

print(f"\n{'='*60}\nDONE — {updated} upgraded to '{TARGET_LABEL}'")
