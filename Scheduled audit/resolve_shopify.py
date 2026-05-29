import json, requests, concurrent.futures as cf

H = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}

# brand -> shopify storefront base
SHOP = {
    "Alpinestars": "https://www.alpinestars.com",
    "REV'IT!": "https://www.revitsport.com",
    "Stellar": "https://www.stellarmotobrand.com",
    "Olympia": "https://shop.olympiagloves.com",
    "Skull Riderz": "https://skullriderz.com",
    "Andromeda": "https://andromedamoto.com",
    "Atwyld": "https://atwyld.com",
    "Tobacco Motorwear": "https://tobaccomotorwear.com",
    "Motogirl": "https://motogirl.co.uk",
    "Joe Rocket": "https://www.joerocket.com",
    "Rokker": "https://therokkercompany.com",
    "Bull-it Jeans": "https://www.bull-it.com",
    "Bitwell": "https://biltwellinc.com",
}

def norm(u):
    if u.startswith("//"):
        return "https:" + u
    return u

def product_images(base, handle):
    for suf in (".js", ".json"):
        try:
            r = requests.get(f"{base}/products/{handle}{suf}", headers=H, timeout=15)
            if r.status_code == 200:
                d = r.json(); p = d.get("product", d)
                return [norm(i["src"] if isinstance(i, dict) else i) for i in p.get("images", [])]
        except Exception:
            pass
    return []

import re
def clean(s):
    s = s.replace("®", " ").replace("™", " ").replace("®", " ")
    return re.sub(r"\s+", " ", s).strip()

def search(base, q, limit=8):
    try:
        r = requests.get(f"{base}/search/suggest.json",
                         params={"q": clean(q), "resources[type]": "product", "resources[limit]": limit},
                         headers=H, timeout=15)
        if r.status_code == 200:
            return [(p["title"], p["handle"]) for p in r.json()["resources"]["results"]["products"]]
    except Exception:
        pass
    return []

STOP = {"the", "and", "boots", "boot", "shoes", "shoe", "gloves", "glove",
        "jacket", "pants", "jeans", "ladies", "women", "womens", "woman",
        "men", "mens", "man", "stella"}
def toks(s):
    return {t for t in re.findall(r"[a-z0-9]+", clean(s).lower()) if t and t not in STOP}

CATWORDS = {
    "boots": "boot", "boot": "boot", "shoes": "boot", "shoe": "boot",
    "gloves": "glove", "glove": "glove",
    "jacket": "jacket", "sweater": "jacket", "sweatshirt": "jacket", "hoodie": "jacket",
    "pants": "pants", "jeans": "pants", "jean": "pants", "leggings": "pants",
}
def category(s):
    l = s.lower()
    for w, c in CATWORDS.items():
        if re.search(rf"\b{w}\b", l):
            return c
    return None

def gender(s):
    l = s.lower()
    if any(w in l for w in ("women", "woman", "ladies", "stella", "girl")):
        return "w"
    if re.search(r"\bmen('?s)?\b|\bman\b|\bmale\b", l):
        return "m"
    return None

VARIANT = {"vented", "drystar", "goretex", "gore", "gtx", "h2o", "wp", "waterproof", "tex"}
def variants(s):
    return {t for t in toks(s) if t in VARIANT}

def best_candidate(name, cands, cat_hint=None):
    """Pick candidate matching model tokens + gender + variant + category."""
    want = toks(name)
    ng = gender(name)
    nv = variants(name)
    nc = category(name) or (category(cat_hint) if cat_hint else None)
    nums = {t for t in want if any(c.isdigit() for c in t)}
    best, bestscore = None, -1
    for title, handle in cands:
        have = toks(title)
        cg = gender(title)
        cc = category(title)
        if nc and cc and nc != cc:        # category conflict (boot vs glove) -> skip
            continue
        if ng and cg and ng != cg:        # gender conflict -> skip
            continue
        if nums and not nums.issubset(have):  # model/version conflict -> skip
            continue
        cv = variants(title)
        if nv and cv and nv != cv:        # variant conflict (vented vs drystar etc) -> skip
            continue
        cnums = {t for t in have if any(c.isdigit() for c in t)}
        extra_nums = cnums - nums          # candidate introduces a version the name lacks
        score = len(want & have) - 2 * len(extra_nums)
        if score > bestscore:
            best, bestscore = (title, handle), score
    if not best:
        return None
    title, handle = best
    # confidence: high if all model tokens present AND (gender agrees or name has none)
    conf = "high" if (nums.issubset(toks(title)) and bestscore >= max(1, len(want) - 1)) else "low"
    return (title, handle, conf)

def handle_from_url(url):
    if "/products/" in url:
        return url.split("/products/")[1].split("?")[0].strip("/")
    return None

def url_host_base(url):
    m = re.match(r"(https?://[^/]+)", url or "")
    return m.group(1) if m else None

# hosts known NOT to be Shopify (skip url-host probing for these)
NON_SHOPIFY_HOSTS = ("revzilla.com", "dainese.com", "klim.com", "aerostich.com",
                     "sportbiketrackgear.com", "shewolfmotoco.com")

data = json.load(open("Scheduled audit/affected_photos.json"))
out = []
for d in data:
    brand = d["brand"]
    base = SHOP.get(brand)
    uh = url_host_base(d["url"])
    url_is_shopify = (uh and "/products/" in (d["url"] or "")
                      and not any(h in uh for h in NON_SHOPIFY_HOSTS))
    if not base and url_is_shopify:
        base = uh
    if not base:
        out.append({**d, "status": "non-shopify-skip", "imgs": []})
        continue
    imgs, used, conf = [], None, None
    # 1) try the product URL's own host + handle (most precise) if it's a Shopify store
    if url_is_shopify:
        h = handle_from_url(d["url"])
        imgs = product_images(uh, h)
        if imgs: used, conf = f"url-handle:{h}@{uh}", "high"
    # 2) try brand-base + handle if URL host matches brand base
    if not imgs and base.split("//")[1].split("/")[0] in (d["url"] or ""):
        h = handle_from_url(d["url"])
        if h:
            imgs = product_images(base, h)
            if imgs: used, conf = f"url-handle:{h}", "high"
    if not imgs:
        words = d["name"].split()
        cands = []
        for q in (d["name"], " ".join(words[:3]), " ".join(words[:2]), words[0]):
            cands = search(base, q)
            if cands:
                break
        cand_str = "; ".join(f"{t}->{hh}" for t, hh in cands)
        cat_hint = " ".join(d.get("category") or [])
        pick = best_candidate(d["name"], cands, cat_hint) if cands else None
        if pick:
            imgs = product_images(base, pick[1])
            if imgs: used, conf = f"search:{pick[0]}|{pick[1]}", pick[2]
        out.append({**d, "status": "resolved" if imgs else "no-images",
                    "conf": conf, "used": used, "candidates": cand_str, "imgs": imgs})
        continue
    out.append({**d, "status": "resolved", "conf": conf, "used": used, "candidates": "", "imgs": imgs})

# HEAD-check resolved imgs
def ok(u):
    try:
        r = requests.head(u, headers=H, timeout=12, allow_redirects=True)
        if r.status_code in (403, 405):
            r = requests.get(u, headers=H, timeout=15, stream=True)
        return r.status_code == 200
    except Exception:
        return False

all_imgs = {u for o in out for u in o["imgs"]}
verdict = {}
with cf.ThreadPoolExecutor(max_workers=20) as ex:
    fs = {ex.submit(ok, u): u for u in all_imgs}
    for f in cf.as_completed(fs):
        verdict[fs[f]] = f.result()
for o in out:
    o["imgs_ok"] = [u for u in o["imgs"] if verdict.get(u)]
    # single-image search matches are weak -> review, not auto-write
    if o.get("conf") == "high" and o.get("used", "").startswith("search:") and len(o["imgs_ok"]) <= 1:
        o["conf"] = "low"

json.dump(out, open("Scheduled audit/resolved_shopify.json", "w"), indent=1)
print("=== SHOPIFY RESOLUTION ===")
for o in out:
    if o["status"] == "non-shopify-skip":
        continue
    print(f'\n{o["name"]}  [{o["brand"]}]  {o["status"]}  conf={o.get("conf")}  ok={len(o.get("imgs_ok",[]))}/{len(o["imgs"])}')
    if o.get("used"): print("   used:", o["used"])
ns = [o for o in out if o["status"] == "non-shopify-skip"]
hi = [o for o in out if o.get("imgs_ok") and o.get("conf") == "high"]
lo = [o for o in out if o.get("imgs_ok") and o.get("conf") == "low"]
print(f"\nHIGH-confidence (auto-write): {len(hi)}")
print(f"LOW-confidence (review):     {len(lo)} ->", ", ".join(o["name"] for o in lo))
print(f"non-shopify ({len(ns)}):", ", ".join(sorted({o["brand"] for o in ns})))
