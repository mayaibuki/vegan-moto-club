"""Upload REV'IT! women's vegan pants (maker-declared) to Notion.
Creates 8 ladies pants. Skips Component 3 H2O (already added as unisex)."""
import os, json, time
from notion_client import Client

n = Client(auth=os.environ["NOTION_API_KEY"])
DB = os.environ["NOTION_PRODUCTS_DB_ID"]
DS = n.databases.retrieve(DB)["data_sources"][0]["id"]

src = {p["name"]: p for p in json.load(open(os.path.join(os.path.dirname(__file__), "women_pants.json")))}

GTX = "Waterproof (Gore-tex®) "   # trailing space matches schema option exactly
HYD = "Waterproof (Hydratex®)"

MAP = {
 "Pants Sand 5 H2O Ladies": dict(protection="Highly protective", waterproof=HYD,
    riding=["Adventure / Touring"], season=["☀️ Summer","🌦 Mid season","❄️ Winter"],
    materials=["Polyester","Elastane (Elastic fabric)","Mesh fabric"],
    description="The women's-fit version of REV'IT!'s long-running Sand travel pant, with a slightly more speed-driven cut than the Sand 4. It uses the proven over-and-under concept: a detachable 3L hydratex waterproof liner you can wear over or under the CE-certified protection layer, plus a detachable thermal liner for cold, wet days. Drop-down mesh thigh vents and calf straps handle the heat, and it's Class AA certified with CE-level 2 SEEFLEX knee and CE-level 1 SEESMART hip armor. Made with recycled polyester; all-textile, no leather."),
 "Pants Airwave 4 Ladies": dict(protection="Moderately protective", waterproof="Not waterproof",
    riding=["Adventure / Touring","Commute / Street"], season=["☀️ Summer"],
    materials=["Mesh fabric","Polyester","Elastane (Elastic fabric)"],
    description="A hot-weather adventure-sport pant in a female-specific fit, built for maximum airflow. It combines PWR|Shell mesh, ripstop, and stretch with full ventilation down the front of the legs and around three-quarters of the back, directing air to your lower half on the hottest rides. Despite the open construction it carries a Class AA CE rating, with SEESMART hip and adjustable knee protection and laminated reflective detail at the knees. All-textile, no leather."),
 "Pants Tornado 4 H2O Ladies": dict(protection="Highly protective", waterproof=HYD,
    riding=["Adventure / Touring"], season=["☀️ Summer","🌦 Mid season","❄️ Winter"],
    materials=["Mesh fabric","Polyester","Elastane (Elastic fabric)"],
    description="A women's-fit multi-season touring pant that swaps between hot and wet conditions with ease. Drop the detachable thermal and 2L hydratex waterproof liners and the fully ventilated mesh leg panels flow air straight to your body; reattach them when it cools or rains. Mesh-and-ripstop construction earns a Class AA rating, with CE-level 2 SEEFLEX knee and CE-level 1 SEESMART hip armor, a grip seat panel, and laminated reflective detail. All-textile, no leather."),
 "Pants Berlin H2O Ladies": dict(protection="Moderately protective", waterproof=HYD,
    riding=["Commute / Street"], season=["☀️ Summer","🌦 Mid season","❄️ Winter"],
    materials=["Polyester","Elastane (Elastic fabric)"],
    description="A versatile women's city pant built from a three-layer softshell with breathable and thermal properties for multi-season commuting. A 100% waterproof hydratex G-liner is bonded to the inner lining, and an extra-long easy-entry zipper with a wind-and-water catcher behind it makes changing quick and keeps you dry at speed. SEESMART CE-level 1 knee and hip armor and reflective ankle straps add protection and visibility. All-textile, no leather."),
 "Pants Lamina GTX Ladies": dict(protection="Highly protective", waterproof=GTX,
    riding=["Adventure / Touring"], season=["☀️ Summer","🌦 Mid season","❄️ Winter"],
    materials=["Gore-tex (waterproof fabric)","Polyester","Elastane (Elastic fabric)"],
    description="A women's adventure-travel pant designed from the ground up around the female physique — not a resized men's pattern — by REV'IT!'s design and R&D team. Laminated GORE-TEX keeps all-day, all-weather rain out, while waist-reducing tabs and adjustment straps at the calves, waist, and hems dial in the fit. CE-level 2 SEEFLEX knee and CE-level 1 SEESMART hip armor handle protection, with front pockets, ventilation zippers, a gripping seat panel, and a short connection zipper for the matching jacket. All-textile, no leather."),
 "Pants Eclipse 2 Ladies": dict(protection="Moderately protective", waterproof=HYD,
    riding=["Commute / Street"], season=["☀️ Summer","🌦 Mid season"],
    materials=["Mesh fabric","Polyester"],
    description="A chino-inspired women's urban riding pant for warm city days, now with a detachable hydratex waterproof liner so you can stay dry when the weather turns. Full-coverage polyester mesh panels front and back keep air moving, while the rest is abrasion-resistant 600-denier polyester. The clean regular-fit silhouette hides welded reflective ankle detail and low-profile CE-rated armor, with height-adjustable SEESMART knee protection. All-textile, no leather."),
 "Pants Outback 5 H2O Ladies": dict(protection="Highly protective", waterproof=HYD,
    riding=["Adventure / Touring"], season=["☀️ Summer","🌦 Mid season","❄️ Winter"],
    materials=["Polyester","Elastane (Elastic fabric)"],
    description="The women's-fit fifth generation of REV'IT!'s long-running Outback adventure-touring pant, on a tried-and-tested three-layer system with detachable thermal insulation and over-and-under hydratex waterproofing. New diagonally cut drop-down vents improve airflow, and stretch across the knees plus two waist buckles keep the fit secure but flexible. Class AA certified with top-tier CE-level 2 SEEFLEX knee and CE-level 1 SEESMART hip armor, plus reflective detailing. All-textile, no leather."),
 "Pants Convergent H2O Ladies": dict(protection="Highly protective", waterproof=HYD,
    riding=["Adventure / Touring"], season=["☀️ Summer","🌦 Mid season","❄️ Winter"],
    materials=["Mesh fabric","Polyester","Elastane (Elastic fabric)"],
    description="A straightforward, fully waterproof women's touring pant built around a fixed hydratex mesh G-liner. A detachable thermal liner extends the season, while waist straps and hook-and-loop hems dial in the fit and a short connection zipper secures it to your jacket so your lower back stays covered. Class AA certified with CE-level 2 SEEFLEX knee and CE-level 1 SEESMART hip armor, plus grip patches, a thigh cargo pocket, and reflective detailing. All-textile, no leather."),
}

def build_props(name, m):
    p = src[name]
    props = {
        "Name of product": {"title": [{"text": {"content": name}}]},
        "URL": {"url": p["url"]},
        "Brand": {"select": {"name": "REV'IT!"}},
        "Gender": {"multi_select": [{"name": "Women"}]},
        "Category": {"multi_select": [{"name": "Pants"}]},
        "Level of Protection": {"select": {"name": m["protection"]}},
        "Level of Waterproof": {"select": {"name": m["waterproof"]}},
        "Riding style": {"multi_select": [{"name": s} for s in m["riding"]]},
        "Season": {"multi_select": [{"name": s} for s in m["season"]]},
        "Materials": {"multi_select": [{"name": x} for x in m["materials"]]},
        "Vegan Verified": {"select": {"name": "Confirmed Vegan by maker"}},
        "Description": {"rich_text": [{"text": {"content": m["description"]}}]},
    }
    if p.get("img"):
        props["Photos"] = {"files": [{"type": "external", "name": name, "external": {"url": p["img"]}}]}
    return props

created = errors = 0
for name, m in MAP.items():
    try:
        n.pages.create(parent={"database_id": DB}, properties=build_props(name, m))
        print(f"[CREATED] {name}"); created += 1
    except Exception as e:
        print(f"[ERROR] {name}: {e}"); errors += 1
    time.sleep(0.4)

print(f"\nDone. created={created} errors={errors} (Component 3 H2O skipped - already unisex)")
