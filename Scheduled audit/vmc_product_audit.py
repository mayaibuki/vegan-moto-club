#!/usr/bin/env python3
"""
Vegan Moto Club - Product Audit Script
Fetches product details from user-submitted URLs and updates the Notion database.

Fields updated (using ONLY existing schema options):
  - Name of product, Brand, Category, Description, Price,
    Materials, Gender, Level of Protection, Level of Waterproof,
    Riding style, Season, Vegan Verified, Photos (URLs)

REQUIRED ENV VARS:
  NOTION_TOKEN   - Notion integration token
  NOTION_DB_ID   - Notion database ID (3323ccff-5165-4a31-93bc-232407c82454)
  OPENAI_API_KEY - (optional) Used for LLM-assisted field mapping
"""

import os
import re
import json
import time
import logging
import requests
from bs4 import BeautifulSoup
from notion_client import Client

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

# ─── CONFIG ──────────────────────────────────────────────────────────────────

NOTION_TOKEN = os.environ["NOTION_TOKEN"]
NOTION_DB_ID = os.environ.get("NOTION_DB_ID", "3323ccff-5165-4a31-93bc-232407c82454")

notion = Client(auth=NOTION_TOKEN)

# ─── VALID SCHEMA OPTIONS (DO NOT ADD NEW OPTIONS) ───────────────────────────

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
        # Forma is not in the list — will be left blank if not found
    ],
    "Category": ["Jackets","Gloves","Pants","Boots","Racing Suits","Protection","Street wear"],
    "Gender": ["Women","Men","Unisex"],
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

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122 Safari/537.36"
    )
}

# ─── HELPERS ─────────────────────────────────────────────────────────────────

def match_option(value: str, valid_list: list[str]) -> str | None:
    """Case-insensitive substring match against valid options. Returns the first match."""
    if not value:
        return None
    v_lower = value.lower()
    for opt in valid_list:
        if opt.lower() in v_lower or v_lower in opt.lower():
            return opt
    return None

def match_multi(raw_values: list[str], valid_list: list[str]) -> list[str]:
    """Match multiple raw values against the valid list, returning only valid hits."""
    results = []
    for rv in raw_values:
        m = match_option(rv, valid_list)
        if m and m not in results:
            results.append(m)
    return results

def safe_get(url: str, timeout: int = 15) -> BeautifulSoup | None:
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        r.raise_for_status()
        return BeautifulSoup(r.text, "html.parser")
    except Exception as e:
        log.warning(f"Failed to fetch {url}: {e}")
        return None

def extract_price(text: str) -> float | None:
    """Pull first dollar amount from text."""
    m = re.search(r"\$\s*([\d,]+(?:\.\d{2})?)", text)
    if m:
        return float(m.group(1).replace(",", ""))
    return None

def extract_images(soup: BeautifulSoup, base_url: str) -> list[str]:
    """Find product image URLs (prefer large/zoom images)."""
    imgs = []
    for img in soup.select("img[src]"):
        src = img.get("src", "")
        if not src or "data:" in src:
            continue
        if not src.startswith("http"):
            src = base_url.rstrip("/") + "/" + src.lstrip("/")
        if any(k in src for k in ["product", "variant", "featured", "original"]):
            if src not in imgs:
                imgs.append(src)
    return imgs[:5]  # cap at 5 photos

def infer_vegan_status(soup: BeautifulSoup, description: str) -> str:
    """Best-effort vegan verification based on page text."""
    text = (soup.get_text() + " " + description).lower()
    if any(k in text for k in ["confirmed vegan", "100% vegan", "certified vegan"]):
        return "Confirmed Vegan by maker"
    if any(k in text for k in ["synthetic", "textile", "no animal", "animal-free",
                                 "microfiber", "polyester", "nylon", "cordura"]):
        return "Verified Vegan by AI"
    return "Waiting for confirmation as Vegan"

def scrape_product(url: str) -> dict:
    """Scrape a product page and return a dict of raw extracted data."""
    log.info(f"Scraping: {url}")
    soup = safe_get(url)
    if not soup:
        return {}

    data = {}

    # Product name
    for sel in ["h1.product__title", "h1.product-single__title", "h1", "title"]:
        el = soup.select_one(sel)
        if el:
            data["name"] = el.get_text(strip=True)
            break

    # Description
    for sel in [".product__description", ".product-single__description",
                ".product-description", '[itemprop="description"]']:
        el = soup.select_one(sel)
        if el:
            data["description"] = el.get_text(" ", strip=True)[:2000]
            break

    # Price
    for sel in [".price__regular .price-item", ".product__price", ".price",
                '[itemprop="price"]', ".money"]:
        el = soup.select_one(sel)
        if el:
            price = extract_price(el.get_text())
            if price:
                data["price"] = price
                break

    # Photos
    data["photos"] = extract_images(soup, url)

    # Grab all page text for inference
    full_text = soup.get_text(" ", strip=True).lower()
    data["_full_text"] = full_text

    return data

def map_fields(raw: dict) -> dict:
    """Map raw scraped data onto Notion schema using only valid options."""
    props = {}
    full = raw.get("_full_text", "")

    # Brand — infer from URL domain or page text
    for brand in VALID["Brand"]:
        if brand.lower().replace(" ", "") in full.replace(" ", ""):
            props["Brand"] = brand
            break

    # Category
    category_keywords = {
        "Jackets": ["jacket", "coat"],
        "Gloves": ["glove"],
        "Pants": ["pant", "trouser", "jean"],
        "Boots": ["boot", "shoe", "footwear"],
        "Racing Suits": ["suit", "race suit", "one-piece"],
        "Protection": ["protector", "armor", "armour", "airbag", "vest", "back protector"],
        "Street wear": ["hoodie", "t-shirt", "shirt", "casual"],
    }
    cats = []
    for cat, kws in category_keywords.items():
        if any(kw in full for kw in kws):
            cats.append(cat)
    if cats:
        props["Category"] = cats

    # Gender
    gender = []
    if any(k in full for k in ["women", "woman", "female", "ladies"]):
        gender.append("Women")
    if any(k in full for k in [" men's", " men ", "male", "mens"]):
        gender.append("Men")
    if not gender:
        gender.append("Unisex")
    props["Gender"] = gender

    # Level of Protection — CE level hints
    if any(k in full for k in ["ce level 2", "cat. ii level 2", "cat ii level 2"]):
        props["Level of Protection"] = "Most protective"
    elif any(k in full for k in ["ce level 1", "cat. ii level 1"]):
        props["Level of Protection"] = "Highly protective"
    elif any(k in full for k in ["armor", "armour", "protector", "protection"]):
        props["Level of Protection"] = "Moderately protective"

    # Level of Waterproof
    waterproof_map = {
        "Waterproof (Gore-tex®) ": ["gore-tex", "goretex"],
        "Waterproof (D-Dry®)": ["d-dry"],
        "Waterproof (Drystar®)": ["drystar"],
        "Waterproof (Hydratex®)": ["hydratex"],
        "Waterproof (NextDry™)": ["nextdry"],
        "Waterproof": ["waterproof", "100% waterproof"],
        "Water resistant": ["water resist", "water repel", "dwr"],
        "Not waterproof": [],
    }
    for option, keywords in waterproof_map.items():
        if any(kw in full for kw in keywords):
            props["Level of Waterproof"] = option
            break

    # Materials — keyword scan
    found_mats = []
    mat_keywords = {
        "Cordura® (Synhtetic fabric)": ["cordura"],
        "Gore-tex (waterproof fabric)": ["gore-tex"],
        "Kevlar® (Para-Aramid)": ["kevlar"],
        "Dyneema® (Fiber)(UHMWPE)": ["dyneema"],
        "Mesh fabric": ["mesh"],
        "Nylon": ["nylon"],
        "Polyester": ["polyester"],
        "Cotton": ["cotton"],
        "Denim": ["denim"],
        "Spandex": ["spandex"],
        "Elastane (Elastic fabric)": ["elastane"],
        "YKK zippers": ["ykk"],
        "Microfiber": ["microfiber", "micro fiber"],
        "Vibram®": ["vibram"],
        "Carbon fiber": ["carbon fiber", "carbon fibre"],
        "Titanium": ["titanium"],
        "Aluminum": ["aluminum", "aluminium"],
        "Neoprene": ["neoprene"],
        "D3O® (protective insert)": ["d3o"],
        "Ripstop nylon": ["ripstop"],
        "Amara (Synthetic leather)": ["amara"],
        "Clarino (Artificial leather)": ["clarino"],
        "PrimaLoft®": ["primaloft"],
        "3M Thinsulate (Insulation)": ["thinsulate"],
        "SAS-TEC Level 1": ["sas-tec level 1", "sas-tec lv1"],
        "SAS-TEC Level 2": ["sas-tec level 2", "sas-tec lv2"],
        "Ax® Laredo synthetic leather": ["ax laredo", "axe laredo"],
    }
    for mat, kws in mat_keywords.items():
        if any(kw in full for kw in kws):
            found_mats.append(mat)
    if found_mats:
        props["Materials"] = found_mats

    # Riding style
    style_map = {
        "Off-roading": ["off-road", "offroad", "enduro", "motocross", "dirt"],
        "Adventure / Touring": ["adventure", "adv", "touring", "dual sport"],
        "Commute / Street": ["commute", "urban", "city"],
        "Street": ["street"],
        "Sport / Canyons": ["sport", "canyon", "track day", "spirited"],
        "Racing / Trackdays": ["racing", "race", "trackday", "track day", "circuit"],
    }
    styles = []
    for style, kws in style_map.items():
        if any(kw in full for kw in kws):
            styles.append(style)
    if styles:
        props["Riding style"] = styles

    # Season
    season_map = {
        "☀️ Summer": ["summer", "warm weather", "ventilated", "airflow", "mesh"],
        "🌦 Mid season": ["mid season", "mid-season", "spring", "autumn", "fall", "transition"],
        "❄️ Winter": ["winter", "cold weather", "thermal", "insulated", "heated"],
    }
    seasons = []
    for season, kws in season_map.items():
        if any(kw in full for kw in kws):
            seasons.append(season)
    if seasons:
        props["Season"] = seasons

    # Vegan Verified (AI assessment)
    description = raw.get("description", "")
    props["Vegan Verified"] = infer_vegan_status(
        BeautifulSoup(f"<p>{description}</p>", "html.parser"), full
    )

    # Simple text/number fields
    if raw.get("name"):
        props["_name"] = raw["name"]
    if raw.get("description"):
        props["Description"] = raw["description"]
    if raw.get("price"):
        props["Price"] = raw["price"]
    if raw.get("photos"):
        props["_photos"] = raw["photos"]

    return props

# ─── NOTION HELPERS ───────────────────────────────────────────────────────────

def build_notion_props(mapped: dict) -> dict:
    """Convert mapped fields dict to Notion property update payload."""
    p = {}

    if "_name" in mapped:
        p["Name of product"] = {"title": [{"text": {"content": mapped["_name"]}}]}

    if "Description" in mapped:
        p["Description"] = {"rich_text": [{"text": {"content": mapped["Description"][:2000]}}]}

    if "Price" in mapped:
        p["Price"] = {"number": mapped["Price"]}

    if "Brand" in mapped:
        p["Brand"] = {"select": {"name": mapped["Brand"]}}

    if "Category" in mapped:
        p["Category"] = {"multi_select": [{"name": c} for c in mapped["Category"]]}

    if "Gender" in mapped:
        p["Gender"] = {"multi_select": [{"name": g} for g in mapped["Gender"]]}

    if "Level of Protection" in mapped:
        p["Level of Protection"] = {"select": {"name": mapped["Level of Protection"]}}

    if "Level of Waterproof" in mapped:
        p["Level of Waterproof"] = {"select": {"name": mapped["Level of Waterproof"]}}

    if "Materials" in mapped:
        p["Materials"] = {"multi_select": [{"name": m} for m in mapped["Materials"]]}

    if "Riding style" in mapped:
        p["Riding style"] = {"multi_select": [{"name": s} for s in mapped["Riding style"]]}

    if "Season" in mapped:
        p["Season"] = {"multi_select": [{"name": s} for s in mapped["Season"]]}

    if "Vegan Verified" in mapped:
        p["Vegan Verified"] = {"select": {"name": mapped["Vegan Verified"]}}

    return p

def get_pending_entries() -> list[dict]:
    """Query Notion for entries that have a user-submitted URL but missing key fields."""
    results = []
    cursor = None

    while True:
        kwargs = {
            "database_id": NOTION_DB_ID,
            "filter": {
                "and": [
                    {"property": "userDefined:URL", "url": {"is_not_empty": True}},
                    {"property": "Description", "rich_text": {"is_empty": True}},
                ]
            },
            "page_size": 100,
        }
        if cursor:
            kwargs["start_cursor"] = cursor

        resp = notion.databases.query(**kwargs)
        results.extend(resp.get("results", []))

        if not resp.get("has_more"):
            break
        cursor = resp.get("next_cursor")

    log.info(f"Found {len(results)} entries to audit")
    return results

def update_entry(page_id: str, notion_props: dict, photo_urls: list[str]) -> None:
    """Update a Notion page with the audited properties."""
    if not notion_props:
        return

    notion.pages.update(page_id=page_id, properties=notion_props)
    log.info(f"Updated page {page_id}")

    # Upload photos as external file links (Notion API only supports external URLs)
    if photo_urls:
        try:
            notion.pages.update(
                page_id=page_id,
                properties={
                    "Photos": {
                        "files": [
                            {"name": f"photo_{i+1}", "type": "external",
                             "external": {"url": u}}
                            for i, u in enumerate(photo_urls[:5])
                        ]
                    }
                }
            )
        except Exception as e:
            log.warning(f"Could not update photos for {page_id}: {e}")

# ─── MAIN ─────────────────────────────────────────────────────────────────────

def run_audit():
    log.info("=== Vegan Moto Club Product Audit Started ===")
    entries = get_pending_entries()

    updated = 0
    skipped = 0
    errors = 0

    for entry in entries:
        page_id = entry["id"]
        props = entry.get("properties", {})

        # Get the user-submitted product URL
        url_prop = props.get("userDefined:URL", {})
        product_url = url_prop.get("url") or (
            url_prop.get("rich_text", [{}])[0].get("plain_text") if url_prop.get("rich_text") else None
        )

        if not product_url:
            log.warning(f"No URL for page {page_id}, skipping")
            skipped += 1
            continue

        try:
            raw = scrape_product(product_url)
            if not raw:
                log.warning(f"No data scraped from {product_url}")
                skipped += 1
                continue

            mapped = map_fields(raw)
            notion_props = build_notion_props(mapped)
            photo_urls = mapped.pop("_photos", [])

            update_entry(page_id, notion_props, photo_urls)
            updated += 1

            # Be polite to servers
            time.sleep(1.5)

        except Exception as e:
            log.error(f"Error processing {product_url}: {e}", exc_info=True)
            errors += 1
            time.sleep(2)

    log.info(
        f"=== Audit Complete: {updated} updated, {skipped} skipped, {errors} errors ==="
    )

if __name__ == "__main__":
    run_audit()
