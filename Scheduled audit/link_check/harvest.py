#!/usr/bin/env python3
"""
harvest.py: store-link health check for the Vegan Moto Club products DB.

Read-only. Never writes to Notion. Stage 1 of the link audit:
  harvest.py -> agent review (Workflow) -> prices.py -> apply.py

For every product row it fetches the "View on Store" URL and records what a
shopper lands on: HTTP status, redirect chain, final URL, page title, JSON-LD
Product data, Shopify product data (.js + cart.js currency), meta prices,
stock / discontinued / bot-wall markers and a text excerpt. Each row gets a
health bucket:

  OK          200 on the same product URL
  REDIRECTED  200, but landed on a different path (renamed handle, listing...)
  HOMEPAGE    redirected to the store's homepage
  DEAD        404/410, no response, or a soft-404 page
  BLOCKED     403/429/5xx or a bot wall, even after a real-browser retry

OK/REDIRECTED rows with no product signals (or with soft-404 / listing
markers) are flagged `ambiguous` for agent triage.

Modes
  --all               snapshot every row, then harvest all of them
  --ids a,b,c         re-harvest only these page ids (into <run>/recheck/)
  --url URL           fetch one URL and print its digest JSON (used by agents)
  --search DOMAIN Q   Shopify store search, print candidates JSON (used by agents)
  --batches           split an existing run into agent batches

Run data goes to runs/<YYYY-MM-DD>/ (override with --run DIR).
ENV: NOTION_API_KEY, NOTION_PRODUCTS_DB_ID (read from the repo .env.local if unset)
"""
import os, re, sys, csv, json, time, argparse, threading, datetime
import concurrent.futures as cf
from collections import Counter, defaultdict
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
TODAY = datetime.date.today().isoformat()

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}
WORKERS = 10        # global concurrency
PER_DOMAIN = 1      # concurrent requests per host
DOMAIN_DELAY = 1.0  # seconds each request holds its host slot after finishing
TIMEOUT = 25
BACKOFF_429 = (20, 60, 120)  # host-wide pause before each retry after a 429
THROTTLE_STRIKES = 3         # requests still 429 after all retries before a host is skipped
BULK_MIN = 5                 # Shopify stores with this many rows download their catalog once
SHOPIFY_DELAY = 1.5          # seconds between requests to ANY Shopify store: Shopify
                             # rate-limits a visitor IP across all of its stores at once

BATCH_SIZE = {"match": 20, "triage": 25, "fix": 5}


# ── Env + Notion ──────────────────────────────────────────────────────────────
def load_env():
    path = os.path.join(REPO, ".env.local")
    if not os.path.exists(path):
        return
    for line in open(path):
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def notion():
    from notion_client import Client
    load_env()
    n = Client(auth=os.environ["NOTION_API_KEY"])
    ds = n.databases.retrieve(os.environ["NOTION_PRODUCTS_DB_ID"])["data_sources"][0]["id"]
    return n, ds


def all_rows(n, ds):
    rows, cursor = [], None
    while True:
        kw = {"data_source_id": ds, "page_size": 100}
        if cursor:
            kw["start_cursor"] = cursor
        r = n.data_sources.query(**kw)
        rows += r["results"]
        if not r.get("has_more"):
            break
        cursor = r["next_cursor"]
    return rows


def flatten(props):
    """Readable {field: value} view of a Notion page's properties."""
    out = {}
    for k, v in props.items():
        t = v.get("type")
        if t == "title":
            out[k] = "".join(r["plain_text"] for r in v["title"])
        elif t == "rich_text":
            out[k] = "".join(r["plain_text"] for r in v["rich_text"])
        elif t == "select":
            out[k] = (v["select"] or {}).get("name")
        elif t == "multi_select":
            out[k] = [o["name"] for o in v["multi_select"]]
        elif t in ("number", "url", "checkbox"):
            out[k] = v[t]
        else:
            out[k] = None
    return out


def snapshot_row(row):
    f = flatten(row["properties"])
    return {
        "page_id": row["id"],
        "name": f.get("Name of product") or "",
        "brand": f.get("Brand"),
        "url": f.get("URL") or "",
        "price": f.get("Price"),
        "category": f.get("Category") or [],
        "gender": f.get("Gender") or [],
        "vegan_verified": f.get("Vegan Verified"),
        "last_edited": row.get("last_edited_time"),
    }


# ── HTTP with per-host politeness ─────────────────────────────────────────────
_host_sems = defaultdict(lambda: threading.Semaphore(PER_DOMAIN))
_host_guard = threading.Lock()
_host_pause = {}          # host -> monotonic time before which nobody calls it
_host_strikes = Counter()
_host_prefix = {}         # host -> Shopify market folder seen on its pages ('/en-us' or '')
_catalogs = {}            # origin+folder -> {handle: product} from /products.json
_catalog_lock = threading.Lock()
_shopify_hosts = set()    # hosts that share the single "shopify" request slot
_currency = {}
_currency_lock = threading.Lock()


def host_of(url):
    return urlparse(url).netloc.lower()


def origin(url):
    p = urlparse(url)
    return f"{p.scheme}://{p.netloc}"


def http_get(url, timeout=TIMEOUT, **kw):
    """GET with per-host politeness. A 429 pauses that host for every thread and
    retries, so rate limiting is never mistaken for a broken link. Once a host
    stays 429 through THROTTLE_STRIKES full retry cycles it is skipped for the
    rest of the run; its rows come back THROTTLED (re-run with --resume)."""
    host = host_of(url)
    # Every Shopify store shares one slot: pacing, pauses and strikes apply platform-wide.
    key = "shopify" if host in _shopify_hosts else host
    delay = SHOPIFY_DELAY if key == "shopify" else DOMAIN_DELAY
    with _host_guard:
        sem = _host_sems[key]
    r, err = None, None
    for attempt in range(len(BACKOFF_429) + 1):
        if _host_strikes[key] >= THROTTLE_STRIKES:
            return None, "rate limited (429): store is throttling the checker"
        with sem:
            pause = _host_pause.get(key, 0) - time.monotonic()
            if pause > 0:
                time.sleep(pause)
            try:
                r, err = requests.get(url, headers=HEADERS, timeout=timeout,
                                      allow_redirects=True, **kw), None
            except Exception as e:
                r, err = None, f"{type(e).__name__}: {str(e)[:160]}"
            time.sleep(delay)
        if r is not None and host not in _shopify_hosts and any(
                k.lower().startswith(("x-shopify", "x-shopid")) for k in r.headers):
            with _host_guard:
                _shopify_hosts.add(host)
        if r is None or r.status_code != 429:
            return r, err
        ra = r.headers.get("retry-after") or ""
        wait = int(ra) if ra.isdigit() else BACKOFF_429[min(attempt, len(BACKOFF_429) - 1)]
        with _host_guard:
            _host_pause[key] = max(_host_pause.get(key, 0), time.monotonic() + wait)
    with _host_guard:
        _host_strikes[key] += 1
    return r, err


# ── Shopify ───────────────────────────────────────────────────────────────────
def shopify_handle(url):
    m = re.search(r"/products/([^/?#]+)", url or "")
    return m.group(1) if m else None


def shopify_prefix(url):
    """Shopify Markets locale folder in front of the product path (e.g. '/en-us'), or ''.
    REV'IT! prices its root domain in EUR and its /en-us/ market in USD, so the
    .js and cart.js calls must use the same folder as the page the shopper sees."""
    m = re.match(r"^(/[a-z]{2}(?:-[a-z]{2})?)/(?:collections/[^/]+/)?products/", urlparse(url or "").path, re.I)
    return m.group(1) if m else ""


def shopify_currency(url):
    o = origin(url) + shopify_prefix(url)
    with _currency_lock:
        if o in _currency:
            return _currency[o]
    cur = None
    r, _ = http_get(f"{o}/cart.js", timeout=15)
    if r is not None and r.status_code == 200:
        try:
            cur = r.json().get("currency")
        except Exception:
            pass
    with _currency_lock:
        _currency[o] = cur
    return cur


def shopify_product_js(url):
    h = shopify_handle(url)
    if not h:
        return None
    r, _ = http_get(f"{origin(url)}{shopify_prefix(url)}/products/{h}.js", timeout=20)
    # Shopify serves .js as text/javascript; an HTML body means no product endpoint.
    if r is None or r.status_code != 200 or r.text.lstrip()[:1] != "{":
        return None
    try:
        return r.json()
    except Exception:
        return None


def compact_shopify(p, currency):
    """Shopify /products/<handle>.js payload -> compact dict (prices in major units)."""
    if not p or not isinstance(p, dict):
        return None

    def money(c):
        return round(c / 100.0, 2) if isinstance(c, (int, float)) and c else None

    vs = p.get("variants") or []
    variants = [{
        "title": v.get("title"),
        "price": money(v.get("price")),
        "compare_at": money(v.get("compare_at_price")),
        "available": v.get("available"),
    } for v in vs[:4]]
    d = variants[0] if variants else {}
    regular = d.get("price")
    if d.get("compare_at") and d.get("price") and d["compare_at"] > d["price"]:
        regular = d["compare_at"]
    return {
        "title": p.get("title"),
        "vendor": p.get("vendor"),
        "type": p.get("type"),
        "handle": p.get("handle"),
        "available_any": p.get("available"),
        "currency": currency,
        "variant_count": len(vs),
        "variants": variants,
        "default_price": d.get("price"),
        "default_compare_at": d.get("compare_at"),
        "default_regular": regular,
    }


def shopify_catalog(purl):
    """Whole-store product list from /products.json, 250 per page. One download per
    store replaces a .js call per product, which keeps big Shopify stores (REV'IT!
    has ~160 of our rows) from rate-limiting the checker. None if unavailable."""
    key = origin(purl) + shopify_prefix(purl)
    with _catalog_lock:
        if key in _catalogs:
            return _catalogs[key]
    cat = {}
    for page in range(1, 30):
        r, _ = http_get(f"{key}/products.json", timeout=40, params={"limit": 250, "page": page})
        if r is None or r.status_code != 200 or r.text.lstrip()[:1] != "{":
            cat = cat or None
            break
        ps = r.json().get("products") or []
        for p in ps:
            cat[p.get("handle")] = p
        if len(ps) < 250:
            break
    with _catalog_lock:
        _catalogs[key] = cat
    return cat


def compact_catalog(p, currency):
    """/products.json product (prices are strings in major units) -> same shape as compact_shopify."""
    def money(s):
        try:
            v = float(s)
            return round(v, 2) if v else None
        except (TypeError, ValueError):
            return None

    vs = p.get("variants") or []
    variants = [{
        "title": v.get("title"),
        "price": money(v.get("price")),
        "compare_at": money(v.get("compare_at_price")),
        "available": v.get("available"),
    } for v in vs[:4]]
    d = variants[0] if variants else {}
    regular = d.get("price")
    if d.get("compare_at") and d.get("price") and d["compare_at"] > d["price"]:
        regular = d["compare_at"]
    return {
        "title": p.get("title"),
        "vendor": p.get("vendor"),
        "type": p.get("product_type"),
        "handle": p.get("handle"),
        "available_any": any(v.get("available") for v in vs),
        "currency": currency,
        "variant_count": len(vs),
        "variants": variants,
        "default_price": d.get("price"),
        "default_compare_at": d.get("compare_at"),
        "default_regular": regular,
        "source": "store catalog",
    }


def shopify_search(domain, query, limit=8):
    base = domain if domain.startswith("http") else f"https://{domain}"
    r, err = http_get(f"{base.rstrip('/')}/search/suggest.json", timeout=20, params={
        "q": query, "resources[type]": "product", "resources[limit]": limit})
    if r is None:
        return {"error": err}
    if r.status_code != 200 or "json" not in (r.headers.get("content-type") or "").lower():
        return {"error": f"HTTP {r.status_code}: not a Shopify store search endpoint; use WebSearch site:{host_of(base)}"}
    try:
        prods = r.json()["resources"]["results"]["products"]
    except Exception as e:
        return {"error": f"unexpected response: {e}"}
    o = origin(base)
    return {"results": [{
        "title": p.get("title"),
        "url": o + (p.get("url") or f"/products/{p.get('handle')}").split("?")[0],
        "price": p.get("price"),
        "compare_at_max": p.get("compare_at_price_max"),
        "available": p.get("available"),
        "vendor": p.get("vendor"),
    } for p in prods]}


# ── HTML parsing ──────────────────────────────────────────────────────────────
SOFT404_TITLE = re.compile(
    r"(\b404\b|not found|can[’']?t be found|cannot be found|could not be found|"
    r"doesn[’']?t exist|does not exist|no longer exists|page (?:is )?(?:missing|unavailable))", re.I)
SOFT404_TEXT = re.compile(
    r"(page (?:you (?:are|were|’re|'re) looking for|you requested) (?:is|was|could|can|does|cannot|can[’']?t)[^.]{0,40}|"
    r"page not found|we couldn[’']?t find (?:the|that) page|this page (?:no longer exists|doesn[’']?t exist))", re.I)
DISCONT = re.compile(
    r"(discontinued|no longer (?:available|produced|in production|sold|offered|carried|manufactured)|"
    r"end[ -]of[ -]line|retired (?:product|model|style))", re.I)
SOLDOUT = re.compile(
    r"(sold out|out of stock|currently unavailable|temporarily unavailable|notify me when|"
    r"email me when|back in stock)", re.I)
BOTWALL = re.compile(
    r"(access denied|access to this page has been denied|press (?:&|and) hold|are you a (?:human|robot)|"
    r"verify (?:that )?you are (?:a )?human|complete the captcha|just a moment\.\.\.|checking your browser|"
    r"pardon our interruption|request unsuccessful|attention required|ddos protection|"
    r"please enable (?:js|javascript) and disable any ad blocker)", re.I)
MONEY = re.compile(
    r"((?:US\$|CA\$|C\$|AU\$|A\$|NZ\$|\$|€|£|USD|EUR|GBP|AUD|CAD)\s?\d{1,3}(?:[,.]\d{3})*(?:[.,]\d{2})?"
    r"|\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?\s?(?:€|EUR|USD|GBP|AUD|CAD))")
LOCALE = re.compile(r"^/[a-z]{2}(?:[-_][a-z]{2})?(?:/[a-z]{2}(?:[-_][a-z]{2})?)?(?=/|$)", re.I)
HOME = ("", "/home", "/index.html", "/index.php", "/shop", "/store")
LISTING = re.compile(r"(^/collections(?:/|$)(?!.*products/)|/search\b|/category\b|/categories\b|/c/)", re.I)


def norm_path(url):
    """Comparable path: Shopify product handle if present, else the path with
    locale prefix, case and trailing slash removed."""
    path = urlparse(url or "").path.lower().rstrip("/")
    m = re.search(r"/products/([^/]+)", path)
    if m:
        return "products/" + m.group(1)
    return LOCALE.sub("", path).rstrip("/")


def snippets(rx, text, n=3, pad=60):
    out = []
    for m in rx.finditer(text or ""):
        s = text[max(0, m.start() - pad): m.end() + pad].strip()
        out.append(s)
        if len(out) >= n:
            break
    return out


def _walk(d):
    if isinstance(d, dict):
        yield d
        for v in d.values():
            for x in _walk(v):
                yield x
    elif isinstance(d, list):
        for v in d:
            for x in _walk(v):
                yield x


def _compact_ld(p):
    brand = p.get("brand")
    if isinstance(brand, dict):
        brand = brand.get("name")
    elif isinstance(brand, list):
        brand = ", ".join(b.get("name", "") if isinstance(b, dict) else str(b) for b in brand)
    offers = p.get("offers")
    offers = offers if isinstance(offers, list) else ([offers] if isinstance(offers, dict) else [])
    co = []
    for o in offers[:3]:
        if not isinstance(o, dict):
            continue
        e = {k: o.get(k) for k in ("@type", "price", "lowPrice", "highPrice", "priceCurrency", "availability")
             if o.get(k) not in (None, "")}
        spec = o.get("priceSpecification")
        specs = spec if isinstance(spec, list) else ([spec] if isinstance(spec, dict) else [])
        specs = [{k: s.get(k) for k in ("price", "priceCurrency", "priceType") if s.get(k) not in (None, "")}
                 for s in specs[:3] if isinstance(s, dict)]
        if specs:
            e["priceSpecification"] = specs
        co.append(e)
    return {"name": p.get("name"), "sku": p.get("sku") or p.get("mpn"), "brand": brand, "offers": co}


def jsonld_products(soup):
    out = []
    for s in soup.find_all("script", type=lambda t: t and "ld+json" in t.lower()):
        raw = (s.string or s.get_text() or "").strip()
        try:
            data = json.loads(raw)
        except Exception:
            try:
                data = json.loads(re.sub(r",\s*([}\]])", r"\1", raw))
            except Exception:
                continue
        for node in _walk(data):
            t = node.get("@type")
            types = t if isinstance(t, list) else [t]
            if any(x in ("Product", "ProductGroup", "IndividualProduct") for x in types if isinstance(x, str)):
                out.append(_compact_ld(node))
                if len(out) >= 3:
                    return out
    return out


def _meta(soup, *names):
    for nm in names:
        for attr in ("property", "name", "itemprop"):
            t = soup.find("meta", attrs={attr: nm})
            if t and t.get("content"):
                return t["content"].strip()
    return None


def parse_html(html):
    soup = BeautifulSoup(html or "", "html.parser")
    title = soup.title.get_text(" ", strip=True)[:200] if soup.title else ""
    h1 = soup.find("h1")
    h1 = h1.get_text(" ", strip=True)[:200] if h1 else ""
    canon = soup.find("link", rel=lambda v: v and "canonical" in (v if isinstance(v, list) else [v]))
    ld = jsonld_products(soup)
    meta_price = {
        "amount": _meta(soup, "og:price:amount", "product:price:amount", "price"),
        "currency": _meta(soup, "og:price:currency", "product:price:currency", "priceCurrency"),
    }
    page = {
        "title": title,
        "h1": h1,
        "og_title": _meta(soup, "og:title"),
        "og_type": _meta(soup, "og:type"),
        "canonical": canon.get("href") if canon else None,
        "availability_meta": _meta(soup, "product:availability", "og:availability"),
    }
    # <header> is kept: some themes wrap the product title + price in one.
    for tag in soup(["script", "style", "noscript", "svg", "iframe", "template", "footer", "nav"]):
        tag.decompose()
    root = soup.find("main") or soup.body or soup
    text = re.sub(r"\s+", " ", root.get_text(" ", strip=True))
    head = f"{title} {h1}"
    markers = {
        "soft404": snippets(SOFT404_TEXT, text) + ([title] if SOFT404_TITLE.search(head) else []),
        "discontinued": snippets(DISCONT, text),
        "soldout": snippets(SOLDOUT, text),
        "botwall": snippets(BOTWALL, head + " " + text[:3000]),
    }
    # Prices right after the product title come first: that is where a
    # struck-through regular price sits next to a sale price ("$299 $209.30 -30%").
    seen, prices = set(), []
    i = text.find(h1[:40]) if h1 else -1
    if i >= 0:
        win = text[i: i + 1500]
        for m in MONEY.finditer(win):
            s = "[near title] " + win[max(0, m.start() - 45): m.end() + 25].strip()
            if s not in seen:
                seen.add(s)
                prices.append(s)
            if len(prices) >= 5:
                break
    values = set()
    for m in MONEY.finditer(text[:20000]):
        v = m.group(1).strip()
        if v in values:
            continue
        values.add(v)
        prices.append(text[max(0, m.start() - 45): m.end() + 20].strip())
        if len(prices) >= 10:
            break
    return page, ld, (meta_price if meta_price["amount"] else None), markers, prices, text


# ── Bundle building ───────────────────────────────────────────────────────────
def new_bundle(row):
    return {
        "page_id": row.get("page_id"),
        "notion": {k: row.get(k) for k in ("name", "brand", "category", "gender", "vegan_verified", "url", "price")},
        "fetch": {},
        "page": {},
        "jsonld": [],
        "shopify": None,
        "meta_price": None,
        "markers": {"soft404": [], "discontinued": [], "soldout": [], "botwall": []},
        "price_snippets": [],
        "text": "",
        "bucket": None,
        "bucket_reason": "",
        "ambiguous": False,
        "fetched_at": datetime.datetime.now().isoformat(timespec="seconds"),
    }


def fill_from_html(b, html):
    page, ld, mp, markers, prices, text = parse_html(html)
    b["page"], b["jsonld"], b["meta_price"] = page, ld, mp
    b["markers"], b["price_snippets"], b["text"] = markers, prices, text[:3000]
    b["text_len"] = len(text)


def has_product_data(b):
    return bool(b["jsonld"] or b["shopify"] or b["meta_price"]
                or (b["page"].get("og_type") or "").lower().startswith("product"))


def bucketize(b):
    f, pg = b["fetch"], b["page"]
    st = f.get("status")
    orig = b["notion"]["url"]
    final = f.get("final_url") or orig
    prod = has_product_data(b)
    head = f"{pg.get('title', '')} {pg.get('h1', '')}"
    if st == 429 or (st is None and (f.get("error") or "").startswith("rate limited")):
        if b["shopify"]:
            return "OK", "page throttled, but the store's product data confirms the product is live"
        return "THROTTLED", "store rate-limited the checker; re-run harvest.py --all --resume"
    if st is None:
        return "DEAD", f"no response ({f.get('error')})"
    if st in (404, 410):
        return "DEAD", f"HTTP {st}"
    if st in (401, 403, 429) or st >= 500 or (b["markers"]["botwall"] and not prod):
        if b["shopify"]:
            return "OK", f"page HTTP {st} to scripts, but the Shopify product endpoint confirms the product"
        return "BLOCKED", f"HTTP {st}" + (" + bot wall" if b["markers"]["botwall"] else "")
    if st >= 400:
        return "DEAD", f"HTTP {st}"
    if norm_path(final) in HOME and norm_path(orig) not in HOME:
        return "HOMEPAGE", f"redirected to {final}"
    if SOFT404_TITLE.search(head) and not prod:
        return "DEAD", f"soft 404: {head.strip()[:100]}"
    if norm_path(final) != norm_path(orig):
        return "REDIRECTED", f"landed on {final}"
    return "OK", ""


def classify(b):
    b["bucket"], b["bucket_reason"] = bucketize(b)
    listing = bool(LISTING.search(urlparse(b["fetch"].get("final_url") or "").path))
    b["landed_on_listing"] = listing
    b["ambiguous"] = b["bucket"] in ("OK", "REDIRECTED") and (
        not has_product_data(b) or bool(b["markers"]["soft404"]) or listing)
    return b


def needs_browser(b):
    st = b["fetch"].get("status")
    if b["fetch"].get("method") in ("playwright", "catalog"):
        return False  # already rendered in a browser, or confirmed by the store catalog
    if b["bucket"] == "THROTTLED":
        return False  # a browser would get the same 429; retry later with --resume
    if b["bucket"] == "BLOCKED" or st is None:
        return True
    if 300 <= st < 400:
        return True  # a JS or meta redirect page that requests could not follow
    if b["ambiguous"]:
        return True  # JS-rendered shell, soft-404 wording or a listing: let a real browser look
    return False


def harvest_requests(row, bulk=False):
    """Plain HTTP for the page, plus Shopify product data when the URL is a product
    handle: from the store catalog for big stores (bulk=True), else from <handle>.js."""
    b = new_bundle(row)
    url = row["url"]
    if not url:
        b["fetch"] = {"method": "none", "status": None, "error": "no URL on row"}
        return classify(b)
    # Big Shopify stores: a handle listed in the store catalog is a live product page,
    # so the page request is skipped (the per-product requests are what trigger 429s).
    h0 = shopify_handle(url)
    if bulk and h0:
        pre = _host_prefix.get(host_of(url), shopify_prefix(url))
        purl = f"{origin(url)}{pre}/products/{h0}"
        cat = shopify_catalog(purl)
        if cat and h0 in cat:
            b["shopify"] = compact_catalog(cat[h0], shopify_currency(purl))
            b["fetch"] = {"method": "catalog", "status": 200, "final_url": url, "chain": []}
            b["page"] = {"title": b["shopify"]["title"], "h1": b["shopify"]["title"]}
            return classify(b)
    r, err = http_get(url)
    ok = r is not None and r.status_code == 200
    if r is None:
        b["fetch"] = {"method": "requests", "status": None, "error": err, "final_url": None, "chain": []}
    else:
        b["fetch"] = {
            "method": "requests",
            "status": r.status_code,
            "final_url": r.url,
            "chain": [h.url for h in r.history] + [r.url] if r.history else [],
        }
        ctype = (r.headers.get("content-type") or "").lower()
        if "html" in ctype or not ctype:
            fill_from_html(b, r.text)
    # Shopify data comes from the URL the shopper lands on: that keeps the market
    # folder (USD on /en-us/) and follows renamed handles. When the page itself is
    # blocked or throttled, reuse the market folder seen on the store's other pages.
    src = r.url if ok else url
    h = shopify_handle(src)
    if h:
        if ok:
            pre = shopify_prefix(src)
            _host_prefix.setdefault(host_of(src), pre)
        else:
            pre = _host_prefix.get(host_of(src), shopify_prefix(src))
        purl = f"{origin(src)}{pre}/products/{h}"
        cat = shopify_catalog(purl) if bulk else None
        if cat and h in cat:
            b["shopify"] = compact_catalog(cat[h], shopify_currency(purl))
        else:
            p = shopify_product_js(purl)
            if p:
                b["shopify"] = compact_shopify(p, shopify_currency(purl))
    return classify(b)


JS_SHOPIFY = """async ([h, pre]) => {
  try {
    const r = await fetch(location.origin + pre + '/products/' + h + '.js');
    if (!r.ok) return null;
    const p = await r.json();
    let cur = null;
    try { const c = await fetch(location.origin + pre + '/cart.js'); if (c.ok) cur = (await c.json()).currency || null; } catch (e) {}
    return {p: p, cur: cur};
  } catch (e) { return null; }
}"""


def harvest_browser(bundles, log=print, save=None):
    """Retry rows in a plain headless Chromium (renders JS pages). No stealth tricks:
    a page that still shows a bot wall stays BLOCKED."""
    if not bundles:
        return
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        br = p.chromium.launch(headless=True)
        ctx = br.new_context(locale="en-US", viewport={"width": 1366, "height": 900})
        page = ctx.new_page()
        for i, b in enumerate(bundles, 1):
            url = b["notion"]["url"]
            before = b["bucket"]
            try:
                resp = page.goto(url, wait_until="domcontentloaded", timeout=45000)
                page.wait_for_timeout(3500)
                chain, req = [], (resp.request if resp else None)
                while req is not None:
                    chain.insert(0, req.url)
                    req = req.redirected_from
                b["fetch"] = {"method": "playwright", "status": resp.status if resp else None,
                              "final_url": page.url, "chain": chain if len(chain) > 1 else []}
                fill_from_html(b, page.content())
                h = shopify_handle(page.url) or shopify_handle(url)
                if h and not b["shopify"]:
                    got = page.evaluate(JS_SHOPIFY, [h, shopify_prefix(page.url)])
                    if got and got.get("p"):
                        b["shopify"] = compact_shopify(got["p"], got.get("cur"))
            except Exception as e:
                b["fetch"] = dict(b["fetch"], method="playwright",
                                  browser_error=f"{type(e).__name__}: {str(e)[:160]}")
            classify(b)
            if save:
                save(b)
            log(f"  [browser {i:>3}/{len(bundles)}] {before:>10} -> {b['bucket']:<10} {url[:90]}")
            time.sleep(1.0)
        br.close()


def digest(b):
    """Compact view for agents (what they need to judge health, match and price)."""
    return {
        "page_id": b.get("page_id"),
        "notion": b["notion"],
        "health": {
            "bucket": b["bucket"], "reason": b["bucket_reason"], "ambiguous": b["ambiguous"],
            "status": b["fetch"].get("status"), "method": b["fetch"].get("method"),
            "final_url": b["fetch"].get("final_url"), "redirect_chain": b["fetch"].get("chain") or [],
            "landed_on_listing": b.get("landed_on_listing"),
            "error": b["fetch"].get("error") or b["fetch"].get("browser_error"),
        },
        "page": b["page"],
        "product_data": {"jsonld": b["jsonld"], "shopify": b["shopify"], "meta_price": b["meta_price"]},
        "markers": b["markers"],
        "price_snippets": b["price_snippets"],
        "text": (b["text"] or "")[:1800],
    }


# ── Run orchestration ─────────────────────────────────────────────────────────
def save_bundle(b, out_dir):
    pid = b["page_id"].replace("-", "")
    json.dump(b, open(os.path.join(out_dir, "bundles", f"{pid}.json"), "w"), indent=1, ensure_ascii=False)
    json.dump(digest(b), open(os.path.join(out_dir, "digests", f"{pid}.json"), "w"), indent=1, ensure_ascii=False)


def load_bundles(out_dir):
    d = os.path.join(out_dir, "bundles")
    if not os.path.isdir(d):
        return {}
    return {f[:-5]: json.load(open(os.path.join(d, f))) for f in os.listdir(d) if f.endswith(".json")}


def harvest_rows(rows, out_dir, log=print, browser=True):
    os.makedirs(os.path.join(out_dir, "bundles"), exist_ok=True)
    os.makedirs(os.path.join(out_dir, "digests"), exist_ok=True)
    by_host = defaultdict(list)
    for r in rows:
        by_host[host_of(r["url"] or "")].append(r)
    bulk = {h for h, rs in by_host.items() if sum(1 for r in rs if shopify_handle(r["url"])) >= BULK_MIN}
    for h, rs in by_host.items():
        if any(shopify_handle(r["url"]) for r in rs) or h.endswith("revitsport.com"):
            _shopify_hosts.add(h)
        # Market folder from the rows' own URLs (REV'IT! -> /en-us), so catalog
        # prices come back in USD even before any page on that store is fetched.
        pres = Counter(shopify_prefix(r["url"]) for r in rs if shopify_prefix(r["url"]))
        if pres:
            _host_prefix.setdefault(h, pres.most_common(1)[0][0])
    bundles, lock, t0 = [], threading.Lock(), time.time()

    def work(host_rows):
        host, rs = host_rows
        for r in rs:
            try:
                b = harvest_requests(r, bulk=host in bulk)
            except Exception as e:
                b = new_bundle(r)
                b["fetch"] = {"method": "requests", "status": None, "error": f"crash: {e}"}
                classify(b)
            with lock:
                bundles.append(b)
                save_bundle(b, out_dir)
                n = len(bundles)
            if n % 25 == 0 or n == len(rows):
                log(f"  [http {n:>3}/{len(rows)}] {time.time() - t0:5.0f}s")

    # One worker per store, biggest stores first: a throttled store only stalls its own queue.
    log(f"  {len(by_host)} stores; catalog download for {sorted(bulk)}")
    with cf.ThreadPoolExecutor(max_workers=WORKERS) as ex:
        list(ex.map(work, sorted(by_host.items(), key=lambda kv: -len(kv[1]))))
    if browser:
        retry = [b for b in bundles if needs_browser(b)]
        log(f"Browser retry for {len(retry)} rows")
        harvest_browser(retry, log, save=lambda b: save_bundle(b, out_dir))
    everything = list(load_bundles(out_dir).values())
    write_health(everything, out_dir)
    th = sum(1 for b in everything if b["bucket"] == "THROTTLED")
    if th:
        log(f"{th} rows THROTTLED: wait a few minutes, then run harvest.py --all --resume")
    return bundles


def write_health(bundles, out_dir):
    with open(os.path.join(out_dir, "health.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["page_id", "brand", "name", "host", "bucket", "ambiguous", "status", "method",
                    "final_url", "reason", "notion_price", "shopify_regular", "shopify_currency",
                    "ld_price", "ld_currency"])
        for b in sorted(bundles, key=lambda x: (x["notion"].get("brand") or "", x["notion"].get("name") or "")):
            sh = b["shopify"] or {}
            off = (b["jsonld"][0]["offers"][0] if b["jsonld"] and b["jsonld"][0].get("offers") else {})
            w.writerow([b["page_id"], b["notion"].get("brand"), b["notion"].get("name"),
                        host_of(b["notion"].get("url") or ""), b["bucket"], b["ambiguous"],
                        b["fetch"].get("status"), b["fetch"].get("method"), b["fetch"].get("final_url"),
                        b["bucket_reason"], b["notion"].get("price"), sh.get("default_regular"),
                        sh.get("currency"), off.get("price") or off.get("lowPrice"), off.get("priceCurrency")])
    by = defaultdict(Counter)
    for b in bundles:
        by[host_of(b["notion"].get("url") or "")][b["bucket"] + ("*" if b["ambiguous"] else "")] += 1
    lines = ["host | total | buckets (* = ambiguous)"]
    for h, c in sorted(by.items(), key=lambda kv: -sum(kv[1].values())):
        lines.append(f"{h} | {sum(c.values())} | " + ", ".join(f"{k}={v}" for k, v in sorted(c.items())))
    tot = Counter(b["bucket"] for b in bundles)
    lines.append("TOTAL | " + str(len(bundles)) + " | " + ", ".join(f"{k}={v}" for k, v in sorted(tot.items()))
                 + f", ambiguous={sum(1 for b in bundles if b['ambiguous'])}")
    open(os.path.join(out_dir, "health_summary.txt"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))


def make_batches(run):
    bdir = os.path.join(run, "bundles")
    bundles = [json.load(open(os.path.join(bdir, f))) for f in sorted(os.listdir(bdir)) if f.endswith(".json")]
    key = lambda b: ((b["notion"].get("brand") or "").lower(), (b["notion"].get("name") or "").lower())
    groups = {
        "match": [b for b in bundles if b["bucket"] in ("OK", "REDIRECTED") and not b["ambiguous"]],
        "triage": [b for b in bundles if b["ambiguous"] or b["bucket"] in ("BLOCKED", "THROTTLED")],
        "fix": [b for b in bundles if b["bucket"] in ("DEAD", "HOMEPAGE")],
    }
    out_dir = os.path.join(run, "batches")
    os.makedirs(out_dir, exist_ok=True)
    index = {}
    for kind, items in groups.items():
        items.sort(key=key)
        size = BATCH_SIZE[kind]
        index[kind] = []
        for i in range(0, len(items), size):
            chunk = items[i:i + size]
            label = f"{kind}-{i // size + 1:02d}"
            path = os.path.join(out_dir, f"{label}.json")
            json.dump([digest(b) for b in chunk], open(path, "w"), indent=1, ensure_ascii=False)
            index[kind].append({"label": label, "path": path,
                                "ids": [b["page_id"] for b in chunk],
                                "brands": sorted({b["notion"].get("brand") or "?" for b in chunk})})
    json.dump(index, open(os.path.join(out_dir, "index.json"), "w"), indent=1)
    print({k: f"{len(groups[k])} rows / {len(v)} batches" for k, v in index.items()})


def _price_shown(b, value):
    """Does the fetched page show this price (meta price or a price snippet)?"""
    if value is None:
        return False
    targets = {f"{value:.2f}", f"{value:,.2f}"}
    if float(value).is_integer():
        targets |= {f"{int(value)}", f"{int(value):,}"}
    hay = [(b.get("meta_price") or {}).get("amount") or ""] + list(b.get("price_snippets") or [])
    return any(t in s.replace(" ", "") for s in hay for t in targets)


def enrich(run, log=print):
    """Second pass over saved bundles, closing two gaps the big-store shortcuts leave:
    1. Shopify data without a currency (browser path): read it from the store's cart.js.
    2. Catalog-only rows (no page text) whose price differs from Notion: fetch the page.
       Some stores (REV'IT!) show a sale only on the page ("$1,029.99 USD $720.99 USD"),
       never as a Shopify compare-at price, so the page is the only proof of the regular
       price. A catalog price the US page does not show (product not sold in that
       market) is dropped so nobody copies it into Notion."""
    bundles = load_bundles(run)
    by_host = defaultdict(list)
    for b in bundles.values():
        by_host[host_of(b["notion"]["url"] or "")].append(b)
    for h, bs in by_host.items():
        if any(x["shopify"] for x in bs) or h.endswith("revitsport.com"):
            _shopify_hosts.add(h)
        pres = Counter(shopify_prefix(x["fetch"].get("final_url") or x["notion"]["url"]) for x in bs)
        pres.pop("", None)
        if pres:
            _host_prefix.setdefault(h, pres.most_common(1)[0][0])
    cur_fixed = checked = dropped = 0
    for b in bundles.values():
        sh = b["shopify"]
        if not sh:
            continue
        url = b["fetch"].get("final_url") or b["notion"]["url"]
        pre = shopify_prefix(url) or _host_prefix.get(host_of(url), "")
        market = f"{origin(url)}{pre}/products/{shopify_handle(url) or sh.get('handle')}"
        changed = False
        if not sh.get("currency"):
            sh["currency"] = shopify_currency(market)
            cur_fixed += bool(sh["currency"])
            changed = True
        reg, old = sh.get("default_regular"), b["notion"].get("price")
        if b["fetch"].get("method") == "catalog" and reg and old and abs(reg - old) >= 1:
            r, _ = http_get(market)
            page_ok = r is not None and r.status_code == 200
            if page_ok:
                fill_from_html(b, r.text)
                b["page"]["title"] = b["page"].get("title") or sh.get("title")
                b["fetch"]["page_checked"] = market
            if not _price_shown(b, sh.get("default_price")):
                for k in ("default_price", "default_compare_at", "default_regular"):
                    sh[k] = None
                sh["variants"] = [{"title": v.get("title"), "available": v.get("available")}
                                  for v in sh.get("variants") or []]
                sh["price_note"] = ("store catalog price is not shown on the store's US page; ignore it"
                                    if page_ok else "store page could not be fetched to confirm the catalog price; ignore it")
                dropped += 1
            classify(b)
            checked += 1
            changed = True
        if changed:
            save_bundle(b, run)
    write_health(list(bundles.values()), run)
    log(f"enrich: currency filled on {cur_fixed}, pages checked {checked}, catalog prices dropped {dropped}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--ids", default="")
    ap.add_argument("--url", default="")
    ap.add_argument("--search", nargs=2, metavar=("DOMAIN", "QUERY"))
    ap.add_argument("--batches", action="store_true")
    ap.add_argument("--enrich", action="store_true",
                    help="fill missing Shopify currencies and page-check catalog prices that differ from Notion")
    ap.add_argument("--run", default="", help="run folder; only --all may omit it (defaults to runs/<today>)")
    ap.add_argument("--limit", type=int, default=0, help="harvest only the first N rows (testing)")
    ap.add_argument("--hosts", default="", help="comma-separated hosts to include (testing)")
    ap.add_argument("--per-host", type=int, default=0, dest="per_host", help="keep at most N rows per host (testing)")
    ap.add_argument("--no-browser", action="store_true", dest="no_browser")
    ap.add_argument("--resume", action="store_true",
                    help="with --all: only rows not yet harvested, or THROTTLED / BLOCKED / unanswered")
    args = ap.parse_args()
    if not args.run and not (args.search or args.url):
        if args.all and not args.resume:
            args.run = os.path.join(HERE, "runs", TODAY)
        else:
            ap.error("pass --run runs/<date>: a date default would switch folders at midnight")

    if args.search:
        print(json.dumps(shopify_search(*args.search), indent=1, ensure_ascii=False))
        return
    if args.url:
        b = harvest_requests({"page_id": None, "url": args.url})
        if needs_browser(b) and not args.no_browser:
            harvest_browser([b], log=lambda m: print(m, file=sys.stderr))
        print(json.dumps(digest(b), indent=1, ensure_ascii=False))
        return
    if args.enrich:
        enrich(args.run)
        return
    if args.batches:
        make_batches(args.run)
        return
    if not (args.all or args.ids):
        ap.error("choose a mode: --all / --ids / --url / --search / --batches")

    os.makedirs(args.run, exist_ok=True)
    n, ds = notion()
    print("Fetching all rows from Notion...", flush=True)
    raw = [r for r in all_rows(n, ds) if not (r.get("archived") or r.get("in_trash"))]
    rows = [snapshot_row(r) for r in raw]
    rows = [r for r in rows if not r["name"].startswith("User Suggestion -")]
    print(f"  {len(rows)} product rows", flush=True)

    if args.all:
        snap = os.path.join(args.run, "snapshot.json")
        if not os.path.exists(snap):  # never overwrite the pre-change snapshot
            json.dump(rows, open(snap, "w"), indent=1, ensure_ascii=False)
            print(f"  snapshot -> {snap}")
        out_dir = args.run
        if args.resume:
            have = load_bundles(out_dir)

            def pending(r):
                b = have.get(r["page_id"].replace("-", ""))
                return (b is None or b["bucket"] in ("THROTTLED", "BLOCKED")
                        or b["fetch"].get("status") is None or needs_browser(b))
            rows = [r for r in rows if pending(r)]
    else:
        want = {i.strip().replace("-", "") for i in args.ids.split(",") if i.strip()}
        rows = [r for r in rows if r["page_id"].replace("-", "") in want]
        out_dir = os.path.join(args.run, "recheck")
    if args.hosts:
        hs = {h.strip().lower() for h in args.hosts.split(",")}
        rows = [r for r in rows if host_of(r["url"]) in hs]
    if args.per_host:
        seen = Counter()
        keep = []
        for r in rows:
            h = host_of(r["url"])
            if seen[h] < args.per_host:
                keep.append(r)
                seen[h] += 1
        rows = keep
    if args.limit:
        rows = rows[: args.limit]
    print(f"Harvesting {len(rows)} rows -> {out_dir}", flush=True)
    harvest_rows(rows, out_dir, log=lambda m: print(m, flush=True), browser=not args.no_browser)


if __name__ == "__main__":
    main()
