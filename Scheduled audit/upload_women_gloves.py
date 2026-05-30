"""Upload REV'IT! women's vegan gloves (maker-declared) to Notion.
Creates Access Ladies + Endo Ladies; updates existing Cavern women's entry."""
import os, time
from notion_client import Client

n = Client(auth=os.environ["NOTION_API_KEY"])
DB = os.environ["NOTION_PRODUCTS_DB_ID"]
DS = n.databases.retrieve(DB)["data_sources"][0]["id"]

PRODUCTS = [
    {
        "action": "create",
        "name": "Gloves Access Ladies",
        "url": "https://revitsport.com/en-us/products/en-motorcycles-gloves-access-ladies-black-white",
        "protection": "Slightly protective",
        "waterproof": "Not waterproof",
        "riding": ["Commute / Street", "Sport / Canyons"],
        "season": ["☀️ Summer"],
        "materials": ["Mesh fabric", "Microfiber", "Ethylene Vinyl Acetate"],
        "img": "https://cdn.shopify.com/s/files/1/0664/7912/8749/files/091224092249_83598068084643301.jpg?v=1745549950",
        "description": "An entry-level summer glove that keeps the essentials and skips the price tag. It's short-cuffed and fully ventilated, with 4-way stretch and a hook-and-loop cuff for an easy on-off and a snug fit on hot city rides. Protection comes from a thermopressed hard knuckle, EVA foam at the palm for impact absorption, and a microfiber palm with reinforced grip material. A straightforward, street-minded glove built from textile and synthetic materials, with no leather.",
    },
    {
        "action": "create",
        "name": "Gloves Endo Ladies",
        "url": "https://revitsport.com/en-us/products/en-motorcycles-gloves-endo-ladies-black-white",
        "protection": "Slightly protective",
        "waterproof": "Not waterproof",
        "riding": ["Commute / Street", "Sport / Canyons"],
        "season": ["☀️ Summer"],
        "materials": ["Mesh fabric", "Microfiber"],
        "img": "https://cdn.shopify.com/s/files/1/0664/7912/8749/files/091224092238_83598068084642714.jpg?v=1745549994",
        "description": "The women's-fit version of the Endo, built around airflow for warm-weather riding. Fully ventilated 3D air mesh on the back of the hand lets heat escape on stop-and-go rides, while the soft microfiber palm keeps a natural feel on the controls. It's CE level 1 certified, with a SEESOFT 3D knuckle that follows the shape of your hand and impact-absorbing foam underneath, plus OrthoLite palm padding for comfort over longer stints. Textile and synthetic throughout, with no leather.",
    },
    {
        "action": "update",
        "name": "Gloves Cavern Ladies",
        "url": "https://revitsport.com/en-us/products/en-motorcycles-gloves-cavern-ladies-black",
        "protection": "Slightly protective",
        "waterproof": "Not waterproof",
        "riding": ["Adventure / Touring", "Commute / Street"],
        "season": ["☀️ Summer"],
        "materials": ["Mesh fabric", "Microfiber"],
        "img": "https://cdn.shopify.com/s/files/1/0664/7912/8749/files/060125115606_83598068085065549_08fabc68-4b4a-48d8-959b-48922ac9b088.jpg?v=1745549763",
        "description": "The female-specific version of the Cavern, a short-cuff adventure glove made for hot-weather miles. It pairs 3D air mesh with microfiber and perforated panels so air moves through the hand instead of pooling inside, and stretch fabric between the fingers keeps it easy to flex on the bars. The armor is there without the bulk: memory-foam thumb protection, a SEESOFT knuckle plus middle and ring finger guards, and OrthoLite Ultralite foam at the wrist and palm. All-textile build, with no leather.",
    },
]

def build_props(p):
    props = {
        "Name of product": {"title": [{"text": {"content": p["name"]}}]},
        "URL": {"url": p["url"]},
        "Brand": {"select": {"name": "REV'IT!"}},
        "Gender": {"multi_select": [{"name": "Women"}]},
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
                    {"property": "Gender", "multi_select": {"contains": "Women"}},
                ]})
            pid = None
            for r in res["results"]:
                t = r["properties"]["Name of product"]["title"]
                nm = (t[0]["plain_text"] if t else "").lower()
                if "cavern" in nm:
                    pid = r["id"]; break
            if pid:
                n.pages.update(page_id=pid, properties=build_props(p))
                print(f"[UPDATED] {p['name']} ({pid})"); updated += 1
            else:
                n.pages.create(parent={"database_id": DB}, properties=build_props(p))
                print(f"[NOT FOUND -> CREATED] {p['name']}"); created += 1
        else:
            n.pages.create(parent={"database_id": DB}, properties=build_props(p))
            print(f"[CREATED] {p['name']}"); created += 1
    except Exception as e:
        print(f"[ERROR] {p['name']}: {e}"); errors += 1
    time.sleep(0.4)

print(f"\nDone. created={created} updated={updated} errors={errors}")
