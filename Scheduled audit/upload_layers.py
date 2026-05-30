"""
upload_layers.py
Add the 9 maker-declared vegan REV'IT! base/mid layers to Notion.
Category mapping (closest existing): Jacket->Jackets, Pants->Pants, Undersuit->Racing Suits.
All are non-protective undergarments -> "Not protective", "Not waterproof".
Unisex undersuits (Blast, Excellerator 2) deduped to one row each.
Names: strip leading garment word; "Pants Core 2" -> "Core 2 Pants" to avoid clash
with "Jacket Core 2" -> "Core 2".
Dry-run unless APPLY=1.
"""
import os, json, time
from notion_client import Client

n = Client(auth=os.environ["NOTION_API_KEY"])
DB = os.environ["NOTION_PRODUCTS_DB_ID"]
DS = n.databases.retrieve(DB)["data_sources"][0]["id"]
APPLY = os.environ.get("APPLY") == "1"

HERE = os.path.dirname(__file__)
items = json.load(open(os.path.join(HERE, "layers.json")))

# keyed by original layers.json name:
# (final_name, category, gender, materials, season, riding, description)
JKT = "Jackets"; PNT = "Pants"; RAC = "Racing Suits"
WARM = ["🌦 Mid season", "❄️ Winter"]
HOT = ["☀️ Summer", "🌦 Mid season"]
TOUR = ["Adventure / Touring", "Commute / Street"]
RACE = ["Racing / Trackdays", "Sport / Canyons"]
PL = ["PrimaLoft®", "Polyester"]
POLY = ["Polyester", "Elastane (Elastic fabric)"]

DETAIL = {
 "Undersuit Blast": ("Blast", RAC, "Unisex", POLY, HOT, RACE,
   "A hot-weather track undersuit in low-friction PWR|Jersey with elastane and a large open-knit structure for maximum airflow. Moisture-wicking and anatomically cut to sit under one-piece race leathers, with thumb loops, ankle straps and an easy-entry front zip. Unisex."),
 "Undersuit Excellerator 2": ("Excellerator 2", RAC, "Unisex", POLY, HOT, RACE,
   "A lightweight base-layer undersuit in moisture-wicking PWR|Jersey with elastane, shaped to be worn under a one-piece leather suit. Makes peeling the leathers on and off far easier, with thumb loops, ankle straps and a diagonal front zip. Unisex."),
 "Jacket Climate 3": ("Climate 3", JKT, "Men", POLY, WARM, TOUR,
   "A high-tech insulating mid layer using breathable Polartec® Alpha® for active temperature regulation on the move. Full-stretch with a snug fit, quick-dry hydrophobic properties, underarm ventilation, two side pockets and a chest pocket; packs into its own transport bag."),
 "Jacket Storm 2 WB": ("Storm 2 WB", JKT, "Men", PL, WARM, TOUR,
   "An insulating, windbreaking mid layer combining compact PrimaLoft® Silver synthetic down with a hydratex|Windbarrier® membrane to block wind. Lightweight, packable, with reflective detailing and elasticated cuffs; comes with its own transport bag. Windproof, not waterproof."),
 "Jacket Solar 3": ("Solar 3", JKT, "Men", PL, WARM, TOUR,
   "A packable padded mid layer jacket with PrimaLoft® Silver synthetic down for high warmth at low weight. Slips under your riding jacket on cold mornings, then packs into its own carrier bag when it warms up; two zippered side pockets, a chest pocket and elastic drawcords."),
 "Jacket Core 2": ("Core 2", JKT, "Men", POLY, WARM, TOUR,
   "REV'IT!'s entry-level insulating mid layer jacket — highly breathable, lightweight and packable. Worn under any outer shell without a thermal liner to extend your riding season; compact enough to stow under a seat or in a backpack via its transport bag."),
 "Pants Core 2": ("Core 2 Pants", PNT, "Men", POLY, WARM, TOUR,
   "Insulating mid layer pants that slip between your base layer and riding trousers for added warmth without restricting movement. Breathable, lightweight and packable into their own compact carrier bag."),
 "Jacket Core 2 Ladies": ("Core 2 Ladies", JKT, "Women", POLY, WARM, TOUR,
   "The women's-fit entry-level insulating mid layer jacket — highly breathable, lightweight and packable. Worn under any outer shell without a thermal liner to extend your riding season; stows away in its own transport bag."),
 "Jacket Solar 3 Ladies": ("Solar 3 Ladies", JKT, "Women", PL, WARM, TOUR,
   "The women's-fit packable padded mid layer jacket with PrimaLoft® Silver synthetic down for high warmth at low weight. Slips under your riding jacket on cold mornings, then packs into its own carrier bag; two zippered side pockets, a chest pocket and elastic drawcords."),
}

def build_props(item):
    final, cat, gender, mats, season, riding, desc = DETAIL[item["name"]]
    props = {
        "Name of product": {"title": [{"text": {"content": final}}]},
        "URL": {"url": item["url"]},
        "Brand": {"select": {"name": "REV'IT!"}},
        "Gender": {"multi_select": [{"name": gender}]},
        "Category": {"multi_select": [{"name": cat}]},
        "Level of Protection": {"select": {"name": "Not protective"}},
        "Level of Waterproof": {"select": {"name": "Not waterproof"}},
        "Riding style": {"multi_select": [{"name": r} for r in riding]},
        "Season": {"multi_select": [{"name": s} for s in season]},
        "Materials": {"multi_select": [{"name": m} for m in mats]},
        "Vegan Verified": {"select": {"name": "Confirmed Vegan by maker"}},
        "Description": {"rich_text": [{"text": {"content": desc}}]},
    }
    if item.get("img"):
        props["Photos"] = {"files": [{"type": "external", "name": final, "external": {"url": item["img"]}}]}
    return final, cat, props

def find_row(title_exact):
    r = n.data_sources.query(data_source_id=DS, filter={
        "property": "Name of product", "title": {"equals": title_exact}})
    return r["results"][0] if r["results"] else None

created = updated = 0
done = set()
for item in items:
    if item["name"] in done:   # unisex undersuit second occurrence
        continue
    done.add(item["name"])
    final, cat, props = build_props(item)
    existing = find_row(final)
    if existing:
        print(f"UPDATE {final}  [{cat}]")
        updated += 1
        if APPLY:
            n.pages.update(page_id=existing["id"], properties=props); time.sleep(0.4)
    else:
        print(f"CREATE {final:18} [{cat:13}] {props['Gender']['multi_select'][0]['name']:6} "
              f"season={[s['name'] for s in props['Season']['multi_select']]} "
              f"mats={[m['name'] for m in props['Materials']['multi_select']]}")
        created += 1
        if APPLY:
            n.pages.create(parent={"database_id": DB}, properties=props); time.sleep(0.4)

print(f"\n{'APPLIED' if APPLY else 'DRY-RUN'}: {created} create, {updated} update")
