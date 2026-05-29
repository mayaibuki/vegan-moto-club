"""
export_revit_source.py
Export source material for description writing. For every Notion product that
matches a REV'IT! collection model (by name), dump page_id + name + cleaned
feature text (from Shopify body_html) to revit_source.json.

This feeds a human/Claude-authored description pass — no API needed.

Run: set -a && source ./.env.local && set +a && python3 "Scheduled audit/export_revit_source.py"
"""

import os, re, json, requests
from html.parser import HTMLParser
from notion_client import Client

H = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
n = Client(auth=os.environ["NOTION_API_KEY"])
db = os.environ["NOTION_PRODUCTS_DB_ID"]
DS = n.databases.retrieve(db)["data_sources"][0]["id"]
COLLECTION = "https://revitsport.com/en-us/collections/men-motorcycle-jackets"

def norm(s):
    return re.sub(r"[^a-z0-9 ]", "", s.lower()).strip()

PREFIX = re.compile(r"^(jacket|smock|jersey|overshirt|hoodie|sweater|one piece)\s+")
def core(s):
    return PREFIX.sub("", norm(s)).strip()

class Strip(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts = []
    def handle_data(self, d): self.parts.append(d)
    def text(self): return re.sub(r"\s+", " ", " ".join(self.parts)).strip()

def clean(html):
    s = Strip(); s.feed(html or ""); return s.text()

# 1. collection: name -> feature text
prods = requests.get(f"{COLLECTION}/products.json", params={"limit": 250},
                     headers=H, timeout=20).json()["products"]
by_full, by_core = {}, {}
for p in prods:
    base = re.sub(r"\s*\|\s*.*$", "", p["title"]).strip()
    txt = clean(p.get("body_html"))
    tags = ", ".join(p.get("tags") or [])
    rec = {"text": txt, "tags": tags}
    by_full.setdefault(norm(base), rec)
    c = PREFIX.sub("", norm(base)).strip()
    by_core[c] = None if c in by_core else rec

# 2. scan DB, match by name
pages, has_more, cursor = [], True, None
while has_more:
    kw = {"data_source_id": DS, "page_size": 100}
    if cursor: kw["start_cursor"] = cursor
    resp = n.data_sources.query(**kw)
    pages += resp["results"]; has_more = resp["has_more"]; cursor = resp.get("next_cursor")

out = []
for pg in pages:
    title = pg["properties"].get("Name of product", {}).get("title", [])
    if not title: continue
    name = title[0]["plain_text"]
    rec = by_full.get(norm(name)) or by_core.get(core(name))
    if rec is None: continue
    out.append({"page_id": pg["id"], "name": name,
                "tags": rec["tags"], "text": rec["text"][:1500]})

path = os.path.join(os.path.dirname(__file__), "revit_source.json")
with open(path, "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"Exported {len(out)} products to {path}")
