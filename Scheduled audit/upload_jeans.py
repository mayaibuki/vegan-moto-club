"""
upload_jeans.py
Add the 22 maker-declared vegan REV'IT! jeans/chinos/leggings to Notion.
- Category -> "Pants" (no "Jeans" option in schema)
- Protection by CE class: A->Moderately, AA->Highly, AAA->Most protective
- Waterproof -> "Not waterproof" (riding denim is not waterproof)
- Strip leading category word from name (Jeans/Chino/Cargo/Worker/Leggings)
- "Moto 2 TF" updates the existing "Moto 2 Jeans" row instead of duplicating.
Dry-run unless APPLY=1.
"""
import os, re, json, time
from notion_client import Client

n = Client(auth=os.environ["NOTION_API_KEY"])
DB = os.environ["NOTION_PRODUCTS_DB_ID"]
DS = n.databases.retrieve(DB)["data_sources"][0]["id"]
APPLY = os.environ.get("APPLY") == "1"

HERE = os.path.dirname(__file__)
items = json.load(open(os.path.join(HERE, "jeans.json")))

PREFIXES = ("Jeans ", "Chino ", "Cargo ", "Worker ", "Leggings ")
DENIM = ["Denim", "Cordura®", "Elastane (Elastic fabric)"]
TWILL = ["Cordura®", "Elastane (Elastic fabric)"]          # Cordura Twill chinos/workers
KNIT  = ["Polyester", "Elastane (Elastic fabric)"]          # PWR Fleece/Shell/Interlock

# per-product overrides: materials + 1-line honest description.
# Anything not listed defaults to DENIM materials.
DETAIL = {
 "Cargo Brant Slim": (DENIM, "Slim-fit cargo trousers in garment-dyed CORDURA stretch denim, with webbing belt loops and plenty of pockets. CE Class A, with barely-there SEESMART knee armour and room to add hip protectors."),
 "Jeans Keegan Tapered": (DENIM, "Tapered five-pocket jeans in a lighter 13 oz CORDURA stretch denim that wears like ordinary denim. CE Class A with height-adjustable SEESMART knee armour; hip protectors optional."),
 "Jeans Moto 2 TF": (DENIM, "Tapered-fit riding jeans cut from CORDURA denim with a COOLMAX element for cooler wear. Stretch panels free up movement on the bike; CE Class AA with adjustable SEESMART knee armour."),
 "Jeans Carlin SK": (DENIM, "The narrowest, skinniest fit in the range, made from 12.5 oz CORDURA denim with plenty of stretch. CE Class A; SEESMART knee armour sits flat enough to disappear under the slim cut."),
 "Jeans Detroit 3 Tapered": (DENIM, "Single-layer tapered jeans in PWR|Hyperstretch CORDURA denim — very stretchy, yet still CE Class AA. SEESMART armour at both knees and hips comes included."),
 "Jeans Rilan TF": (DENIM, "Tapered jeans with a deliberately distressed, repaired-look finish, in 15.5 oz CORDURA stretch denim with COOLMAX and THERMOLITE. CE Class A with SEESMART knee armour; hips optional."),
 "Jeans Piston 3 Skinny": (DENIM, "Skinny mid-waist jeans in 16.7 oz CORDURA PWR|Hyperstretch denim with COOLMAX and THERMOLITE, built to hug close. CE Class AA with thin SEESMART knee armour; hips upgradeable."),
 "Chino Dean 2 Tapered": (TWILL, "Tapered chinos in CORDURA Twill — a non-denim option with tear and abrasion resistance. CE Class A; an extra deep front pocket keeps your phone secure, with reflective tape at the turn-up."),
 "Jeans Lewis Selvedge TF": (DENIM, "Tapered selvedge jeans in 13 oz CORDURA stretch denim that moulds to you over time. CE Class AA in a single layer, with SEESMART armour at knees and hips included."),
 "Jeans Lombard 3 RF": (DENIM, "Regular-fit everyday riding jeans in CORDURA denim with generous stretch so they stay comfortable on and off the bike. CE Class AA with adjustable SEESMART knee armour."),
 "Jeans Cargo 2 TF": (DENIM, "Cargo-styled tapered jeans in a lighter 13.5 oz CORDURA stretch twill, with large slanted thigh pockets that open easily with gloves on. Single-layer CE Class A."),
 "Jeans Micah TF": (DENIM, "Tapered jeans rated to the top CE Class AAA, built from 16 oz CORDURA denim with PWR|Shield reinforcement at hips, seat and knees plus SEESMART armour at knees and hips."),
 "Chino Mason Slim": (KNIT, "Slim chinos in PWR|Fleece with a jogger feel and a flat hidden waist elastic. CE Class A; a dedicated phone pocket and a side-seam reflective strip add everyday practicality."),
 "Worker Davis 2 Regular": (TWILL, "Regular-fit worker trousers in CORDURA Twill with tear and abrasion resistance. CE Class A; a deep extra front pocket and reflective turn-up tape round out the practical, classic cut."),
 "Jeans Ortes TF": (DENIM, "Timeless tapered five-pocket jeans in 15.5 oz CORDURA stretch denim with COOLMAX and THERMOLITE for multi-season wear. Single-layer CE Class AA with SEESMART knee and hip armour."),
 "Chino Terry Skinny": (["Polyester", "Nylon", "Elastane (Elastic fabric)"], "Lightweight skinny chinos in four-way-stretch PWR|Shell ripstop with a utilitarian thigh stash pocket. CE Class A with height-adjustable SEESMART knee armour; hips optional."),
 "Leggings Ellison 2 Ladies": (KNIT, "High-waisted ride-ready leggings in stretchy PWR|Interlock knit with a connection zip for your jacket. CE Class AA with thin, flexible SEESMART armour at knees and hips included."),
 "Leggings Talia Ladies": (KNIT, "Sporty high-rise leggings in soft PWR|Interlock knit with pull loops and a body-hugging waistband. CE Class A with barely-noticeable SEESMART knee armour; hips upgradeable."),
 "Jeans Harper Tapered Ladies": (DENIM, "REV'IT!'s first women's jeans rated to the top CE Class AAA — tapered, mid-waist, in 16 oz CORDURA stretch denim with PWR|Shield reinforcement and SEESMART armour at knees and hips."),
 "Jeans Violet Ladies BF": (DENIM, "Boyfriend-fit women's jeans with a roomier hip and thigh and a tapered ankle, in 15.5 oz CORDURA stretch denim with COOLMAX and THERMOLITE. Single-layer CE Class AA with SEESMART knee and hip armour."),
 "Jeans Marzia Skinny Ladies": (DENIM, "Budget-friendly skinny women's jeans in 13 oz CORDURA stretch denim, with a fit tuned for a range of body shapes. CE Class A with SEESMART knee armour; hip protectors optional."),
 "Jeans Shelby 3 Skinny Ladies": (DENIM, "Skinny mid-waist women's jeans in 16.7 oz CORDURA PWR|Hyperstretch denim with COOLMAX and THERMOLITE. CE Class AA with thin SEESMART knee armour; hips upgradeable."),
}

CLASS_PROT = {"AAA": "Most protective", "AA": "Highly protective", "A": "Moderately protective"}

def ce_class(tags):
    for t in tags:
        m = re.match(r"Class (A+) certified", t)
        if m: return m.group(1)
    return "A"

def strip_name(name):
    for pre in PREFIXES:
        if name.startswith(pre):
            return name[len(pre):].strip()
    return name.strip()

def seasons(item):
    blob = (item["body"] + " " + " ".join(item["tags"])).upper()
    if "THERMOLITE" in blob and "COOLMAX" in blob:
        return ["☀️ Summer", "🌦 Mid season", "❄️ Winter"]
    return ["☀️ Summer", "🌦 Mid season"]

def build_props(item):
    raw = item["name"]
    name = strip_name(raw)
    mats, desc = DETAIL.get(raw, (DENIM, ""))
    prot = CLASS_PROT[ce_class(item["tags"])]
    gender = "Women" if item["gender"] == "women" else "Men"
    props = {
        "Name of product": {"title": [{"text": {"content": name}}]},
        "URL": {"url": item["url"]},
        "Brand": {"select": {"name": "REV'IT!"}},
        "Gender": {"multi_select": [{"name": gender}]},
        "Category": {"multi_select": [{"name": "Pants"}]},
        "Level of Protection": {"select": {"name": prot}},
        "Level of Waterproof": {"select": {"name": "Not waterproof"}},
        "Riding style": {"multi_select": [{"name": "Commute / Street"}]},
        "Season": {"multi_select": [{"name": s} for s in seasons(item)]},
        "Materials": {"multi_select": [{"name": m} for m in mats]},
        "Vegan Verified": {"select": {"name": "Confirmed Vegan by maker"}},
        "Description": {"rich_text": [{"text": {"content": desc}}]},
    }
    if item.get("img"):
        props["Photos"] = {"files": [{"type": "external", "name": name, "external": {"url": item["img"]}}]}
    return name, props

# find existing "Moto 2 Jeans" to update instead of duplicating
def find_row(title_exact):
    r = n.data_sources.query(data_source_id=DS, filter={
        "property": "Name of product", "title": {"equals": title_exact}})
    return r["results"][0] if r["results"] else None

moto2_existing = find_row("Moto 2 Jeans")

created = updated = 0
for item in items:
    name, props = build_props(item)
    if item["name"] == "Jeans Moto 2 TF" and moto2_existing:
        print(f"UPDATE existing 'Moto 2 Jeans' -> '{name}'  [{props['Level of Protection']['select']['name']}]")
        updated += 1
        if APPLY:
            n.pages.update(page_id=moto2_existing["id"], properties=props)
            time.sleep(0.4)
        continue
    print(f"CREATE [{item['gender']:5}] {name}  [{props['Level of Protection']['select']['name']}]  "
          f"mats={[m['name'] for m in props['Materials']['multi_select']]}  "
          f"season={[s['name'] for s in props['Season']['multi_select']]}")
    created += 1
    if APPLY:
        n.pages.create(parent={"database_id": DB}, properties=props)
        time.sleep(0.4)

print(f"\n{'APPLIED' if APPLY else 'DRY-RUN'}: {created} create, {updated} update")
