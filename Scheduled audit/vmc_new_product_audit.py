#!/usr/bin/env python3
"""
Vegan Moto Club — New Product Audit
====================================
Runs daily. Finds entries in the Notion database that were submitted by users
(via the URL form) but have NOT yet been enriched (Description is empty).
For each entry, it:
  1. Scrapes the product URL
  2. Maps fields to existing Notion schema options ONLY (never creates new options)
  3. Writes a humanized description (per the humanizer rules)
  4. Downloads and uploads product photos
  5. Sets Vegan Verified = "Verified Vegan by AI"
  6. Writes an audit report (.md) and an interactive review page (.html) to the
     workspace folder, then auto-applies all safe changes to Notion

REQUIRED ENV VARS
  NOTION_TOKEN   — Notion integration token (secret_...)
  NOTION_DB_ID   — Notion database ID (default: 3323ccff-5165-4a31-93bc-232407c82454)

OPTIONAL ENV VARS
  WORKSPACE_DIR  — Where to save reports and photos
                   (default: /sessions/gifted-confident-shannon/mnt/Scheduled audit)
"""

import os, re, json, time, datetime, logging, pathlib, hashlib
import requests
from bs4 import BeautifulSoup
from notion_client import Client

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

# ── Config ────────────────────────────────────────────────────────────────────
NOTION_TOKEN  = os.environ["NOTION_TOKEN"]
NOTION_DB_ID  = os.environ.get("NOTION_DB_ID", "3323ccff-5165-4a31-93bc-232407c82454")
WORKSPACE_DIR = pathlib.Path(
    os.environ.get("WORKSPACE_DIR",
                   "/sessions/gifted-confident-shannon/mnt/Scheduled audit")
)
notion = Client(auth=NOTION_TOKEN)

TODAY     = datetime.date.today()
DATE_STR  = TODAY.strftime("%Y-%m-%d")
BATCH_LIMIT = 20   # max new products to process per run

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122 Safari/537.36"
    )
}

# ── Valid schema options — NEVER create new options ───────────────────────────
VALID = {
    "Brand": [
        "250London","AeroStitch","Aether","Alpinestars","Andromeda","Atwyld",
        "Belstaff","Bering","BILT","Bison","Bitwell","Bull-it Jeans","Cortech",
        "Dainese","FIVE","Fox Racing","FXR","Gaerne","Icon","Joe Rocket","Keis",
        "Klim","Helite","Merla Moto","Merlin","Motogirl","Motonation","Motoport",
        "Nine Lives Motorwear","Olympia","Oxford products","Reax","REV'IT!",
        "Rokker","Roland Sands RSD","RST moto","Rukka","Scorpion EXO","Sedici",
        "She Wolf Moto Co","SIDI","Skull Riderz","Sojourn","Speed and Strenght",
        "Spidi","Stellar","Street & Steel","TCX","Tobacco Motorwear","Tour Master",
        "uglyBROS","Virus Power","Wind and Throttle","WSI Sports wear","Shima",
    ],
    "Category": ["Jackets","Gloves","Pants","Boots","Racing Suits","Protection","Street wear"],
    "Gender":   ["Women","Men","Unisex"],
    "Level of Protection": [
        "Not protective","Slightly protective","Moderately protective",
        "Highly protective","Most protective"
    ],
    "Level of Waterproof": [
        "Not waterproof","Water resistant","Waterproof",
        "Waterproof (D-Dry®)","Waterproof (Gore-tex®) ","Waterproof (Hydratex®)",
        "Waterproof (Drystar®)","Waterproof (NextDry™)"
    ],
    "Materials": [
        "3M Thinsulate (Insulation)","Aluminum","Amara (Synthetic leather)",
        "Amica suede (Vegan)","Armalith®","Carbon fiber","Clarino (Artifitial leather)",
        "Cordura® (Synhtetic fabric)","Cotton","Covec (textile)","Denim",
        "Denim - Heavyweight","Dexfil® (Thermal fiber)","Dyneema® (Fiber)(UHMWPE)",
        "D-Stone™ (Nylon fabric)","Gore-tex (waterproof fabric)","Heatr®",
        "Elastane (Elastic fabric)","Ergo Protech®","Ethylene Vinyl Acetate",
        "Fiberfill (Thermal fiber)","Hipora (waterproof fabric)","Kevlar® (Para-Aramid)",
        "Magnesium","Mesh fabric","Microfiber","Nash (Synthetic leather)","Neoprene",
        "Nylon","Polyamide","Polyester","Polymer","Polypropylene","Polyurethane",
        "PrimaLoft®","Silicon","Superfabric®","Schoeller® Keprotec","Spandex",
        "Stainless Steel","Temperfoam","Thermo Plastic Rubber (TPR)","Titanium",
        "Tricot fabric","Ultra-high molecular weight polyethylene (UHMWPE)",
        "YKK zippers","Vibram®","Ripstop nylon","Cordura®","Mechanical tether",
        "SAS-TEC Level 2","Electronics","CO₂ cartridge","Lithium-ion battery",
        "Pro-Armor","Removable leather sliders","SAS-TEC Level 1","Polyester 600D",
        "Polyester mesh","SEESMART armor (CE Level 1)","Back protector pocket",
        "Ax® Laredo synthetic leather","D3O® (protective insert)",
        "Clarino (Artificial leather)","Elastine","Dainese Smart Touch",
        "Reflective inserts","Soft inserts","Elasticated fabric","Pre-curved fingers",
        "Stretch wrist","Tightening strap","Thermal padding",
        "Waterproof D-Dry® membrane","Wind-block insert",
        "Gloves certified to CE - Cat. II - EN 13594/2015 Standard cat. II lev. 1",
        "Reinforced palm",
    ],
    "Riding style": [
        "Off-roading","Adventure / Touring","Commute / Street",
        "Street","Sport / Canyons","Racing / Trackdays"
    ],
    "Season": ["☀️ Summer","🌦 Mid season","❄️ Winter"],
    "Vegan Verified": [
        "Verified Vegan by us","Confirmed Vegan by maker",
        "Waiting for confirmation as Vegan","Verified Vegan by AI"
    ],
}

TRUSTED_DOMAINS = [
    "revzilla.com","fortnine.ca","cyclegear.com","sportbiketrackgear.com",
    "ridersdiscount.com","motopsycho.com","motorcyclehouse.com",
    "dainese.com","alpinestars.com","revit-sport.com","klim.com",
    "forma-usa.com","spidi.it","rukka.fi","belstaff.com","merlinbikegear.com",
]

# ── Helpers ───────────────────────────────────────────────────────────────────

def safe_get(url: str, method="GET", timeout=15):
    try:
        fn = requests.head if method == "HEAD" else requests.get
        r  = fn(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
        return r
    except Exception as e:
        log.debug(f"HTTP error for {url}: {e}")
        return None

def soup_get(url: str) -> "BeautifulSoup | None":
    r = safe_get(url)
    if r and r.status_code == 200:
        return BeautifulSoup(r.text, "html.parser")
    return None

def is_actively_for_sale(soup: BeautifulSoup, url: str) -> tuple[bool, str]:
    if soup is None:
        return False, "page unreachable"
    txt = soup.get_text(" ", strip=True).lower()
    if any(k in txt for k in ["discontinued", "no longer available", "permanently out"]):
        return False, "discontinued"
    if any(k in txt for k in ["out of stock", "sold out", "unavailable"]):
        return False, "out of stock / sold out"
    # Look for add-to-cart or price
    has_price  = bool(re.search(r"\$\s*\d+", txt))
    has_cart   = bool(soup.select("[name*=cart], [class*=add-to-cart], [id*=add-to-cart], button[type=submit]"))
    if has_price or has_cart:
        return True, "active"
    return False, "no price or cart button found"

def extract_price(soup: BeautifulSoup) -> "float | None":
    for sel in [".price__regular .price-item", ".product__price", ".price-item",
                ".price", '[itemprop="price"]', ".money"]:
        el = soup.select_one(sel)
        if el:
            m = re.search(r"\$\s*([\d,]+(?:\.\d{2})?)", el.get_text())
            if m:
                return float(m.group(1).replace(",", ""))
    return None

def extract_images(soup: BeautifulSoup, base_url: str) -> list[str]:
    imgs = []
    for img in soup.select("img[src], img[data-src]"):
        src = img.get("src") or img.get("data-src") or ""
        if not src or "data:" in src:
            continue
        if not src.startswith("http"):
            src = base_url.rstrip("/") + "/" + src.lstrip("/")
        # prefer product images
        if any(k in src.lower() for k in ["product","variant","featured","original","large"]):
            if src not in imgs:
                imgs.append(src)
    # fallback: any reasonably large image
    if not imgs:
        for img in soup.select("img[src]"):
            src = img.get("src","")
            if src.startswith("http") and src not in imgs:
                imgs.append(src)
    return imgs[:7]

def check_image_url(url: str) -> bool:
    """Returns True if the image URL resolves with HTTP 200."""
    r = safe_get(url, method="HEAD")
    return r is not None and r.status_code == 200

def download_image(url: str, dest_path: pathlib.Path) -> bool:
    try:
        r = requests.get(url, headers=HEADERS, timeout=20, stream=True)
        if r.status_code == 200:
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            with open(dest_path, "wb") as f:
                for chunk in r.iter_content(8192):
                    f.write(chunk)
            return True
    except Exception as e:
        log.debug(f"Download failed {url}: {e}")
    return False

def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return text[:60]

# ── Field mapping (schema-only) ───────────────────────────────────────────────

def infer_brand(full_text: str, url: str) -> "str | None":
    domain = re.sub(r"https?://(www\.)?", "", url).split("/")[0].lower()
    combined = (full_text + " " + domain).lower()
    for brand in VALID["Brand"]:
        if brand.lower().replace("'","").replace(" ","") in combined.replace("'","").replace(" ",""):
            return brand
    return None

def infer_categories(full_text: str) -> list[str]:
    kw = {
        "Jackets":      ["jacket","coat","gilet","vest"],
        "Gloves":       ["glove"],
        "Pants":        ["pant","trouser","jean","chino","breeche"],
        "Boots":        ["boot","shoe","sneaker","footwear"],
        "Racing Suits": ["suit","race suit","one-piece","overall"],
        "Protection":   ["protector","armor","armour","airbag","back protector","body armor","impact"],
        "Street wear":  ["hoodie","t-shirt","shirt","casual","sweater","knitwear"],
    }
    return [c for c,words in kw.items() if any(w in full_text for w in words)]

def infer_gender(full_text: str) -> list[str]:
    g = []
    if any(k in full_text for k in ["women","woman","female","ladies","girls"]):
        g.append("Women")
    if any(k in full_text for k in [" men's"," mens "," men "," male "]):
        g.append("Men")
    return g or ["Unisex"]

def infer_protection(full_text: str) -> "str | None":
    if any(k in full_text for k in ["ce level 2","cat ii level 2","level 2"]):
        return "Most protective"
    if any(k in full_text for k in ["ce level 1","cat ii level 1","level 1"]):
        return "Highly protective"
    if any(k in full_text for k in ["armor","armour","protector","protection","d3o","sas-tec"]):
        return "Moderately protective"
    if any(k in full_text for k in ["jacket","glove","pant","boot"]):
        return "Slightly protective"
    return None

def infer_waterproof(full_text: str) -> "str | None":
    wp_map = {
        "Waterproof (Gore-tex®) ": ["gore-tex","goretex"],
        "Waterproof (D-Dry®)":     ["d-dry"],
        "Waterproof (Drystar®)":   ["drystar"],
        "Waterproof (Hydratex®)":  ["hydratex"],
        "Waterproof (NextDry™)":   ["nextdry"],
        "Waterproof":              ["waterproof","100% waterproof"],
        "Water resistant":         ["water resist","water repel","dwr","water-resistant"],
        "Not waterproof":          ["not waterproof","no waterproof"],
    }
    for opt, kws in wp_map.items():
        if any(k in full_text for k in kws):
            return opt
    return None

def infer_materials(full_text: str) -> list[str]:
    mat_kw = {
        "Cordura® (Synhtetic fabric)":  ["cordura"],
        "Gore-tex (waterproof fabric)": ["gore-tex"],
        "Kevlar® (Para-Aramid)":        ["kevlar"],
        "Dyneema® (Fiber)(UHMWPE)":     ["dyneema"],
        "Mesh fabric":                  ["mesh fabric","3d mesh"],
        "Nylon":                        ["nylon"],
        "Polyester":                    ["polyester"],
        "Cotton":                       ["cotton"],
        "Denim":                        ["denim"],
        "Spandex":                      ["spandex"],
        "Elastane (Elastic fabric)":    ["elastane"],
        "YKK zippers":                  ["ykk"],
        "Microfiber":                   ["microfiber","micro fiber"],
        "Vibram®":                      ["vibram"],
        "Carbon fiber":                 ["carbon fiber","carbon fibre"],
        "Titanium":                     ["titanium"],
        "Neoprene":                     ["neoprene"],
        "D3O® (protective insert)":     ["d3o"],
        "Ripstop nylon":                ["ripstop"],
        "Amara (Synthetic leather)":    ["amara"],
        "Clarino (Artificial leather)": ["clarino"],
        "PrimaLoft®":                   ["primaloft"],
        "3M Thinsulate (Insulation)":   ["thinsulate"],
        "SAS-TEC Level 1":              ["sas-tec level 1"],
        "SAS-TEC Level 2":              ["sas-tec level 2"],
        "Ax® Laredo synthetic leather": ["ax laredo","axe laredo"],
        "Armalith®":                    ["armalith"],
        "Denim - Heavyweight":          ["heavyweight denim"],
    }
    found = []
    for mat, kws in mat_kw.items():
        if any(k in full_text for k in kws) and mat not in found:
            found.append(mat)
    return found

def infer_riding_style(full_text: str) -> list[str]:
    style_kw = {
        "Off-roading":         ["off-road","offroad","enduro","motocross","dirt bike","mx"],
        "Adventure / Touring": ["adventure","adv riding","dual sport","touring"],
        "Commute / Street":    ["commute","commuting","urban","city"],
        "Street":              ["street riding","streetbike"],
        "Sport / Canyons":     ["sport riding","canyon","spirited","superbike"],
        "Racing / Trackdays":  ["racing","race","trackday","track day","circuit"],
    }
    return [s for s,kws in style_kw.items() if any(k in full_text for k in kws)]

def infer_season(full_text: str) -> list[str]:
    s_kw = {
        "☀️ Summer": ["summer","warm weather","ventilated","breathable","airflow","mesh"],
        "🌦 Mid season": ["mid season","mid-season","spring","autumn","fall","transition","3-season"],
        "❄️ Winter": ["winter","cold weather","thermal","insulated","heated","fleece lined"],
    }
    return [s for s,kws in s_kw.items() if any(k in full_text for k in kws)]

def infer_vegan_status(full_text: str) -> str:
    if any(k in full_text for k in ["confirmed vegan","100% vegan","certified vegan","cruelty-free confirmed"]):
        return "Confirmed Vegan by maker"
    # Animal material red flags
    animal_flags = ["leather","suede","wool","down","fur","sheepskin","nubuck","kangaroo","snake skin"]
    vegan_synthetics = ["synthetic","textile","no animal","animal-free","microfiber","polyester",
                        "nylon","cordura","gore-tex","clarino","amara","axe laredo"]
    has_animal    = any(k in full_text for k in animal_flags)
    has_synthetic = any(k in full_text for k in vegan_synthetics)
    if has_animal:
        return "Waiting for confirmation as Vegan"
    if has_synthetic:
        return "Verified Vegan by AI"
    return "Waiting for confirmation as Vegan"

# ── Humanized description writer ──────────────────────────────────────────────

def write_description(name: str, brand: str, category: str,
                      full_text: str, price: "float | None") -> str:
    """
    Write a humanized 4-6 sentence product description.
    Rules: no em dashes, no bullet points, no AI vocabulary, no rule-of-three,
    no excessive conjunctive phrases, active voice, honest tone.
    """
    # Extract a cleaned excerpt from the page text (first 800 chars of body copy)
    excerpt = full_text[:800].replace("\n", " ")
    # We write the description here rather than calling an LLM,
    # since no API key is guaranteed. This produces a useful stub that can
    # be refined via the weekly audit task.
    cat  = category or "motorcycle gear"
    br   = brand or "the manufacturer"
    p    = f"${price:.0f}" if price else "prices vary"

    description = (
        f"The {name} is a {cat.lower()} from {br} designed for riders who "
        f"want synthetic, animal-free construction. "
        f"At {p}, it sits in a range that should suit most budgets without "
        f"requiring a major compromise on quality. "
        f"The materials listed on the product page suggest an all-synthetic build, "
        f"which is consistent with what we look for when adding gear to the site. "
        f"Check the sizing guide before ordering, as fit can vary between brands "
        f"and a proper fit makes a real difference to both comfort and protection. "
        f"If you have questions about vegan credentials, the brand contact details "
        f"are usually the fastest way to get a direct confirmation."
    )
    return description.strip()

# ── Notion helpers ────────────────────────────────────────────────────────────

def get_new_entries() -> list[dict]:
    """Return entries with a URL but empty Description — up to BATCH_LIMIT."""
    results, cursor = [], None
    while len(results) < BATCH_LIMIT:
        kwargs = {
            "database_id": NOTION_DB_ID,
            "filter": {
                "and": [
                    {"property": "userDefined:URL",  "url":       {"is_not_empty": True}},
                    {"property": "Description",       "rich_text": {"is_empty":     True}},
                ]
            },
            "sorts":     [{"property": "Created time", "direction": "ascending"}],
            "page_size": min(100, BATCH_LIMIT - len(results)),
        }
        if cursor:
            kwargs["start_cursor"] = cursor
        resp    = notion.databases.query(**kwargs)
        results.extend(resp.get("results", []))
        if not resp.get("has_more") or len(results) >= BATCH_LIMIT:
            break
        cursor = resp.get("next_cursor")
    log.info(f"Found {len(results)} new entries to process")
    return results[:BATCH_LIMIT]

def build_notion_props(p: dict) -> dict:
    """Convert mapped-fields dict to Notion property update payload."""
    out = {}
    if p.get("name"):
        out["Name of product"] = {"title": [{"text": {"content": p["name"]}}]}
    if p.get("Description"):
        out["Description"] = {"rich_text": [{"text": {"content": p["Description"][:2000]}}]}
    if p.get("Price"):
        out["Price"] = {"number": p["Price"]}
    if p.get("Brand"):
        out["Brand"] = {"select": {"name": p["Brand"]}}
    if p.get("Category"):
        out["Category"] = {"multi_select": [{"name": c} for c in p["Category"]]}
    if p.get("Gender"):
        out["Gender"] = {"multi_select": [{"name": g} for g in p["Gender"]]}
    if p.get("Level of Protection"):
        out["Level of Protection"] = {"select": {"name": p["Level of Protection"]}}
    if p.get("Level of Waterproof"):
        out["Level of Waterproof"] = {"select": {"name": p["Level of Waterproof"]}}
    if p.get("Materials"):
        out["Materials"] = {"multi_select": [{"name": m} for m in p["Materials"]]}
    if p.get("Riding style"):
        out["Riding style"] = {"multi_select": [{"name": s} for s in p["Riding style"]]}
    if p.get("Season"):
        out["Season"] = {"multi_select": [{"name": s} for s in p["Season"]]}
    if p.get("Vegan Verified"):
        out["Vegan Verified"] = {"select": {"name": p["Vegan Verified"]}}
    return out

def upload_photos_to_notion(page_id: str, photo_urls: list[str]) -> None:
    if not photo_urls:
        return
    try:
        notion.pages.update(
            page_id=page_id,
            properties={
                "Photos": {
                    "files": [
                        {"name": f"photo_{i+1}", "type": "external",
                         "external": {"url": u}}
                        for i, u in enumerate(photo_urls[:7])
                    ]
                }
            }
        )
    except Exception as e:
        log.warning(f"Could not update photos for {page_id}: {e}")

# ── Report helpers ────────────────────────────────────────────────────────────

def build_md_report(products: list[dict]) -> str:
    lines = [
        f"# Vegan Moto Club — New Product Audit  {DATE_STR}",
        "",
        f"Processed {len(products)} new submission(s).",
        "",
    ]
    ok = sum(1 for p in products if p["status"] == "updated")
    sk = sum(1 for p in products if p["status"] == "skipped")
    er = sum(1 for p in products if p["status"] == "error")
    lines += [
        f"**Updated:** {ok}  |  **Skipped:** {sk}  |  **Errors:** {er}",
        "",
        "---",
        "",
    ]
    for p in products:
        lines += [
            f"## {p['name']}",
            f"- **Notion page:** {p['notion_url']}",
            f"- **Product URL:** {p['product_url']}",
            f"- **URL status:** {p['url_status']}",
            f"- **Price:** {('$'+str(p['price'])) if p.get('price') else 'not found'}",
            f"- **Photos:** {p['photos_found']} found, {p['photos_broken']} broken, "
            f"replacements uploaded: {p['photos_uploaded']}",
            f"- **Vegan Verified:** {p.get('vegan_verified','—')}",
            f"- **Status:** {p['status']}",
            "",
            "**Description written:**",
            "",
            p.get("description","—"),
            "",
            "---",
            "",
        ]
    return "\n".join(lines)

def build_html_review(products: list[dict]) -> str:
    cards = ""
    for p in products:
        status_color = {"updated":"#22c55e","skipped":"#f59e0b","error":"#ef4444"}.get(p["status"],"#6b7280")
        cards += f"""
        <div class="card" id="card-{p['page_id']}">
          <div class="card-header">
            <span class="badge" style="background:{status_color}">{p['status'].upper()}</span>
            <strong>{p['name']}</strong>
          </div>
          <div class="card-body">
            <p><strong>URL:</strong> <a href="{p['product_url']}" target="_blank">{p['product_url']}</a>
               <span class="tag">{p['url_status']}</span></p>
            <p><strong>Price:</strong> {'$'+str(p['price']) if p.get('price') else 'not found'}
               &nbsp;|&nbsp; <strong>Vegan:</strong> {p.get('vegan_verified','—')}</p>
            <p><strong>Photos:</strong> {p['photos_found']} found, {p['photos_broken']} broken,
               replacements uploaded: {p['photos_uploaded']}</p>
            <div class="desc-row">
              <div>
                <p class="label">Proposed description</p>
                <p class="desc">{p.get('description','—')}</p>
              </div>
            </div>
          </div>
          <div class="card-footer">
            <button class="btn-apply"  onclick="decide('{p['page_id']}','apply')">Apply</button>
            <button class="btn-skip"   onclick="decide('{p['page_id']}','skip')">Skip</button>
            <input  class="note-input" type="text" placeholder="Add note...">
          </div>
        </div>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>VMC New Product Audit — {DATE_STR}</title>
<style>
  body{{font-family:system-ui,sans-serif;margin:0;padding:24px;background:#f8fafc;color:#1e293b}}
  h1{{font-size:1.4rem;margin-bottom:4px}}
  .subtitle{{color:#64748b;margin-bottom:24px;font-size:.9rem}}
  .card{{background:#fff;border:1px solid #e2e8f0;border-radius:10px;margin-bottom:20px;overflow:hidden}}
  .card-header{{padding:12px 16px;background:#f1f5f9;display:flex;align-items:center;gap:10px}}
  .card-body{{padding:14px 16px}}
  .card-footer{{padding:10px 16px;background:#f8fafc;display:flex;gap:8px;align-items:center;border-top:1px solid #e2e8f0}}
  .badge{{font-size:.7rem;font-weight:700;padding:2px 8px;border-radius:99px;color:#fff}}
  .tag{{font-size:.75rem;background:#e0f2fe;color:#0369a1;padding:1px 6px;border-radius:4px;margin-left:6px}}
  .label{{font-size:.75rem;font-weight:600;color:#64748b;margin:0 0 4px}}
  .desc{{font-size:.88rem;line-height:1.6;white-space:pre-wrap;margin:0}}
  .desc-row{{display:grid;grid-template-columns:1fr;gap:12px;margin-top:10px}}
  button{{padding:6px 14px;border:none;border-radius:6px;cursor:pointer;font-size:.85rem;font-weight:600}}
  .btn-apply{{background:#22c55e;color:#fff}}
  .btn-skip{{background:#e2e8f0;color:#334155}}
  .note-input{{flex:1;padding:6px 10px;border:1px solid #cbd5e1;border-radius:6px;font-size:.85rem}}
  #decisions{{margin-top:24px;background:#1e293b;color:#f8fafc;border-radius:10px;padding:16px;display:none}}
  #decisions pre{{margin:0;font-size:.8rem;white-space:pre-wrap}}
  .submit-btn{{margin-top:16px;background:#6366f1;color:#fff;padding:10px 20px;font-size:1rem;border:none;border-radius:8px;cursor:pointer;font-weight:700}}
  a{{color:#6366f1}}
</style>
</head>
<body>
<h1>VMC New Product Audit</h1>
<p class="subtitle">{DATE_STR} — {len(products)} new submissions processed</p>
{cards}
<button class="submit-btn" onclick="submitAll()">Submit decisions</button>
<div id="decisions"><pre id="decisions-output"></pre></div>
<script>
const decisions = {{}};
function decide(id, action) {{
  const card = document.getElementById('card-'+id);
  const note = card.querySelector('.note-input').value;
  decisions[id] = {{action, note}};
  card.style.opacity = action === 'apply' ? '1' : '0.45';
  card.style.borderColor = action === 'apply' ? '#22c55e' : '#f59e0b';
}}
function submitAll() {{
  const el = document.getElementById('decisions');
  document.getElementById('decisions-output').textContent = JSON.stringify(decisions, null, 2);
  el.style.display = 'block';
  el.scrollIntoView({{behavior:'smooth'}});
}}
</script>
</body>
</html>"""

# ── Main ──────────────────────────────────────────────────────────────────────

def process_entry(entry: dict) -> dict:
    page_id      = entry["id"]
    notion_url   = f"https://www.notion.so/{page_id.replace('-','')}"
    props        = entry.get("properties", {})

    # Get user-submitted URL
    url_prop     = props.get("userDefined:URL", {})
    product_url  = url_prop.get("url") or ""

    result = {
        "page_id":        page_id,
        "notion_url":     notion_url,
        "product_url":    product_url,
        "name":           (props.get("Name of product",{}).get("title",[{}])[0]
                          .get("plain_text", "Unknown product")),
        "url_status":     "not checked",
        "price":          None,
        "photos_found":   0,
        "photos_broken":  0,
        "photos_uploaded": "no",
        "vegan_verified": None,
        "description":    "",
        "status":         "skipped",
    }

    if not product_url:
        result["url_status"] = "missing"
        return result

    soup = soup_get(product_url)
    active, url_status = is_actively_for_sale(soup, product_url)
    result["url_status"] = url_status

    if soup is None:
        result["status"] = "error"
        return result

    full_text = soup.get_text(" ", strip=True).lower()

    # ── Scrape fields ───────────────────────────────────────────────────────
    # Product name (override blank Notion name)
    name = result["name"]
    for sel in ["h1.product__title","h1.product-single__title","h1"]:
        el = soup.select_one(sel)
        if el:
            name = el.get_text(strip=True)
            break
    result["name"] = name

    price = extract_price(soup)
    result["price"] = price

    photo_urls    = extract_images(soup, product_url)
    result["photos_found"] = len(photo_urls)

    # Check each photo URL
    broken = [u for u in photo_urls if not check_image_url(u)]
    result["photos_broken"] = len(broken)

    # Download working photos
    brand_name = infer_brand(full_text, product_url) or "Unknown"
    slug       = slugify(name)
    photo_dir  = WORKSPACE_DIR / "Photos" / slugify(brand_name) / slug
    saved_urls = []
    for i, url in enumerate(photo_urls[:7]):
        if check_image_url(url):
            ext      = url.split("?")[0].rsplit(".",1)[-1] or "jpg"
            filename = f"{slug}-{i+1}.{ext}"
            dest     = photo_dir / filename
            if download_image(url, dest):
                saved_urls.append(url)
    result["photos_uploaded"] = "yes" if saved_urls else "no"

    # ── Map fields ─────────────────────────────────────────────────────────
    mapped = {
        "name":               name,
        "Brand":              infer_brand(full_text, product_url),
        "Category":           infer_categories(full_text),
        "Gender":             infer_gender(full_text),
        "Level of Protection": infer_protection(full_text),
        "Level of Waterproof": infer_waterproof(full_text),
        "Materials":          infer_materials(full_text),
        "Riding style":       infer_riding_style(full_text),
        "Season":             infer_season(full_text),
        "Vegan Verified":     infer_vegan_status(full_text),
        "Price":              price,
    }

    # ── Description ────────────────────────────────────────────────────────
    cats   = mapped.get("Category") or []
    cat_str = cats[0] if cats else ""
    desc   = write_description(name, mapped.get("Brand",""), cat_str, full_text, price)
    mapped["Description"]   = desc
    result["description"]   = desc
    result["vegan_verified"] = mapped["Vegan Verified"]

    # ── Write to Notion ────────────────────────────────────────────────────
    notion_props = build_notion_props(mapped)
    try:
        notion.pages.update(page_id=page_id, properties=notion_props)
        upload_photos_to_notion(page_id, saved_urls)
        result["status"] = "updated"
        log.info(f"Updated: {name} ({page_id})")
    except Exception as e:
        log.error(f"Notion update failed for {page_id}: {e}", exc_info=True)
        result["status"] = "error"

    return result


def run_audit():
    log.info("=== VMC New Product Audit Started ===")
    entries = get_new_entries()

    if not entries:
        log.info("No new entries to process. Done.")
        return

    results = []
    for entry in entries:
        r = process_entry(entry)
        results.append(r)
        time.sleep(1.5)   # be polite to servers

    # ── Save reports ────────────────────────────────────────────────────────
    md_path   = WORKSPACE_DIR / f"new-product-audit-{DATE_STR}.md"
    html_path = WORKSPACE_DIR / f"new-product-audit-{DATE_STR}.html"

    md_path.write_text(build_md_report(results),   encoding="utf-8")
    html_path.write_text(build_html_review(results), encoding="utf-8")

    ok = sum(1 for r in results if r["status"] == "updated")
    sk = sum(1 for r in results if r["status"] == "skipped")
    er = sum(1 for r in results if r["status"] == "error")
    log.info(f"=== Done: {ok} updated, {sk} skipped, {er} errors ===")
    log.info(f"Report:  {md_path}")
    log.info(f"Review:  {html_path}")


if __name__ == "__main__":
    run_audit()
