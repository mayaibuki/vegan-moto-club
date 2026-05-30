"""Upload REV'IT! men's vegan gloves (maker-declared) to Notion.
Creates Endo + Tacto; updates existing Gloves Cavern entry."""
import os, time
from notion_client import Client

n = Client(auth=os.environ["NOTION_API_KEY"])
DB = os.environ["NOTION_PRODUCTS_DB_ID"]
DS = n.databases.retrieve(DB)["data_sources"][0]["id"]

PRODUCTS = [
    {
        "action": "create",
        "name": "Gloves Endo",
        "url": "https://revitsport.com/en-us/products/en-motorcycles-gloves-endo-black-sand",
        "protection": "Slightly protective",
        "waterproof": "Not waterproof",
        "riding": ["Commute / Street", "Sport / Canyons"],
        "season": ["☀️ Summer"],
        "materials": ["Mesh fabric", "Microfiber"],
        "img": "https://cdn.shopify.com/s/files/1/0664/7912/8749/files/021225114048_83598068085261785.jpg?v=1767241493",
        "description": "A warm-weather city glove built around airflow. The back of the hand is fully ventilated 3D air mesh, so heat escapes instead of building up on stop-and-go rides, while the microfiber palm stays soft and keeps a natural feel on the controls. Protection isn't an afterthought: it's CE level 1 certified, with a SEESOFT 3D knuckle that follows the shape of your hand and impact-absorbing foam underneath. OrthoLite foam at the palm adds comfort over longer stints. Built from textile and synthetic materials throughout, with no leather.",
    },
    {
        "action": "create",
        "name": "Gloves Tacto",
        "url": "https://revitsport.com/en-us/products/en-motorcycles-gloves-tacto-sand",
        "protection": "Not protective",
        "waterproof": "Not waterproof",
        "riding": ["Off-roading"],
        "season": ["☀️ Summer"],
        "materials": ["Mesh fabric", "Microfiber", "Elastane (Elastic fabric)"],
        "img": "https://cdn.shopify.com/s/files/1/0664/7912/8749/files/080725112621_83598068085242997.jpg?v=1755262635",
        "description": "A stripped-back, off-road glove for riders who want maximum feel with minimal weight. The build is deliberately thin: a stretch textile outer, a microfiber palm, and breathable mesh between the fingers, so you keep a direct connection to the clutch, brake, and bars. This is a minimalist design with little to no padding, aimed at off-road feel rather than impact protection, so go in knowing that's the trade-off. Textile and synthetic throughout, with no leather.",
    },
    {
        "action": "update",
        "name": "Gloves Cavern",
        "match_url_contains": "cavern",
        "url": "https://revitsport.com/en-us/products/en-motorcycles-gloves-cavern-sand-black",
        "protection": "Slightly protective",
        "waterproof": "Not waterproof",
        "riding": ["Adventure / Touring", "Commute / Street"],
        "season": ["☀️ Summer"],
        "materials": ["Mesh fabric", "Microfiber"],
        "img": "https://cdn.shopify.com/s/files/1/0664/7912/8749/files/060125115601_83598068085065196.jpg?v=1745549496",
        "description": "A short-cuff adventure glove made for hot-weather miles. It pairs 3D air mesh with microfiber and perforated panels so air moves through the hand instead of pooling inside, and stretch fabric between the fingers keeps it easy to flex on the bars. The armor is there without the bulk: memory-foam thumb protection, a SEESOFT knuckle plus middle and ring finger guards, and OrthoLite Ultralite foam at the wrist and palm. All-textile build, with no leather.",
    },
]

def build_props(p):
    props = {
        "Name of product": {"title": [{"text": {"content": p["name"]}}]},
        "URL": {"url": p["url"]},
        "Brand": {"select": {"name": "REV'IT!"}},
        "Gender": {"multi_select": [{"name": "Men"}]},
        "Category": {"multi_select": [{"name": "Gloves"}]},
        "Level of Protection": {"select": {"name": p["protection"]}},
        "Level of Waterproof": {"select": {"name": p["waterproof"]}},
        "Riding style": {"multi_select": [{"name": s} for s in p["riding"]]},
        "Season": {"multi_select": [{"name": s} for s in p["season"]]},
        "Materials": {"multi_select": [{"name": m} for m in p["materials"]]},
        "Vegan Verified": {"select": {"name": "Confirmed Vegan by maker"}},
        "Description": {"rich_text": [{"text": {"content": p["description"]}}]},
    }
    if p.get("img"):
        props["Photos"] = {"files": [{"type": "external", "name": p["name"], "external": {"url": p["img"]}}]}
    return props

created = updated = errors = 0
for p in PRODUCTS:
    try:
        if p["action"] == "update":
            res = n.data_sources.query(data_source_id=DS, filter={
                "and": [
                    {"property": "Brand", "select": {"equals": "REV'IT!"}},
                    {"property": "Category", "multi_select": {"contains": "Gloves"}},
                ]})
            pid = None; fallback = None
            for r in res["results"]:
                t = r["properties"]["Name of product"]["title"]
                nm = (t[0]["plain_text"] if t else "").lower()
                u = (r["properties"].get("URL", {}).get("url") or "").lower()
                if "cavern" in nm or "cavern" in u:
                    if "revitsport" in u:
                        pid = r["id"]; break
                    fallback = fallback or r["id"]
            pid = pid or fallback
            if pid:
                n.pages.update(page_id=pid, properties=build_props(p))
                print(f"[UPDATED] {p['name']} ({pid})")
                updated += 1
            else:
                print(f"[NOT FOUND for update] {p['name']} -> creating instead")
                n.pages.create(parent={"database_id": DB}, properties=build_props(p))
                created += 1
        else:
            n.pages.create(parent={"database_id": DB}, properties=build_props(p))
            print(f"[CREATED] {p['name']}")
            created += 1
    except Exception as e:
        print(f"[ERROR] {p['name']}: {e}")
        errors += 1
    time.sleep(0.4)

print(f"\nDone. created={created} updated={updated} errors={errors}")
