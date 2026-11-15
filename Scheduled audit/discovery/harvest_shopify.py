#!/usr/bin/env python3
"""
harvest_shopify.py: scout stage of the "discover new vegan gear" pipeline.

Read-only. Never writes to Notion. Used by .claude/commands/discover-gear.md.

  catalog --base URL --out RUN [--cache-json FILE]
      Page through <base>/products.json?limit=250&page=N until an empty page
      and save RUN/catalog.json. --cache-json loads an already downloaded
      list (a bare list or {"products": [...]}) instead of fetching.

  models --run RUN
      Build RUN/models.json from catalog.json: keep US-sellable products
      (tag RegularUS or OutletUS), group colourways into one model, mark
      scope and a leather pre-filter, print a summary.

  specs --run RUN [--limit N] [--only-status candidate,suspect] [--pause 2.0]
      For each in-scope model that was not dropped by the Leather tag, fetch
      the representative colourway page once (one request per --pause
      seconds, global), extract the "Specs and features" accordions and save
      RUN/specs/<model-slug>.json. Resumable: saved models are skipped.

Run folders: Scheduled audit/discovery/<brand-slug>/<YYYY-MM-DD>/ (gitignored).
"""
import argparse
import datetime
import html as htmllib
import json
import os
import re
import sys
import time
from collections import Counter, defaultdict
from urllib.parse import urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
TODAY = datetime.date.today().isoformat()

HEADERS = {
    # The store's robots.txt asks automated clients to identify themselves.
    "User-Agent": "gear-catalog-research-bot/1.0 (automated; low volume)",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}
TIMEOUT = 30
MAX_TRIES = 3
DEFAULT_429_WAIT = 60

US_TAGS = {"RegularUS", "OutletUS"}
IN_SCOPE_TYPES = {
    "Jackets", "Pants", "Jeans", "Gloves", "Boots", "Shoes", "Suits",
    "Protection", "Rain gear", "Undergarments",
}
GENDER_TAGS = ("Men's", "Women's", "Unisex")
ANIMAL_RE = re.compile(
    r"\b(leather|suede|nubuck|goat|goatskin|cow|cowhide|kangaroo|buffalo|wool|"
    r"merino|down|silk|sheepskin|fur)\b",
    re.I,
)
CERT_RE = re.compile(
    r"(EN ?17092[^\s,;]*|EN ?13594[^\s,;]*|EN ?13634[^\s,;]*|EN ?1621[^\s,;]*|"
    r"\bclass (?:AAA|AA|A|B|C)\b)",
    re.I,
)


# ── Small helpers ─────────────────────────────────────────────────────────────
def clean(text):
    return re.sub(r"\s+", " ", htmllib.unescape(text or "")).strip()


def strip_tags(html_text):
    return clean(re.sub(r"<[^>]+>", " ", html_text or ""))


def slugify(text):
    text = clean(text).lower().replace("®", "").replace("™", "")
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def products_of(data):
    """Accept a bare list or {"products": [...]}."""
    if isinstance(data, dict):
        return data.get("products", [])
    return data


# ── Catalog grouping (pure functions, tested offline) ────────────────────────
def is_us(product):
    return bool(US_TAGS & set(product.get("tags") or []))


def colour_of(product):
    for opt in product.get("options") or []:
        if (opt.get("name") or "").lower() in ("color", "colour") and opt.get("values"):
            return clean(opt["values"][0])
    title = product.get("title") or ""
    return clean(title.split(" | ", 1)[1]) if " | " in title else ""


def base_title(product):
    """Title with the colour removed.

    REV'IT! titles are "<Type word> <Model> | <Colour>" and the part after the
    pipe equals the single Color option value. When there is no pipe, fall back
    to removing a trailing colour value from the title.
    """
    title = clean(product.get("title"))
    if " | " in title:
        return clean(title.split(" | ", 1)[0])
    colour = colour_of(product)
    if colour and title.lower().endswith(colour.lower()):
        return clean(title[: -len(colour)]).rstrip("-| ").strip()
    return title


def model_key(product):
    return (clean(product.get("product_type")), base_title(product).lower())


def style_codes(product):
    return sorted(t for t in product.get("tags") or [] if t.startswith("PS-"))


def prefilter_hits(product):
    """Animal keyword hits in the title and body_html, one per term and field."""
    hits, seen = [], set()
    for where, text in (("title", clean(product.get("title"))),
                        ("body_html", strip_tags(product.get("body_html")))):
        for m in ANIMAL_RE.finditer(text):
            term = m.group(1).lower()
            if (term, where) in seen:
                continue
            seen.add((term, where))
            a = max(0, m.start() - 40)
            hits.append({"term": term, "where": where,
                         "handle": product.get("handle"),
                         "snippet": text[a:a + 80]})
    return hits


def colourway_record(product, base):
    variants = product.get("variants") or []
    return {
        "handle": product.get("handle"),
        "title": clean(product.get("title")),
        "colour": colour_of(product),
        "url": f"{base.rstrip('/')}/products/{product.get('handle')}",
        "price": variants[0].get("price") if variants else None,
        "available": any(v.get("available") for v in variants),
        "images": [i.get("src") for i in product.get("images") or [] if i.get("src")],
        "tags": list(product.get("tags") or []),
        "style_codes": style_codes(product),
        "outlet": "OutletUS" in (product.get("tags") or []),
    }


def pick_representative(colourways):
    def rank(item):
        i, cw = item
        colour = (cw["colour"] or "").lower()
        black = 0 if colour == "black" else 1 if "black" in colour else 2
        return (0 if cw["available"] else 1, black, i)
    return sorted(enumerate(colourways), key=rank)[0][1]


def build_models(products, base):
    """Group US-sellable products into models. Returns (models, doubts)."""
    us = [p for p in products if is_us(p)]
    groups = defaultdict(list)
    for p in us:
        groups[model_key(p)].append(p)

    models, slugs = [], Counter()
    for (ptype, _), items in groups.items():
        name = base_title(items[0])
        slugs[slugify(name)] += 1
    for (ptype, _), items in sorted(groups.items()):
        name = base_title(items[0])
        slug = slugify(name)
        if slugs[slug] > 1:
            slug = f"{slug}-{slugify(ptype)}"
        cws = [colourway_record(p, base) for p in items]
        tags = sorted({t for cw in cws for t in cw["tags"]})
        rep = pick_representative(cws)
        leather_tag = [cw["handle"] for cw in cws if "Leather" in cw["tags"]]
        hits = [h for p in items for h in prefilter_hits(p)]
        if leather_tag:
            status = "leather_tag"
        elif hits:
            status = "suspect"
        else:
            status = "candidate"
        models.append({
            "slug": slug,
            "model_name": name,
            "product_type": ptype,
            "gender_tags": [g for g in GENDER_TAGS if g in tags],
            "in_scope": ptype in IN_SCOPE_TYPES,
            "outlet": all(cw["outlet"] for cw in cws),
            "style_codes": sorted({c for cw in cws for c in cw["style_codes"]}),
            "representative": {k: rep[k] for k in ("handle", "url", "colour", "available", "price")},
            "colourways": cws,
            "tags": tags,
            "prefilter": {
                "status": status,
                "leather_tag_handles": leather_tag,
                "keyword_hits": hits,
            },
        })
    return models, find_doubts(models)


def find_doubts(models):
    """Groups that may be wrong: mixed style codes, a style code split across
    groups, mixed Leather tag, mixed gender tags, or a wide price spread."""
    doubts = []
    by_code = defaultdict(set)
    for m in models:
        for c in m["style_codes"]:
            by_code[c].add(m["slug"])
        reasons = []
        if len(m["style_codes"]) > 1:
            reasons.append("several style codes: " + ", ".join(m["style_codes"]))
        if not m["style_codes"]:
            reasons.append("no PS- style code tag to cross-check")
        lt = m["prefilter"]["leather_tag_handles"]
        if lt and len(lt) < len(m["colourways"]):
            reasons.append("Leather tag on some colourways only")
        genders = {tuple(g for g in GENDER_TAGS if g in cw["tags"]) for cw in m["colourways"]}
        if len(genders) > 1:
            reasons.append("gender tags differ between colourways")
        # Outlet colourways are a permanent 30% off, so compare like with like.
        for outlet in (False, True):
            prices = [float(cw["price"]) for cw in m["colourways"]
                      if cw["price"] and cw["outlet"] == outlet]
            if prices and max(prices) > 1.25 * min(prices):
                reasons.append(f"price spread {min(prices)} to {max(prices)}"
                               + (" (outlet)" if outlet else ""))
        if reasons:
            doubts.append({"slug": m["slug"], "reasons": reasons})
    for code, slugs in by_code.items():
        if len(slugs) > 1:
            doubts.append({"slug": ",".join(sorted(slugs)),
                           "reasons": [f"style code {code} split across groups"]})
    return doubts


def summarise(products, models):
    us = [p for p in products if is_us(p)]
    rows = defaultdict(Counter)
    for p in us:
        rows[clean(p.get("product_type"))]["us_products"] += 1
    for m in models:
        r = rows[m["product_type"]]
        r["models"] += 1
        if m["in_scope"]:
            r["in_scope"] += 1
            r[m["prefilter"]["status"]] += 1
    total = Counter()
    for r in rows.values():
        total.update(r)
    return rows, total


def print_summary(rows, total, doubts):
    cols = ["us_products", "models", "in_scope", "leather_tag", "suspect", "candidate"]
    print(f"{'product_type':<20}" + "".join(f"{c:>12}" for c in cols))
    for ptype in sorted(rows, key=lambda k: -rows[k]["us_products"]):
        scope = "" if ptype in IN_SCOPE_TYPES else " (out)"
        print(f"{(ptype + scope):<20}" + "".join(f"{rows[ptype][c]:>12}" for c in cols))
    print(f"{'TOTAL':<20}" + "".join(f"{total[c]:>12}" for c in cols))
    print(f"\nDoubtful groups: {len(doubts)}")
    for d in doubts:
        print(f"  {d['slug']}: {'; '.join(d['reasons'])}")


# ── Spec extractor (pure, tested offline) ────────────────────────────────────
def _soup(html_text):
    from bs4 import BeautifulSoup
    return BeautifulSoup(html_text, "html.parser")


def _accordion_lines(details):
    content = details.find(class_="disclosure__content") or details
    lines = []
    heads = content.find_all("h2")
    if heads:
        for h in heads:
            line = clean(h.get_text(" "))
            nxt = h.find_next_sibling()
            if nxt is not None and nxt.name == "p":
                extra = clean(nxt.get_text(" "))
                if extra:
                    line = f"{line}: {extra}"
            if line:
                lines.append(line)
        return lines
    for br in content.find_all("br"):
        br.replace_with("\n")
    for chunk in content.get_text("\n").split("\n"):
        chunk = clean(chunk)
        if chunk:
            lines.append(chunk)
    return lines


def extract_specs(html_text, url=""):
    s = _soup(html_text)
    title = clean(s.title.get_text()) if s.title else ""
    h1 = s.find("h1")
    out = {
        "url": url,
        "page_title": title,
        "is_404": "404" in title and "not found" in title.lower(),
        "canonical": "",
        "h1": clean(h1.get_text(" ")) if h1 else "",
        "description": "",
        "accordions": {},
        "certifications": [],
        "vegan_label": {"present": False, "quote": "", "sustainability": []},
        "vegan_mentions": [],
        "price": {"current": "", "original": "", "on_sale": False},
    }
    can = s.find("link", rel="canonical")
    if can and can.get("href"):
        out["canonical"] = can["href"]

    # Product block: Description disclosure outside the collapsible tabs.
    for d in s.find_all("details"):
        if d.find_parent(class_="collapsible-tabs"):
            continue
        summ = d.find("summary")
        if summ and clean(summ.get_text()).lower() == "description":
            content = d.find(class_="disclosure__content") or d
            for br in content.find_all("br"):
                br.replace_with("\n")
            paras = [clean(x) for x in content.get_text("\n").split("\n")]
            out["description"] = "\n".join(p for p in paras if p)
            break
    if not out["description"]:
        meta = s.find("meta", attrs={"name": "description"})
        if meta and meta.get("content"):
            out["description"] = clean(meta["content"])

    # "Specs and features" area: every accordion in .collapsible-tabs.
    tabs = s.find(class_="collapsible-tabs")
    if tabs:
        for d in tabs.find_all("details"):
            summ = d.find("summary")
            if not summ:
                continue
            head = clean(summ.get_text(" "))
            out["accordions"].setdefault(head, []).extend(_accordion_lines(d))

    # Certification lines: the certified block plus any standard in the specs.
    certs = []
    box = s.find(class_="wrap_certified_container")
    if box:
        for p in box.find_all("p"):
            t = clean(p.get_text(" "))
            if CERT_RE.search(t) or "certified" in t.lower():
                certs.append(t)
    for lines in out["accordions"].values():
        for line in lines:
            if CERT_RE.search(line):
                # keep the heading plus the sentence that names the standard
                head, _, rest = line.partition(": ")
                if CERT_RE.search(head):
                    certs.append(head)
                    continue
                sents = re.split(r"(?<=[.!?])\s+", rest)
                sent = next((x for x in sents if CERT_RE.search(x)), rest)
                certs.append(f"{head}: {sent}")
    out["certifications"] = list(dict.fromkeys(certs))

    # Vegan label under Sustainability, plus vegan mentions in product scope.
    sus = next((v for k, v in out["accordions"].items() if k.lower() == "sustainability"), [])
    out["vegan_label"]["sustainability"] = sus
    for line in sus:
        if re.search(r"\bvegan\b", line, re.I):
            out["vegan_label"]["present"] = True
            out["vegan_label"]["quote"] = line
            break
    scope_text = [("description", out["description"])] + [
        (k, line) for k, v in out["accordions"].items() for line in v
    ]
    for where, text in scope_text:
        for m in re.finditer(r"\bvegan\b|animal[- ]free", text, re.I):
            a = max(0, m.start() - 60)
            out["vegan_mentions"].append({"where": where, "quote": text[a:m.end() + 60]})

    # Price in the product block (first .product-info__price).
    pb = s.find(class_="product-info__price")
    if pb and not out["is_404"]:
        cur = pb.find(class_="price__current")
        was = pb.find(class_="price__was")
        out["price"]["current"] = clean(cur.get_text(" ")) if cur else ""
        out["price"]["original"] = clean(was.get_text(" ")) if was else ""
        out["price"]["on_sale"] = bool(out["price"]["original"])
    return out


# ── Network (one global pacer) ───────────────────────────────────────────────
class Pacer:
    """One request per `pause` seconds for the whole process. Shopify rate
    limits a visitor IP across all of its stores, so never parallelise."""

    def __init__(self, pause):
        self.pause = pause
        self.last = 0.0

    def wait(self):
        delta = time.monotonic() - self.last
        if delta < self.pause:
            time.sleep(self.pause - delta)
        self.last = time.monotonic()


def http_get(session, pacer, url, log=print):
    last_status, last_err = None, ""
    for attempt in range(1, MAX_TRIES + 1):
        pacer.wait()
        try:
            r = session.get(url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
        except Exception as e:  # network error: retry after a pause
            last_err = f"{type(e).__name__}: {e}"
            log(f"  error {last_err} (try {attempt}/{MAX_TRIES})")
            time.sleep(10 * attempt)
            continue
        last_status = r.status_code
        if r.status_code == 429:
            ra = r.headers.get("Retry-After", "")
            wait = int(ra) if ra.strip().isdigit() else DEFAULT_429_WAIT
            if attempt == MAX_TRIES:
                log(f"  429 on {url}, giving up (try {attempt}/{MAX_TRIES})")
                break
            log(f"  429 on {url}, sleeping {wait}s (try {attempt}/{MAX_TRIES})")
            time.sleep(wait)
            continue
        return r, ""
    return None, last_err or f"HTTP {last_status} after {MAX_TRIES} tries"


# ── Commands ─────────────────────────────────────────────────────────────────
def cmd_catalog(args):
    os.makedirs(args.out, exist_ok=True)
    if args.cache_json:
        products = products_of(load_json(args.cache_json))
        source = f"cache:{os.path.abspath(args.cache_json)}"
    else:
        import requests
        session, pacer = requests.Session(), Pacer(args.pause)
        products, page = [], 1
        while True:
            url = f"{args.base.rstrip('/')}/products.json?limit=250&page={page}"
            r, err = http_get(session, pacer, fetch_url)
            if r is None or r.status_code != 200:
                sys.exit(f"catalog fetch failed on page {page}: {err or r.status_code}")
            batch = r.json().get("products", [])
            print(f"page {page}: {len(batch)} products")
            if not batch:
                break
            products.extend(batch)
            page += 1
        source = f"{args.base.rstrip('/')}/products.json"
    save_json(os.path.join(args.out, "catalog.json"), {
        "base": args.base.rstrip("/"),
        "source": source,
        "saved_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "count": len(products),
        "products": products,
    })
    print(f"saved {len(products)} products to {os.path.join(args.out, 'catalog.json')}")


def cmd_models(args):
    cat = load_json(os.path.join(args.run, "catalog.json"))
    products = products_of(cat)
    base = cat.get("base") if isinstance(cat, dict) else args.base
    models, doubts = build_models(products, base)
    rows, total = summarise(products, models)
    save_json(os.path.join(args.run, "models.json"), {
        "base": base,
        "built_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "summary": {"total": dict(total), "by_type": {k: dict(v) for k, v in rows.items()}},
        "doubtful_groups": doubts,
        "models": models,
    })
    print_summary(rows, total, doubts)
    print(f"\nsaved {len(models)} models to {os.path.join(args.run, 'models.json')}")


def cmd_specs(args):
    import requests
    data = load_json(os.path.join(args.run, "models.json"))
    wanted = {s.strip() for s in args.only_status.split(",") if s.strip()}
    todo = [m for m in data["models"]
            if m["in_scope"] and m["prefilter"]["status"] in wanted]
    if args.only_slugs:
        with open(args.only_slugs) as fh:
            keep = {line.strip() for line in fh if line.strip()}
        todo = [m for m in todo if m["slug"] in keep]
    spec_dir = os.path.join(args.run, "specs")
    os.makedirs(spec_dir, exist_ok=True)
    session, pacer = requests.Session(), Pacer(args.pause)
    done = fetched = failed = streak = 0
    stats = Counter()
    for m in todo:
        if args.limit and fetched >= args.limit:
            break
        path = os.path.join(spec_dir, f"{m['slug']}.json")
        if os.path.exists(path):
            prev = load_json(path)
            if prev.get("http_status") in (200, 404):
                done += 1
                continue
        url = m["representative"]["url"]
        fetch_url = url + ("?sections=" + args.sections if args.sections else "")
        print(f"[{fetched + 1}] {m['slug']} <- {url}", flush=True)
        r, err = http_get(session, pacer, url)
        fetched += 1
        rec = {"model": m["model_name"], "slug": m["slug"], "product_type": m["product_type"],
               "prefilter_status": m["prefilter"]["status"], "url": url,
               "fetched_at": datetime.datetime.now().isoformat(timespec="seconds")}
        if r is None:
            rec.update({"http_status": None, "error": err})
            failed += 1
            streak += 1
            stats["error"] += 1
            save_json(path, rec)
            if streak >= args.max_fail_streak:
                print(f"\nstopping: {streak} models in a row failed ({err}). "
                      "Wait, then rerun (resumable), e.g. with --pause 4.", flush=True)
                break
            continue
        else:
            streak = 0
            rec["http_status"] = r.status_code
            rec["final_url"] = r.url
            if r.status_code == 200:
                html_text = r.text
                if args.sections:
                    # Section Rendering API: JSON of section id -> HTML (null if absent).
                    try:
                        parts = [v for v in r.json().values() if v]
                    except ValueError:
                        parts = []
                    rec["sections_found"] = len(parts)
                    html_text = "<html><body>" + "\n".join(parts) + "</body></html>"
                rec.update(extract_specs(html_text, url))
                stats["ok"] += 1
            else:
                stats[f"http_{r.status_code}"] += 1
        save_json(path, rec)
    print(f"\nspecs: {fetched} fetched this run, {done} already saved, "
          f"{failed} failed; {dict(stats)}; folder {spec_dir}")


def default_run(brand):
    return os.path.join(HERE, brand, TODAY)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("catalog")
    c.add_argument("--base", required=True, help="store base, e.g. https://revitsport.com/en-us")
    c.add_argument("--out", help="run folder (default discovery/<brand>/<today>)")
    c.add_argument("--brand", help="brand slug for the default run folder")
    c.add_argument("--cache-json", help="load this products list instead of fetching")
    c.add_argument("--pause", type=float, default=2.0)

    m = sub.add_parser("models")
    m.add_argument("--run", required=True)
    m.add_argument("--base", default="", help="only needed if catalog.json lacks it")

    s = sub.add_parser("specs")
    s.add_argument("--run", required=True)
    s.add_argument("--limit", type=int, default=0)
    s.add_argument("--only-status", default="candidate,suspect")
    s.add_argument("--sections", default="", help="comma list of section ids: fetch only "
                   "these sections (Section Rendering API) instead of the full page")
    s.add_argument("--only-slugs", help="file with one model slug per line; fetch only these")
    s.add_argument("--pause", type=float, default=2.0, help="seconds between requests")
    s.add_argument("--max-fail-streak", type=int, default=3,
                   help="stop after this many models in a row fail (429s, network)")

    args = ap.parse_args(argv)
    if args.cmd == "catalog":
        if not args.out:
            brand = args.brand or slugify(urlparse(args.base).hostname.split(".")[-2])
            args.out = default_run(brand)
        cmd_catalog(args)
    elif args.cmd == "models":
        cmd_models(args)
    elif args.cmd == "specs":
        cmd_specs(args)


if __name__ == "__main__":
    main()
