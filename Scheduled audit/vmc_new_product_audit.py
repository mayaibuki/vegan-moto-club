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

import os, re, sys, json, time, datetime, logging, pathlib, hashlib, argparse
import requests
from bs4 import BeautifulSoup
from notion_client import Client

import lib_anthropic

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

# ── Shopify tag-driven field mapping (authoritative for Shopify-backed brands) ─
# Merchant-curated `tags` from {base}/products/{handle}.json are structured data,
# unlike rendered-page prose which carries footer/nav chrome (the "GORE-TEX
# Gloves" cross-sell link that previously over-tagged waterproof). When a product
# URL is on a known Shopify storefront, we trust its tags over scraped text for
# Gender / Riding style / Level of Waterproof.
SHOPIFY_BRAND_DOMAINS = {
    "revitsport.com": "REV'IT!",
}

def shopify_handle(url: str) -> "str | None":
    m = re.search(r"/products/([^/?#]+)", url or "")
    return m.group(1) if m else None

def shopify_base(url: str) -> "str | None":
    m = re.match(r"(https?://[^/]+)", url or "")
    if not m:
        return None
    host = m.group(1)
    for dom in SHOPIFY_BRAND_DOMAINS:
        if dom in host:
            return host
    return None

def fetch_shopify_tags(url: str) -> "set[str] | None":
    """Return lowercased tag set for a Shopify product URL, or None if N/A."""
    base   = shopify_base(url)
    handle = shopify_handle(url)
    if not base or not handle:
        return None
    try:
        r = safe_get(f"{base}/products/{handle}.json", timeout=15)
        if not r or r.status_code != 200:
            return None
        tags = r.json().get("product", {}).get("tags") or []
        if isinstance(tags, str):           # some stores return CSV string
            tags = [t.strip() for t in tags.split(",")]
        return {t.lower() for t in tags}
    except Exception as e:
        log.debug(f"shopify tag fetch failed for {url}: {e}")
        return None

def tags_map_gender(tags: set) -> list:
    has_w = "women's" in tags or "women" in tags
    has_m = "men's" in tags or "men" in tags
    has_u = "unisex" in tags
    if has_u or (has_w and has_m):
        return ["Unisex"]
    if has_w and not has_m:
        return ["Women"]
    return ["Men"]

def tags_map_riding(tags: set) -> list:
    styles = set()
    joined = " | ".join(tags)
    if "off-road" in joined or "offroad" in joined:
        styles.update({"Off-roading", "Adventure / Touring"})
    if "adventure" in joined:
        styles.add("Adventure / Touring")
    if "sport" in joined:
        styles.add("Sport / Canyons")
    if "urban" in joined:
        styles.add("Commute / Street")
    if "race" in joined or "racing" in joined or "track" in joined:
        styles.add("Racing / Trackdays")
    order = ["Off-roading","Adventure / Touring","Commute / Street",
             "Sport / Canyons","Racing / Trackdays"]
    return [s for s in order if s in styles]

def _wp_opt(substr: str) -> "str | None":
    for o in VALID["Level of Waterproof"]:
        if substr.lower() in o.lower():
            return o
    return None

def tags_map_waterproof(tags: set) -> str:
    joined = " | ".join(tags)
    if "gore-tex" in joined or "goretex" in joined or "gore tex" in joined:
        return _wp_opt("gore-tex") or "Waterproof"
    if "hydratex" in joined:
        return _wp_opt("hydratex") or "Waterproof"
    if "waterproof" in joined or "aquadefence" in joined or "tizip" in joined:
        return _wp_opt("waterproof") or "Waterproof"
    if "water resistant" in joined or "water-resistant" in joined:
        return _wp_opt("water resistant") or "Water resistant"
    return "Not waterproof"

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

def detect_sku(soup: BeautifulSoup) -> "str | None":
    """
    Pull the product's style/SKU code from the page so we can tie images to the
    product being audited. Shopify and most retail platforms embed the code in a
    JSON blob ("sku", "barcode", or a numeric variant id) and reuse it as the
    leading token of every gallery image filename (e.g. 3201026_9298_..._FR.jpg).

    Returns a leading run of >=5 digits (the style code) or None if the page
    does not expose one. Marketing/lifestyle assets do not carry this code, which
    is what lets the caller filter them out.
    """
    html = str(soup)
    candidates: list[str] = []
    # Explicit fields first - these name the product directly.
    for pat in (r'"sku"\s*:\s*"([^"]+)"', r'"barcode"\s*:\s*"([^"]+)"'):
        for raw in re.findall(pat, html):
            m = re.match(r"\D*(\d{5,})", raw)
            if m:
                candidates.append(m.group(1))
    if not candidates:
        return None
    # The most-repeated code is the product's own (variants reuse it).
    from collections import Counter
    return Counter(candidates).most_common(1)[0][0]


def _img_style_token(url: str) -> "str | None":
    """Leading run of >=5 digits in the image's filename, or None."""
    fname = url.rsplit("/", 1)[-1]
    m = re.match(r"(\d{5,})", fname)
    return m.group(1) if m else None


def extract_images(soup: BeautifulSoup, base_url: str) -> list[str]:
    imgs = []
    for img in soup.select("img[src], img[data-src]"):
        src = img.get("src") or img.get("data-src") or ""
        if not src or "data:" in src:
            continue
        if src.startswith("//"):
            src = "https:" + src
        elif not src.startswith("http"):
            src = base_url.rstrip("/") + "/" + src.lstrip("/")
        # prefer product images
        if any(k in src.lower() for k in ["product","variant","featured","original","large"]):
            if src not in imgs:
                imgs.append(src)
    # fallback: any reasonably large image
    if not imgs:
        for img in soup.select("img[src]"):
            src = img.get("src","")
            if src.startswith("//"):
                src = "https:" + src
            if src.startswith("http") and src not in imgs:
                imgs.append(src)

    # SKU-aware filtering: keep only images whose filename carries the product's
    # style code. This drops cross-sell thumbnails, lifestyle renders, and nav
    # GIFs that share no code with the product. Two ways to find the target code:
    #   1. an explicit SKU from the page JSON, if it appears in a filename, or
    #   2. the dominant filename token, when several gallery shots share one.
    # If neither is available we fall back to the unfiltered list (no regression
    # for sites that don't encode a SKU in image names).
    from collections import Counter
    tokens = {src: _img_style_token(src) for src in imgs}
    sku = detect_sku(soup)
    target = sku if (sku and sku in tokens.values()) else None
    if target is None:
        counts = Counter(t for t in tokens.values() if t)
        if counts:
            top, n = counts.most_common(1)[0]
            if n >= 2:
                target = top
    if target:
        matched = [src for src in imgs if tokens[src] == target]
        if matched:
            return matched[:7]
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

def infer_categories(name: str, full_text: str) -> list[str]:
    """
    Name-only keyword matching. Returning empty for names that don't clearly
    indicate a category is intentional - empty fields are reviewable; wrong
    fields disappear into the clutter. The full_text fallback was removed
    after observing cross-sell modules consistently corrupting results.
    The full_text arg is kept for signature compatibility with the LLM path
    that consumes the same page content.
    """
    _ = full_text  # intentionally unused; kept for symmetry with LLM signature
    kw = {
        "Jackets":      ["jacket","coat","gilet","vest"],
        "Gloves":       ["glove"],
        "Pants":        ["pant","trouser","jean","chino","breeche","legging"],
        "Boots":        ["boot","shoe","sneaker","footwear"],
        "Racing Suits": ["race suit","one-piece","one piece","overall","racing suit"],
        "Protection":   ["protector","airbag","back protector","body armor","chest protector","impact vest"],
        "Street wear":  ["hoodie","t-shirt","shirt","casual","sweater","knitwear"],
    }
    name_lc = (name or "").lower()
    return [c for c, words in kw.items() if any(w in name_lc for w in words)]

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

def infer_riding_style(name: str, full_text: str) -> list[str]:
    """
    Name-only keyword matching. See infer_categories for the rationale on
    not falling back to full_text.
    """
    _ = full_text
    style_kw = {
        "Off-roading":         ["off-road","offroad","enduro","motocross","dirt bike","mx ","dirt"],
        "Adventure / Touring": ["adventure","adv ","dual sport","touring","tourer"],
        "Commute / Street":    ["commute","commuting","urban","city"],
        "Street":              ["streetbike"],
        "Sport / Canyons":     ["canyon","superbike"],
        "Racing / Trackdays":  ["racing","trackday","track day","circuit"],
    }
    name_lc = (name or "").lower()
    return [s for s, kws in style_kw.items() if any(k in name_lc for k in kws)]

def infer_season(name: str, full_text: str) -> list[str]:
    """
    Name-only keyword matching. See infer_categories for rationale.
    """
    _ = full_text
    s_kw = {
        "☀️ Summer":     ["summer","airflow","mesh","ventilated"],
        "🌦 Mid season": ["mid season","mid-season","3-season","4-season","all season","all-season"],
        "❄️ Winter":     ["winter","thermal","insulated","heated"],
    }
    name_lc = (name or "").lower()
    return [s for s, kws in s_kw.items() if any(k in name_lc for k in kws)]

# A maker's *structured* vegan claim is a short label, not prose. We accept a
# label whose text is essentially just "Vegan" (optionally "100% Vegan",
# "Vegan friendly", "Vegan construction/materials", "Vegan: Yes").
_VEGAN_LABEL_RE = re.compile(
    r"^\s*(100%\s*|fully\s*)?vegan"
    r"(\s*[:\-–]?\s*(yes|✓|true|certified|approved|friendly|construction|materials?|fabric|product))?"
    r"\s*$",
    re.IGNORECASE,
)
# Tags/classes that mark an element as a label/spec/feature rather than body copy.
_LABEL_SELECTORS = "h1,h2,h3,h4,h5,h6,dt,th,summary,strong,b,caption,figcaption"
_LABEL_CLASS_RE = re.compile(
    r"feature|badge|spec|attribute|tag|label|sustainab|chip|pill|highlight|icon",
    re.IGNORECASE,
)

def maker_marks_vegan(soup) -> bool:
    """
    Brand-agnostic detection of a maker's explicit 'Vegan' label on the product
    page. Looks only at label-like elements (headings, spec/feature cells,
    definition terms, badge/sustainability nodes) so incidental prose mentions
    (e.g. '...vegan leather alternative...') don't trigger a false positive.
    Works whether or not the brand uses a 'Sustainability' tab like REV'IT!.
    """
    if soup is None:
        return False
    try:
        candidates = list(soup.select(_LABEL_SELECTORS))
        # elements whose class/id hints they are a label/spec/feature/badge
        for el in soup.find_all(True):
            attr = " ".join(el.get("class", []) or []) + " " + (el.get("id") or "")
            if attr.strip() and _LABEL_CLASS_RE.search(attr):
                candidates.append(el)
        for el in candidates:
            txt = el.get_text(" ", strip=True)
            if txt and len(txt) <= 40 and _VEGAN_LABEL_RE.match(txt):
                return True
        # spec/definition rows: key cell 'Vegan' with an affirmative value cell
        for dt in soup.select("dt,th"):
            key = dt.get_text(" ", strip=True).lower().rstrip(":")
            if key == "vegan":
                sib = dt.find_next_sibling(["dd", "td"])
                val = (sib.get_text(" ", strip=True).lower() if sib else "")
                if val in ("", "yes", "✓", "true") or val.startswith("yes"):
                    return True
    except Exception as e:
        log.debug(f"maker_marks_vegan parse error: {e}")
    return False

def infer_vegan_status(full_text: str, soup=None) -> str:
    """
    Cheap keyword pass first. If the signal is clean, return immediately.
    If signals conflict or are absent, defer to lib_anthropic.adjudicate_vegan.
    """
    # First-party structured claim on the page outranks everything.
    if maker_marks_vegan(soup):
        return "Confirmed Vegan by maker"
    if any(k in full_text for k in ["confirmed vegan","100% vegan","certified vegan","cruelty-free confirmed"]):
        return "Confirmed Vegan by maker"
    animal_flags = ["leather","suede","wool","down","fur","sheepskin","nubuck","kangaroo","snake skin"]
    vegan_synthetics = ["synthetic","textile","no animal","animal-free","microfiber","polyester",
                        "nylon","cordura","gore-tex","clarino","amara","axe laredo"]
    has_animal    = any(k in full_text for k in animal_flags)
    has_synthetic = any(k in full_text for k in vegan_synthetics)

    # Confident calls: skip the LLM.
    if has_synthetic and not has_animal:
        return "Verified Vegan by AI"
    if has_animal and not has_synthetic:
        return "Waiting for confirmation as Vegan"

    # Ambiguous: both signals present, or neither. Ask Haiku.
    label, rationale = lib_anthropic.adjudicate_vegan(full_text)
    if rationale:
        log.info(f"Vegan adjudicated: {label} ({rationale})")
    return label

# ── Humanized description writer ──────────────────────────────────────────────

def write_description(name: str, brand: str, category: str,
                      full_text: str, price: "float | None",
                      materials: "list | None" = None) -> str:
    """
    Delegates to lib_anthropic.write_description (Haiku 4.5 with prompt caching).
    Falls back to a deterministic stub when ANTHROPIC_API_KEY is absent.
    """
    return lib_anthropic.write_description(
        name=name, brand=brand, category=category,
        full_text=full_text, price=price, materials=materials,
    )

# ── Notion helpers ────────────────────────────────────────────────────────────

def get_new_entries() -> list[dict]:
    """Return entries with a URL but empty Description — up to BATCH_LIMIT."""
    results, cursor = [], None
    while len(results) < BATCH_LIMIT:
        kwargs = {
            "database_id": NOTION_DB_ID,
            "filter": {
                "and": [
                    {"property": "URL",  "url":       {"is_not_empty": True}},
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

def notion_field_empty(existing: dict, field: str) -> bool:
    """True if a Notion property currently holds no value. Used to make the
    audit non-destructive: we only fill blanks, never overwrite curated data."""
    prop = (existing or {}).get(field)
    if not prop:                       # property not present at all
        return True
    kind = prop.get("type") or next((k for k in prop if k != "id"), None)
    val  = prop.get(kind)
    if kind in ("multi_select", "rich_text", "title", "files", "relation"):
        return not val
    if kind in ("select", "status", "date", "url", "number", "email"):
        return val in (None, "", [])
    return val in (None, "", [])

def build_notion_props(p: dict, existing: "dict | None" = None) -> dict:
    """Convert mapped-fields dict to Notion property update payload.

    When `existing` (the page's current properties) is given, only fields that
    are currently empty are written — curated/manual values are never clobbered.
    """
    skip = (lambda f: existing is not None and not notion_field_empty(existing, f))
    out = {}
    if p.get("name") and not skip("Name of product"):
        out["Name of product"] = {"title": [{"text": {"content": p["name"]}}]}
    if p.get("Description") and not skip("Description"):
        out["Description"] = {"rich_text": [{"text": {"content": p["Description"][:2000]}}]}
    if p.get("Price") and not skip("Price"):
        out["Price"] = {"number": p["Price"]}
    if p.get("Brand") and not skip("Brand"):
        out["Brand"] = {"select": {"name": p["Brand"]}}
    if p.get("Category") and not skip("Category"):
        out["Category"] = {"multi_select": [{"name": c} for c in p["Category"]]}
    if p.get("Gender") and not skip("Gender"):
        out["Gender"] = {"multi_select": [{"name": g} for g in p["Gender"]]}
    if p.get("Level of Protection") and not skip("Level of Protection"):
        out["Level of Protection"] = {"select": {"name": p["Level of Protection"]}}
    if p.get("Level of Waterproof") and not skip("Level of Waterproof"):
        out["Level of Waterproof"] = {"select": {"name": p["Level of Waterproof"]}}
    if p.get("Materials") and not skip("Materials"):
        out["Materials"] = {"multi_select": [{"name": m} for m in p["Materials"]]}
    if p.get("Riding style") and not skip("Riding style"):
        out["Riding style"] = {"multi_select": [{"name": s} for s in p["Riding style"]]}
    if p.get("Season") and not skip("Season"):
        out["Season"] = {"multi_select": [{"name": s} for s in p["Season"]]}
    if p.get("Vegan Verified") and not skip("Vegan Verified"):
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
    url_prop     = props.get("URL", {})
    product_url  = url_prop.get("url") or ""

    result = {
        "page_id":        page_id,
        "notion_url":     notion_url,
        "product_url":    product_url,
        "name":           (lambda t: t[0].get("plain_text", "Unknown product") if t else "Unknown product")(
                              props.get("Name of product", {}).get("title", []) or []),
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
    # Brand / Category / Gender go through Haiku first (the keyword versions
    # were noisy: substring matches on "icon", footer cross-sells, etc).
    # Keyword inference stays as the fallback when the LLM is unavailable.
    llm_fields = lib_anthropic.infer_fields(
        name=name,
        url=product_url,
        full_text=full_text,
        valid_brands=VALID["Brand"],
        valid_categories=VALID["Category"],
        valid_genders=VALID["Gender"],
        valid_riding_styles=VALID["Riding style"],
        valid_seasons=VALID["Season"],
    )
    brand    = llm_fields.get("brand")    or infer_brand(full_text, product_url)
    cats_llm   = llm_fields.get("categories")   or []
    cats       = cats_llm   if cats_llm   else infer_categories(name, full_text)
    gend_llm   = llm_fields.get("gender")       or []
    gend       = gend_llm   if gend_llm   else infer_gender(full_text)
    styles_llm = llm_fields.get("riding_style") or []
    styles     = styles_llm if styles_llm else infer_riding_style(name, full_text)
    season_llm = llm_fields.get("season")       or []
    seasons    = season_llm if season_llm else infer_season(name, full_text)
    waterproof = infer_waterproof(full_text)

    # ── Authoritative override: Shopify-backed brands have curated `tags` ────
    # Tags are structured data; they beat page-text heuristics for gender,
    # riding style, and waterproofing (and pin the brand, avoiding the noisy
    # substring "icon"/"bison" mislabels). Only applied when tags are present.
    sp_tags = fetch_shopify_tags(product_url)
    if sp_tags:
        brand      = SHOPIFY_BRAND_DOMAINS.get(shopify_base(product_url).split("//")[-1], brand) \
                     if shopify_base(product_url) else brand
        gend       = tags_map_gender(sp_tags)
        styles     = tags_map_riding(sp_tags) or styles
        waterproof = tags_map_waterproof(sp_tags)
        log.info(f"Shopify tags applied for {name}: gender={gend} "
                 f"styles={styles} waterproof={waterproof}")

    mapped = {
        "name":               name,
        "Brand":              brand,
        "Category":           cats,
        "Gender":             gend,
        "Level of Protection": infer_protection(full_text),
        "Level of Waterproof": waterproof,
        "Materials":          infer_materials(full_text),
        "Riding style":       styles,
        "Season":             seasons,
        "Vegan Verified":     infer_vegan_status(full_text, soup),
        "Price":              price,
    }

    # ── Description ────────────────────────────────────────────────────────
    cats   = mapped.get("Category") or []
    cat_str = cats[0] if cats else ""
    desc   = write_description(name, mapped.get("Brand",""), cat_str, full_text, price,
                               materials=mapped.get("Materials") or [])
    mapped["Description"]   = desc
    result["description"]   = desc
    result["vegan_verified"] = mapped["Vegan Verified"]

    # ── Write to Notion (non-destructive: only fill currently-empty fields) ──
    notion_props = build_notion_props(mapped, existing=props)
    try:
        notion.pages.update(page_id=page_id, properties=notion_props)
        upload_photos_to_notion(page_id, saved_urls)
        result["status"] = "updated"
        log.info(f"Updated: {name} ({page_id})")
    except Exception as e:
        log.error(f"Notion update failed for {page_id}: {e}", exc_info=True)
        result["status"] = "error"

    return result


def run_audit(page_id: "str | None" = None):
    """
    page_id=None (default) -> batch mode: process up to BATCH_LIMIT entries
                              with empty Description (the original behaviour).
    page_id=<id>           -> single-product mode used by the Notion webhook.
                              Skips the database query entirely.
    """
    log.info("=== VMC New Product Audit Started ===")

    if page_id:
        try:
            entry = notion.pages.retrieve(page_id=page_id)
        except Exception as e:
            log.error(f"Failed to retrieve {page_id}: {e}")
            sys.exit(1)
        if entry.get("archived") or entry.get("in_trash"):
            log.warning(f"Page {page_id} is archived/trashed - skipping")
            return
        entries = [entry]
        log.info(f"Single-product mode: {page_id}")
    else:
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

    # In single-page mode (webhook-driven), surface failures as a non-zero exit
    # so the GitHub Action goes red and the issue is visible. Batch mode keeps
    # exit 0 so one bad scrape doesn't fail the whole nightly run.
    if page_id and er > 0:
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="VMC new product audit")
    parser.add_argument("--page-id", help="Process a single Notion page id (event-driven mode)")
    args = parser.parse_args()
    run_audit(page_id=args.page_id)
