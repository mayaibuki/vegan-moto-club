"""
fix_revit_fields.py
Re-derive Gender, Riding style, Level of Waterproof, and Level of Protection
for the REV'IT! men's-collection jackets using the Shopify `tags` field
(authoritative, merchant-curated) instead of body_html prose.

Protection combines the official CE garment class (EN 17092: A/AA/AAA) with
intended use; "Most protective" is reserved for racing-tagged gear.

Matches by product NAME across the whole DB because the scheduled audit
corrupted Brand/Category on some rows (so those are unreliable as filters).

Tag-driven, deterministic. No API needed.

Run: set -a && source ./.env.local && set +a && python3 "Scheduled audit/fix_revit_fields.py"
"""

import os, re, requests
from notion_client import Client

H = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
n = Client(auth=os.environ["NOTION_API_KEY"])
db = os.environ["NOTION_PRODUCTS_DB_ID"]
DS = n.databases.retrieve(db)["data_sources"][0]["id"]
COLLECTION = "https://revitsport.com/en-us/collections/men-motorcycle-jackets"

def norm(s):
    return re.sub(r"[^a-z0-9 ]", "", s.lower()).strip()

# ── 1. Fetch live tags per model ───────────────────────────────────────────
print("Fetching REV'IT! collection tags…")
prods = requests.get(f"{COLLECTION}/products.json", params={"limit": 250},
                     headers=H, timeout=20).json()["products"]
model_tags = {}   # normalized name -> set of tags (lowercased)
for p in prods:
    base = re.sub(r"\s*\|\s*.*$", "", p["title"]).strip()
    tags = {t.lower() for t in (p.get("tags") or [])}
    model_tags.setdefault(norm(base), tags)
print(f"  {len(model_tags)} unique models")

# ── 2. Pull exact schema option strings (avoid trailing-space bugs) ────────
schema = n.data_sources.retrieve(data_source_id=DS)["properties"]
WP_OPTS = [o["name"] for o in schema["Level of Waterproof"]["select"]["options"]]
RS_OPTS = [o["name"] for o in schema["Riding style"]["multi_select"]["options"]]
GEN_OPTS = [o["name"] for o in schema["Gender"]["multi_select"]["options"]]

def wp_option(substr):
    """Find the schema option containing substr (case-insensitive)."""
    for o in WP_OPTS:
        if substr.lower() in o.lower():
            return o
    return None

# ── 3. Tag → field mappers ─────────────────────────────────────────────────
def map_gender(tags):
    has_w = "women's" in tags or "women" in tags
    has_m = "men's" in tags or "men" in tags
    has_u = "unisex" in tags
    if has_u or (has_w and has_m):
        return ["Unisex"]
    if has_w and not has_m:
        return ["Women"]
    return ["Men"]

# riding-style tag substrings -> canonical riding styles
def map_riding(tags):
    styles = set()
    joined = " | ".join(tags)
    if "off-road" in joined or "offroad" in joined:
        styles.add("Off-roading")
        styles.add("Adventure / Touring")
    if "adventure" in joined:            # adventure / adventure tour / travel / sport
        styles.add("Adventure / Touring")
    if "sport" in joined:                # sport / urban sport / adventure sport
        styles.add("Sport / Canyons")
    if "urban" in joined:                # urban / urban sport
        styles.add("Commute / Street")
    if "race" in joined or "racing" in joined or "track" in joined:
        styles.add("Racing / Trackdays")
    # keep only valid options, preserve schema order
    return [s for s in RS_OPTS if s in styles]

def map_waterproof(tags):
    joined = " | ".join(tags)
    if "gore-tex" in joined or "goretex" in joined or "gore tex" in joined:
        return wp_option("gore-tex")
    if "hydratex" in joined:
        return wp_option("hydratex")
    if "waterproof" in joined or "aquadefence" in joined or "tizip" in joined:
        return wp_option("waterproof") or "Waterproof"
    if "water resistant" in joined or "water-resistant" in joined:
        return wp_option("water resistant")
    return wp_option("not waterproof") or "Not waterproof"

# Protection: combine official CE garment class (EN 17092) with intended use.
# "Most protective" is gated behind a Racing tag so it can't be over-applied.
PROT_RANK = {"Slightly protective": 1, "Moderately protective": 2,
             "Highly protective": 3, "Most protective": 4}

def garment_class(tags):
    """Return AAA / AA / A / B from CE class tag, else None (alternation is ordered)."""
    m = re.search(r"class\s+(aaa|aa|a|b)\b", " | ".join(tags))
    return m.group(1).upper() if m else None

def map_protection(styles, cls):
    # class-implied floor (objective abrasion rating)
    class_lvl = {"AAA": "Highly protective", "AA": "Moderately protective",
                 "A": "Slightly protective", "B": "Slightly protective"}.get(cls, "Slightly protective")
    # use-implied level (intended discipline)
    if "Racing / Trackdays" in styles:
        use_lvl = "Most protective" if cls in ("AAA", "AA") else "Highly protective"
    elif "Sport / Canyons" in styles:
        use_lvl = "Highly protective"
    elif "Adventure / Touring" in styles:
        use_lvl = "Moderately protective"
    else:                                   # commute / street / off-road / none
        use_lvl = "Slightly protective"
    final = max([class_lvl, use_lvl], key=lambda x: PROT_RANK[x])
    # honesty guard: never label "Most protective" without a racing intent
    if final == "Most protective" and "Racing / Trackdays" not in styles:
        final = "Highly protective"
    return final

# ── 4. Match by NAME across the whole DB (Brand/Category got corrupted by the
#       scheduled audit, so they are unreliable as filters). ─────────────────
# Build a name index: both the full normalized name AND the prefix-stripped
# "core" name (so "Convergent H2O" matches collection "Jacket Convergent H2O").
PREFIX = re.compile(r"^(jacket|smock|jersey|overshirt|hoodie|sweater|one piece)\s+")
def core(s):
    return PREFIX.sub("", norm(s)).strip()

by_full = dict(model_tags)                       # normalized full name -> tags
by_core = {}                                     # core name -> tags (skip collisions)
for k, t in model_tags.items():
    c = PREFIX.sub("", k).strip()
    by_core[c] = None if c in by_core else t      # mark ambiguous cores as None

print("\nScanning entire products DB and matching by name…")
pages, has_more, cursor = [], True, None
while has_more:
    kw = {"data_source_id": DS, "page_size": 100}
    if cursor:
        kw["start_cursor"] = cursor
    resp = n.data_sources.query(**kw)
    pages += resp["results"]
    has_more = resp["has_more"]
    cursor = resp.get("next_cursor")
print(f"  {len(pages)} total products scanned")

# ── 5. Patch each matched page ─────────────────────────────────────────────
updated, unmatched = 0, []
for pg in pages:
    title = pg["properties"].get("Name of product", {}).get("title", [])
    if not title:
        continue
    name = title[0]["plain_text"]
    tags = by_full.get(norm(name)) or by_core.get(core(name))
    if tags is None:
        continue

    gender = map_gender(tags)
    riding = map_riding(tags)
    wp = map_waterproof(tags)
    cls = garment_class(tags)
    prot = map_protection(riding, cls)

    props = {
        # Restore Brand: the old (destructive) audit relabeled ~9 of these to
        # noisy substring matches ("Icon"/"Bison"). They are all REV'IT!.
        "Brand": {"select": {"name": "REV'IT!"}},
        "Gender": {"multi_select": [{"name": g} for g in gender]},
        "Level of Waterproof": {"select": {"name": wp}},
        "Level of Protection": {"select": {"name": prot}},
    }
    if riding:
        props["Riding style"] = {"multi_select": [{"name": s} for s in riding]}

    n.pages.update(page_id=pg["id"], properties=props)
    updated += 1
    print(f"  {name:32} {('CE '+cls) if cls else 'CE ?':6} {prot:22} {riding}")

print(f"\n{'='*60}")
print(f"DONE — {updated} updated")
if unmatched:
    print(f"UNMATCHED ({len(unmatched)}): {unmatched}")
