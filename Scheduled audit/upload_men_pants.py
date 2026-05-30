"""Upload REV'IT! men's vegan pants (maker-declared) to Notion.
Creates 15 new; updates existing Pants Eclipse 2. Pulls img/url from men_pants.json."""
import os, json, time
from notion_client import Client

n = Client(auth=os.environ["NOTION_API_KEY"])
DB = os.environ["NOTION_PRODUCTS_DB_ID"]
DS = n.databases.retrieve(DB)["data_sources"][0]["id"]

src = {p["name"]: p for p in json.load(open(os.path.join(os.path.dirname(__file__), "men_pants.json")))}

GTX = "Waterproof (Gore-tex®) "   # note trailing space in schema option
HYD = "Waterproof (Hydratex®)"

# name -> mapped props (+ action)
MAP = {
 "Pants Offtrack 3 H2O": dict(action="create", protection="Highly protective", waterproof=HYD,
    riding=["Adventure / Touring"], season=["☀️ Summer","🌦 Mid season","❄️ Winter"],
    materials=["Polyester","Elastane (Elastic fabric)","Mesh fabric"],
    description="A true all-season adventure pant built on a three-layer system: a durable softshell and ripstop outer, a detachable thermal liner, and a removable 3L hydratex waterproof layer with over-and-under functionality. Thigh ventilation panels keep airflow up when the ride heats up, and it's Class AA certified with CE-level 2 SEEFLEX knee armor and CE-level 1 SEESMART hip protectors. Hook-and-loop adjustment lets you wear it over or tucked into boots, with short and long zippers to connect to your jacket. All-textile construction, with no leather."),
 "Pants Sand 5 H2O": dict(action="create", protection="Highly protective", waterproof=HYD,
    riding=["Adventure / Touring"], season=["☀️ Summer","🌦 Mid season","❄️ Winter"],
    materials=["Polyester","Elastane (Elastic fabric)"],
    description="The latest in REV'IT!'s long-running Sand travel line, with a slightly more speed-driven cut than the Sand 4. It uses the proven over-and-under concept: a detachable 3L hydratex waterproof liner you can wear over or under the CE-certified protection layer, plus a detachable thermal liner for cold, wet days. Drop-down thigh vents and calf straps handle warm weather, and it's Class AA certified with CE-level 2 SEEFLEX knee and CE-level 1 SEESMART hip armor. Made with recycled polyester throughout; all-textile, no leather."),
 "Pants Potential GTX": dict(action="create", protection="Moderately protective", waterproof=GTX,
    riding=["Adventure / Touring","Commute / Street"], season=["☀️ Summer","🌦 Mid season","❄️ Winter"],
    materials=["Gore-tex (waterproof fabric)","Polyester","Elastane (Elastic fabric)"],
    description="A sport-leaning adventure pant with a slim, pre-shaped fit that feels close to a second skin. A GORE-TEX Z-liner floats the waterproof membrane between the outer shell and lining, keeping you dry while leaving the polyester ripstop and stretch-twill outer clean and flexible. A detachable thermal liner adds seasonal range, and stretch at the waist keeps it comfortable in the saddle. CE-level 1 SEESMART protection and recycled polyester construction; all-textile, no leather."),
 "Pants Airwave 4": dict(action="create", protection="Moderately protective", waterproof="Not waterproof",
    riding=["Adventure / Touring","Commute / Street"], season=["☀️ Summer"],
    materials=["Mesh fabric","Polyester","Elastane (Elastic fabric)"],
    description="A hot-weather adventure-sport pant built for maximum airflow. It combines PWR|Shell mesh, ripstop, and stretch with full ventilation down the front of the legs and around three-quarters of the back, so air reaches your lower half on the hottest rides. Despite the open construction it carries a Class AA CE rating, with SEESMART hip and adjustable knee protection and laminated reflective detail at the knees. All-textile, no leather."),
 "Pants Eclipse 2": dict(action="update", protection="Moderately protective", waterproof="Not waterproof",
    riding=["Commute / Street"], season=["☀️ Summer"],
    materials=["Mesh fabric","Polyester"],
    description="A chino-inspired urban riding pant for warm city days. Polyester mesh panels run the full length, front and back, to keep air moving, while the rest is abrasion-resistant 600-denier polyester. The clean, regular-fit silhouette hides its technical side: welded reflective detail at the ankle and CE-rated armor that stays low-profile at the hips and knees, with height-adjustable SEESMART knee protection. Made with recycled polyester; all-textile, no leather."),
 "Pants Neptune 3 GTX": dict(action="create", protection="Highly protective", waterproof=GTX,
    riding=["Adventure / Touring"], season=["☀️ Summer","🌦 Mid season","❄️ Winter"],
    materials=["Gore-tex (waterproof fabric)","Polyester","Elastane (Elastic fabric)"],
    description="An adventure-touring pant laminated with GORE-TEX — 3L at the seat and crotch where water hits hardest, 2L elsewhere — to keep the rain out across the seasons. A removable thermal liner and large VCS|Aquadefence ventilation panels with FidLock magnetic fasteners let you dial climate in fast. It's Class AA certified with SEEFLEX knee and SEESMART hip armor, plus grip patches at the seat. All-textile, no leather."),
 "Pants Alpinus GTX": dict(action="create", protection="Highly protective", waterproof=GTX,
    riding=["Adventure / Touring","Commute / Street"], season=["🌦 Mid season","❄️ Winter"],
    materials=["Gore-tex (waterproof fabric)","Polyester"],
    description="High-end GORE-TEX overpants for slipping on when the weather turns. The 3L 400-denier GORE-TEX shell is abrasion-resistant, windproof, and 100% waterproof with virtually no water pick-up, and the long easy-entry zippers let you pull them on without removing your boots. CE-rated SEEFLEX knee and SEESMART hip armor, a Sure Grip seat panel, and a waterproof cargo pocket round it out. All-textile, no leather."),
 "Pants Berlin H2O": dict(action="create", protection="Moderately protective", waterproof=HYD,
    riding=["Commute / Street"], season=["☀️ Summer","🌦 Mid season","❄️ Winter"],
    materials=["Polyester","Elastane (Elastic fabric)"],
    description="A versatile city pant built from a three-layer softshell with breathable and thermal properties for multi-season commuting. A 100% waterproof hydratex G-liner is bonded to the inner lining, and a full-length easy-entry zipper with a wind-and-water catcher behind it makes changing quick and keeps you dry at speed. SEESMART CE-level 1 knee and hip armor and reflective ankle straps add protection and visibility. All-textile, no leather."),
 "Pants Tornado 4 H2O": dict(action="create", protection="Highly protective", waterproof=HYD,
    riding=["Adventure / Touring"], season=["☀️ Summer","🌦 Mid season","❄️ Winter"],
    materials=["Mesh fabric","Polyester","Elastane (Elastic fabric)"],
    description="A multi-season touring pant that swaps between hot and wet conditions easily. Drop the detachable thermal and 2L hydratex waterproof liners and the fully ventilated mesh leg panels flow air straight to your body; reattach them when it cools or rains. Mesh-and-ripstop construction earns a Class AA rating, with CE-level 2 SEEFLEX knee and CE-level 1 SEESMART hip armor, a grip seat panel, and laminated reflective detail. All-textile, no leather."),
 "Pants Vertical GTX": dict(action="create", protection="Highly protective", waterproof=GTX,
    riding=["Adventure / Touring"], season=["☀️ Summer","🌦 Mid season","❄️ Winter"],
    materials=["Gore-tex (waterproof fabric)","Polyester","Elastane (Elastic fabric)"],
    description="A versatile touring pant that takes on most weather without breaking the bank. Laminated GORE-TEX keeps rain out while letting perspiration escape, and a detachable thermal liner handles the temperature swings of multi-season riding. Strategically placed PWR|Shell stretch fabric plus adjustment at the waist, calves, and ankles keep it comfortable and well-fitted, with CE-level 1 SEESMART hip and CE-level 2 SEEFLEX knee armor. All-textile, no leather."),
 "Pants Echelon GTX": dict(action="create", protection="Highly protective", waterproof=GTX,
    riding=["Adventure / Touring"], season=["☀️ Summer","🌦 Mid season","❄️ Winter"],
    materials=["Gore-tex (waterproof fabric)","Polyester"],
    description="An adventure-travel pant wrapped in breathable, 100% waterproof GORE-TEX laminate. Multi-point fit adjustment, ventilation zippers, and connection options for the matching jacket or suspenders pack a lot of clever touring features into one pair. CE-level 2 SEEFLEX knee and CE-level 1 SEESMART hip armor keep you protected through long days in the saddle, and a gripping seat panel stops you sliding around. All-textile, no leather."),
 "Pants Poseidon 3 GTX": dict(action="create", protection="Highly protective", waterproof=GTX,
    riding=["Adventure / Touring"], season=["☀️ Summer","🌦 Mid season","❄️ Winter"],
    materials=["Gore-tex (waterproof fabric)","Polyester"],
    description="An all-season adventure-touring pant built from 2L and 3L GORE-TEX laminated to the outer shell, so wind, rain, and surface spray have no way in. A detachable, packable thermal liner adds warmth without bulk, and VCS|Aquadefence vents with FidLock magnetic fasteners open for airflow with one hand. SEEFLEX CE-level 2 knee and SEESMART CE-level 1 hip armor, plus a Sure Grip seat panel and double connection zippers. All-textile, no leather."),
 "Pants Parabolica 2": dict(action="create", protection="Moderately protective", waterproof="Not waterproof",
    riding=["Commute / Street","Sport / Canyons"], season=["🌦 Mid season"],
    materials=["Polyester","Elastane (Elastic fabric)"],
    description="Motorcycle-ready joggers for urban riders who want comfort without giving up safety. Engineered from PWR|Fleece, the tapered cut delivers lightweight flexibility and a casual, sweatpant-like feel while still carrying a Class AA CE rating. Ultra-thin SEESMART protectors sit at the knees and hips in adjustable pockets so they stay where they should. Made with recycled polyester; all-textile, no leather."),
 "Pants Component 3 H2O": dict(action="create", protection="Moderately protective", waterproof=HYD,
    riding=["Off-roading","Adventure / Touring"], season=["☀️ Summer","🌦 Mid season"], gender=["Men","Women"],
    materials=["Polyester","Elastane (Elastic fabric)"],
    description="A lightweight, waterproof off-road pant from the DIRT Series, worn on its own or as rain-ready overpants. The 3L stretch and heavy-ripstop construction layers comfort with a Class A rating, and a full-length hem-to-hip zipper lets you get them on over boots. Thigh ventilation, a cargo pocket, an aluminum waist hook, and a seamless adaptable waistband keep it practical. Integrated SEESMART armor can be upgraded to a Scram knee protector. All-textile, no leather. (REV'IT! advises women to size down one.)"),
 "Pants Convergent H2O": dict(action="create", protection="Highly protective", waterproof=HYD,
    riding=["Adventure / Touring"], season=["☀️ Summer","🌦 Mid season","❄️ Winter"],
    materials=["Mesh fabric","Polyester","Elastane (Elastic fabric)"],
    description="A straightforward, fully waterproof touring pant built around a fixed hydratex mesh G-liner. A detachable thermal liner extends the season, while waist straps and hook-and-loop hems dial in the fit and a short connection zipper secures it to your jacket so your lower back stays covered. Class AA certified with CE-level 2 SEEFLEX knee and CE-level 1 SEESMART hip armor, plus grip patches, a thigh cargo pocket, and reflective detailing. All-textile, no leather."),
 "Pants Outback 5 H2O": dict(action="create", protection="Highly protective", waterproof=HYD,
    riding=["Adventure / Touring"], season=["☀️ Summer","🌦 Mid season","❄️ Winter"],
    materials=["Polyester","Elastane (Elastic fabric)"],
    description="The fifth generation of REV'IT!'s long-running Outback adventure-touring pant, built on a tried-and-tested three-layer system with detachable thermal insulation and over-and-under hydratex waterproofing. New diagonally cut drop-down vents improve airflow, and stretch across the knees plus two waist buckles keep the fit secure but flexible. Class AA certified with top-tier CE-level 2 SEEFLEX knee and CE-level 1 SEESMART hip armor, plus reflective detailing. All-textile, no leather."),
}

def build_props(name, m):
    p = src[name]
    props = {
        "Name of product": {"title": [{"text": {"content": name}}]},
        "URL": {"url": p["url"]},
        "Brand": {"select": {"name": "REV'IT!"}},
        "Gender": {"multi_select": [{"name": g} for g in m.get("gender", ["Men"])]},
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

# Map existing Eclipse 2 page id for update
def find_pant_page(name):
    res = n.data_sources.query(data_source_id=DS, filter={"and": [
        {"property": "Brand", "select": {"equals": "REV'IT!"}},
        {"property": "Category", "multi_select": {"contains": "Pants"}},
    ]})
    for r in res["results"]:
        t = r["properties"]["Name of product"]["title"]
        nm = (t[0]["plain_text"] if t else "")
        if nm.strip().lower() == name.strip().lower():
            return r["id"]
    return None

created = updated = errors = 0
for name, m in MAP.items():
    try:
        props = build_props(name, m)
        if m["action"] == "update":
            pid = find_pant_page(name)
            if pid:
                n.pages.update(page_id=pid, properties=props)
                print(f"[UPDATED] {name}"); updated += 1
            else:
                n.pages.create(parent={"database_id": DB}, properties=props)
                print(f"[NOT FOUND -> CREATED] {name}"); created += 1
        else:
            n.pages.create(parent={"database_id": DB}, properties=props)
            print(f"[CREATED] {name}"); created += 1
    except Exception as e:
        print(f"[ERROR] {name}: {e}"); errors += 1
    time.sleep(0.4)

print(f"\nDone. created={created} updated={updated} errors={errors}")
