"""
add_revit_jackets.py
Scrapes REV'IT! men's jackets collection, identifies vegan ones,
cross-references Notion to skip duplicates, and adds new vegan jackets.

Run: set -a && source ./.env.local && set +a && python3 "Scheduled audit/add_revit_jackets.py"
"""

import os, re, requests
from html.parser import HTMLParser
from notion_client import Client

# ── Setup ──────────────────────────────────────────────────────────────────
H = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
n = Client(auth=os.environ["NOTION_API_KEY"])
db = os.environ["NOTION_PRODUCTS_DB_ID"]
DS = n.databases.retrieve(db)["data_sources"][0]["id"]

COLLECTION_URL = "https://revitsport.com/en-us/collections/men-motorcycle-jackets"
BASE = "https://revitsport.com"

# ── Material signals → Notion schema option names ──────────────────────────
# Only map to options that EXIST in the schema (validated manually)
MATERIAL_MAP = {
    "gore-tex":   "Gore-tex (waterproof fabric)",
    "gore tex":   "Gore-tex (waterproof fabric)",
    "mesh":       "Mesh fabric",
    "cordura":    "Cordura®",
    "polyester":  "Polyester",
    "nylon":      "Nylon",
    "polyamide":  "Polyamide",
}

NON_VEGAN_KW = [
    "leather", "cowhide", "goatskin", "lambskin", "kangaroo", "suede",
    "nubuck", "down feather", "goose down", "duck down", " wool ", "sheepskin", "pigskin",
]

def norm(s):
    return re.sub(r"[^a-z0-9 ]", "", s.lower()).strip()

class HTMLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
    def handle_data(self, d):
        self.parts.append(d)
    def get_text(self):
        return " ".join(self.parts)

def strip_html(html):
    s = HTMLStripper()
    s.feed(html or "")
    return re.sub(r"\s+", " ", s.get_text()).strip()

def head_ok(u):
    try:
        r = requests.head(u, headers=H, timeout=12, allow_redirects=True)
        if r.status_code in (403, 405):
            r = requests.get(u, headers=H, timeout=15, stream=True)
        return r.status_code == 200
    except Exception:
        return False

# ── 1. Fetch Shopify collection JSON ───────────────────────────────────────
print("Fetching REV'IT! men's jackets collection…")
r = requests.get(f"{COLLECTION_URL}/products.json", params={"limit": 250}, headers=H, timeout=20)
all_prods = r.json()["products"]
print(f"  {len(all_prods)} variants fetched (including color variants)")

# Deduplicate by base model name (strip "| Color" suffix)
unique = {}
for p in all_prods:
    base = re.sub(r"\s*\|\s*.*$", "", p["title"]).strip()
    if base not in unique:
        unique[base] = p
print(f"  {len(unique)} unique models")

# ── 2. Filter to vegan ─────────────────────────────────────────────────────
vegan_prods = {}
for name, p in unique.items():
    combined = ((p.get("body_html") or "") + " ".join(p.get("tags") or [])).lower()
    if not any(kw in combined for kw in NON_VEGAN_KW):
        vegan_prods[name] = p
print(f"  {len(vegan_prods)} vegan models (no animal-material keywords found)")

# ── 3. Fetch existing REV'IT! products from Notion ─────────────────────────
print("\nQuerying Notion for existing REV'IT! products…")
existing, has_more, cursor = [], True, None
while has_more:
    kw = {"data_source_id": DS, "page_size": 100,
          "filter": {"property": "Brand", "select": {"equals": "REV'IT!"}}}
    if cursor:
        kw["start_cursor"] = cursor
    resp = n.data_sources.query(**kw)
    existing += resp["results"]
    has_more = resp["has_more"]
    cursor = resp.get("next_cursor")

existing_names = set()
for pg in existing:
    title = pg["properties"].get("Name of product", {}).get("title", [])
    if title:
        existing_names.add(norm(title[0]["plain_text"]))
print(f"  {len(existing_names)} REV'IT! products already in Notion")

# ── 4. Determine which are new ────────────────────────────────────────────
new_products = []
for name, p in vegan_prods.items():
    n_name = norm(name)
    if any(n_name in en or en in n_name for en in existing_names):
        print(f"  SKIP (exists): {name}")
    else:
        new_products.append((name, p))
print(f"\n  → {len(new_products)} new vegan jackets to add\n")

# ── 5. Validate schema options ────────────────────────────────────────────
schema = n.data_sources.retrieve(data_source_id=DS)["properties"]
valid_materials = {o["name"] for o in schema["Materials"]["multi_select"]["options"]}
valid_vegan = {o["name"] for o in schema["Vegan Verified"]["select"]["options"]}
valid_cats = {o["name"] for o in schema["Category"]["multi_select"]["options"]}
valid_genders = {o["name"] for o in schema["Gender"]["multi_select"]["options"]}

assert "Verified Vegan by us" in valid_vegan
assert "Jackets" in valid_cats
assert "Men" in valid_genders

# ── 6. Build props and write ──────────────────────────────────────────────
def infer_materials(body_html):
    text = body_html.lower()
    mats = []
    for kw, notion_name in MATERIAL_MAP.items():
        if kw in text and notion_name in valid_materials and notion_name not in mats:
            mats.append(notion_name)
    return mats

def infer_season(body_html, name):
    text = (body_html + " " + name).lower()
    if any(w in text for w in ["mesh", " air ", "vented", "ventilat"]):
        return "☀️ Summer"
    if any(w in text for w in ["h2o", "gtx", "gore-tex", "waterproof", "winter", "thermal", "insul"]):
        return "🌦 Mid season"
    return "🌦 Mid season"  # sensible default for jackets

added = []
skipped = []

for name, p in new_products:
    body_html = p.get("body_html") or ""
    description = strip_html(body_html)[:400]

    # Pick canonical URL (first color variant's handle)
    url = f"{BASE}/en-us/products/{p['handle']}"

    # Images — HEAD-check, cap at 8
    raw_imgs = []
    for img in (p.get("images") or []):
        src = img["src"] if isinstance(img, dict) else img
        if src.startswith("//"):
            src = "https:" + src
        raw_imgs.append(src)

    imgs_ok = [u for u in raw_imgs if head_ok(u)][:8]

    # Materials
    materials = infer_materials(body_html)

    # Season
    season_name = infer_season(body_html, name)
    valid_seasons = {o["name"] for o in schema["Season"]["multi_select"]["options"]}
    seasons = [season_name] if season_name in valid_seasons else []

    # Build Notion properties
    props = {
        "Name of product": {"title": [{"text": {"content": name}}]},
        "Brand": {"select": {"name": "REV'IT!"}},
        "Category": {"multi_select": [{"name": "Jackets"}]},
        "Gender": {"multi_select": [{"name": "Men"}]},
        "Vegan Verified": {"select": {"name": "Verified Vegan by us"}},
        "URL": {"url": url},
    }

    if description:
        props["Description"] = {"rich_text": [{"text": {"content": description}}]}

    if materials:
        props["Materials"] = {"multi_select": [{"name": m} for m in materials]}

    if seasons:
        props["Season"] = {"multi_select": [{"name": s} for s in seasons]}

    if imgs_ok:
        props["Photos"] = {"files": [
            {"type": "external", "name": name[:90], "external": {"url": u}}
            for u in imgs_ok
        ]}

    try:
        n.pages.create(parent={"database_id": db}, properties=props)
        print(f"  ✅ {name:45} {len(imgs_ok)} photos  mats={materials}")
        added.append(name)
    except Exception as e:
        print(f"  ❌ {name}: {e}")
        skipped.append((name, str(e)))

print(f"\n{'='*60}")
print(f"DONE — {len(added)} added, {len(skipped)} failed")
if skipped:
    for name, err in skipped:
        print(f"  FAILED: {name} — {err}")
