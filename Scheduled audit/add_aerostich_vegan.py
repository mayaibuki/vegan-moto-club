"""
add_aerostich_vegan.py
Add 22 vegan Aerostich products from 4 collections (r-3, roadcrafter-classic,
cousin-jeremy, falstaff) to Notion.

All shells are synthetic (TLTex/Cordura/HT-Nylon) EXCEPT the waxed-cotton lines
(Cousin Jeremy + Falstaff), whose factory wax type is unconfirmed -> those go in
flagged "Waiting for confirmation as Vegan". The synthetic ones are "Verified
Vegan by AI".

Idempotent: skips any product whose exact Name already exists (protects the 4
r-3 rows added in the prior dedup task, and makes reruns safe).

Dry-run unless APPLY=1.
"""
import os, re, json, time, urllib.request
from notion_client import Client

H = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'}
n = Client(auth=os.environ["NOTION_API_KEY"])
DB = os.environ["NOTION_PRODUCTS_DB_ID"]
DS = n.databases.retrieve(DB)["data_sources"][0]["id"]
APPLY = os.environ.get("APPLY") == "1"

# clean studio shots: numeric SKU prefix + .jpg; drop word/date-named lifestyle + .png diagrams
KEEP = re.compile(r'^\d{3}_', re.I)
BLOCK = re.compile(r'(aerostitch|copy|lifestyle|display)', re.I)

CORDURA = "Cordura® (Synhtetic fabric)"
NYLON = "Nylon"
COTTON = "Cotton"
RIDING = ["Commute / Street", "Adventure / Touring"]
ALLSEASON = ["☀️ Summer", "🌦 Mid season", "❄️ Winter"]
LIGHT_SEASON = ["☀️ Summer", "🌦 Mid season"]
AI = "Verified Vegan by AI"
WAIT = "Waiting for confirmation as Vegan"
BASE = "https://www.aerostich.com/products/"


def gallery(handle, cap=8):
    u = f'{BASE}{handle}.json'
    d = json.load(urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=30))['product']
    out = []
    for im in d['images']:
        fn = im['src'].split('/files/')[-1].split('?')[0]
        if not KEEP.search(fn) or not fn.lower().endswith('.jpg') or BLOCK.search(fn):
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


def files(name, urls):
    return {"files": [{"type": "external", "name": name, "external": {"url": u}} for u in urls]}


# Descriptions (written from body_html, humanized tone)
D = {
 "r3light": ("The R-3 Light is the lighter-weight take on Aerostich's R-3 one-piece suit. A 200-denier "
   "high-tenacity nylon shell with 500-denier reinforcement at the elbows, shoulders and knees sheds weight "
   "while keeping real-world abrasion protection, and the full-length waterproof zipper still lets you pull it "
   "on over street clothes in seconds. Unlined for airflow, with impact armor included. Made in the USA."),
 "rcsuit": ("The original Roadcrafter — Aerostich's one-piece commuter suit that pulls on over your clothes in "
   "under a minute through a full-length zipper. Built from made-in-USA mil-spec 500-denier Cordura with "
   "ballistic nylon reinforcement and a high-pic Supernyl lining, with impact armor at the shoulders, elbows, "
   "hips and knees. You'll ride warmer when it's cool, cooler when it's hot and drier when it's wet."),
 "rcjacket": ("The two-piece Roadcrafter Classic jacket — made-in-USA mil-spec 500-denier Cordura with impact "
   "armor and the vents, pockets and tailoring refined over decades of all-weather commuting. Zips to the "
   "matching Roadcrafter Classic pants for a near one-piece feel."),
 "rcpants": ("The two-piece Roadcrafter Classic overpants — made-in-USA mil-spec 500-denier Cordura with knee "
   "and hip armor. Pull them on over street clothes; zip to the matching jacket when you want full coverage."),
 "rcljacket": ("The lighter Roadcrafter Classic jacket — a 200-denier high-tenacity nylon shell with 500-denier "
   "reinforcement at the elbows, shoulders and knees. Cooler and lighter than the standard Classic, with the "
   "same armor, venting and made-in-USA build."),
 "rclpants": ("The lighter Roadcrafter Classic overpants — a 200-denier high-tenacity nylon shell with "
   "500-denier reinforcement at the knees. Cooler and lighter than the standard Classic pants, with the same "
   "armor and made-in-USA build."),
 "cjsuit": ("The Cousin Jeremy is the waxed-cotton Roadcrafter — the same pull-on-over-your-clothes one-piece "
   "design rendered in tough 10.10 oz English waxed cotton over a smooth nylon lining. Waterproof and "
   "breathable, it forms to your body with no break-in and re-waxes to renew its weather protection. "
   "Double-layer waxed cotton plus removable TF armor at the shoulders, elbows and knees. Made in the USA."),
 "cjjacket": ("The Cousin Jeremy jacket pairs classic 10.10 oz English waxed cotton with modern Roadcrafter "
   "ergonomics — vents, pockets, removable TF armor and a smooth nylon lining. Waterproof, breathable and "
   "built to develop a worn-in patina over the miles. Made in the USA."),
 "cjpants": ("The Cousin Jeremy overpants in tough 10.10 oz English waxed cotton, with a second waxed-cotton "
   "layer at the knees for added abrasion protection. Waterproof, breathable and refined over thirty years of "
   "road experience. Made in the USA."),
 "faljacket": ("The Falstaff is Aerostich's classic British-style riding jacket in authentic 100% English waxed "
   "cotton — windproof, waterproof and breathable, aging into a patina that tells your own road story. Modern "
   "venting, removable TF impact armor and Scotchlite reflective panels, with a rich plaid cotton lining and a "
   "soft synthetic Ultrasuede collar."),
 "falpants": ("The Falstaff overpants in fully-lined 100% English waxed cotton, with the 'oilskin' "
   "waterproofness of a fabric made the same way for over 170 years. A jeans-cut fit with a plaid cotton lining "
   "that matches the Falstaff jacket."),
 "cfaljacket": ("The Competition Falstaff steps up to heavy-duty 10.10 oz English waxed cotton over the standard "
   "Falstaff's 8.25 oz — windproof, waterproof and breathable, with modern venting, removable TF impact armor, "
   "Scotchlite reflective panels, a plaid cotton lining and a soft synthetic Ultrasuede collar."),
 "cfalpants": ("The Competition Falstaff overpants in heavy-duty 10.10 oz English waxed cotton — fully lined, "
   "'oilskin' waterproof, with a jeans-cut fit and a plaid cotton lining that matches the Competition Falstaff "
   "jacket."),
}

W = " Cut for a women's fit."

# (name, handle, gender, category, price, protection, waterproof, season, materials, desc_key, vegan)
SYN, CTN = [CORDURA, NYLON], [COTTON, NYLON]
LIGHT_MAT = [NYLON]
RAC, JKT, PNT = "Racing Suits", "Jackets", "Pants"
HI, MOD = "Highly protective", "Moderately protective"
WP, NWP = "Waterproof", "Not waterproof"

PRODUCTS = [
 # Group A — synthetic, vegan
 ("R-3 Light One Piece Suit", "mens-r-3-light-one-piece", "Men", RAC, 1927, MOD, WP, LIGHT_SEASON, LIGHT_MAT, "r3light", AI),
 ("R-3 Light One Piece Suit Women", "womens-r-3-light-one-piece", "Women", RAC, 1927, MOD, WP, LIGHT_SEASON, LIGHT_MAT, "r3light", AI),
 ("Roadcrafter Classic One Piece Suit", "mens-roadcrafter-classic-one-piece", "Men", RAC, 1997, HI, NWP, ALLSEASON, SYN, "rcsuit", AI),
 ("Roadcrafter Classic One Piece Suit Women", "womens-roadcrafter-classic-one-piece-suit", "Women", RAC, 1997, HI, NWP, ALLSEASON, SYN, "rcsuit", AI),
 ("Roadcrafter Classic Jacket", "mens-roadcrafter-classic-jacket", "Men", JKT, 1147, HI, NWP, ALLSEASON, SYN, "rcjacket", AI),
 ("Roadcrafter Classic Jacket Women", "womens-roadcrafter-classic-jacket", "Women", JKT, 1147, HI, NWP, ALLSEASON, SYN, "rcjacket", AI),
 ("Roadcrafter Classic Pants", "mens-roadcrafter-classic-pants", "Men", PNT, 1047, HI, NWP, ALLSEASON, SYN, "rcpants", AI),
 ("Roadcrafter Classic Pants Women", "womens-roadcrafter-classic-pants", "Women", PNT, 1047, HI, NWP, ALLSEASON, SYN, "rcpants", AI),
 ("Roadcrafter Classic Light Jacket", "mens-roadcrafter-classic-light-jacket", "Men", JKT, 1147, MOD, NWP, LIGHT_SEASON, LIGHT_MAT, "rcljacket", AI),
 ("Roadcrafter Classic Light Jacket Women", "womens-roadcrafter-classic-light-jacket", "Women", JKT, 1147, MOD, NWP, LIGHT_SEASON, LIGHT_MAT, "rcljacket", AI),
 ("Roadcrafter Classic Light Pants", "mens-roadcrafter-classic-light-pants", "Men", PNT, 1047, MOD, NWP, LIGHT_SEASON, LIGHT_MAT, "rclpants", AI),
 ("Roadcrafter Classic Light Pants Women", "womens-roadcrafter-classic-light-pants", "Women", PNT, 1047, MOD, NWP, LIGHT_SEASON, LIGHT_MAT, "rclpants", AI),
 # Group B — waxed cotton, unconfirmed
 ("Cousin Jeremy One Piece Suit", "mens-cousin-jeremy-one-piece-suit", "Men", RAC, 1807, MOD, WP, ALLSEASON, CTN, "cjsuit", WAIT),
 ("Cousin Jeremy One Piece Suit Women", "womens-cousin-jeremy-one-piece-suit", "Women", RAC, 1807, MOD, WP, ALLSEASON, CTN, "cjsuit", WAIT),
 ("Cousin Jeremy Jacket", "mens-cousin-jeremy-jacket", "Men", JKT, 1037, MOD, WP, ALLSEASON, CTN, "cjjacket", WAIT),
 ("Cousin Jeremy Jacket Women", "womens-cousin-jeremy-jacket", "Women", JKT, 1037, MOD, WP, ALLSEASON, CTN, "cjjacket", WAIT),
 ("Cousin Jeremy Pants", "mens-cousin-jeremy-pants", "Men", PNT, 977, MOD, WP, ALLSEASON, CTN, "cjpants", WAIT),
 ("Cousin Jeremy Pants Women", "womens-cousin-jeremy-pants", "Women", PNT, 977, MOD, WP, ALLSEASON, CTN, "cjpants", WAIT),
 ("Falstaff Jacket", "falstaff-jacket", "Men", JKT, 1097, MOD, WP, ALLSEASON, CTN, "faljacket", WAIT),
 ("Falstaff Pants", "falstaff-pants", "Men", PNT, 867, MOD, WP, ALLSEASON, CTN, "falpants", WAIT),
 ("Competition Falstaff Jacket", "competition-falstaff-jacket", "Men", JKT, 1097, MOD, WP, ALLSEASON, CTN, "cfaljacket", WAIT),
 ("Competition Falstaff Pants", "competition-falstaff-pants", "Men", PNT, 867, MOD, WP, ALLSEASON, CTN, "cfalpants", WAIT),
]


def exists(name):
    r = n.data_sources.query(data_source_id=DS, filter={
        "property": "Name of product", "title": {"equals": name}})
    return bool(r["results"])


def build_props(name, handle, gender, cat, price, prot, wp, season, mats, dkey, vegan, imgs):
    desc = D[dkey] + (W if gender == "Women" else "")
    props = {
        "Name of product": {"title": [{"text": {"content": name}}]},
        "URL": {"url": BASE + handle},
        "Brand": {"select": {"name": "AeroStitch"}},
        "Gender": {"multi_select": [{"name": gender}]},
        "Category": {"multi_select": [{"name": cat}]},
        "Level of Protection": {"select": {"name": prot}},
        "Level of Waterproof": {"select": {"name": wp}},
        "Riding style": {"multi_select": [{"name": r} for r in RIDING]},
        "Season": {"multi_select": [{"name": s} for s in season]},
        "Materials": {"multi_select": [{"name": m} for m in mats]},
        "Price": {"number": price},
        "Vegan Verified": {"select": {"name": vegan}},
        "Description": {"rich_text": [{"text": {"content": desc}}]},
    }
    if imgs:
        props["Photos"] = files(name, imgs)
    return props


created = skipped = 0
for row in PRODUCTS:
    name, handle = row[0], row[1]
    if exists(name):
        print(f"[SKIP] exists: {name}")
        skipped += 1
        continue
    imgs = gallery(handle)
    props = build_props(*row, imgs)
    flag = "VEGAN" if row[10] == AI else "WAIT "
    print(f"[CREATE {flag}] {name:42} ${row[4]:>5}  photos={len(imgs)}")
    if APPLY:
        n.pages.create(parent={"database_id": DB}, properties=props)
        time.sleep(0.4)

    created += 1

print(f"\n{'APPLIED' if APPLY else 'DRY-RUN'}: {created} created, {skipped} skipped")
