"""Strip leading category word ('Pants '/'Gloves '/'Shoes '/'Jacket(s) ')
from product names. Dry-run first unless APPLY=1."""
import os, time
from notion_client import Client

n = Client(auth=os.environ["NOTION_API_KEY"])
DB = os.environ["NOTION_PRODUCTS_DB_ID"]
DS = n.databases.retrieve(DB)["data_sources"][0]["id"]
APPLY = os.environ.get("APPLY") == "1"

PREFIXES = ("Pants ", "Gloves ", "Shoes ", "Jackets ", "Jacket ", "Boots ", "Heated Gloves ")

# paginate full DB
results, cursor = [], None
while True:
    kw = {"data_source_id": DS, "page_size": 100}
    if cursor: kw["start_cursor"] = cursor
    r = n.data_sources.query(**kw)
    results += r["results"]
    if not r.get("has_more"): break
    cursor = r["next_cursor"]

changes = 0
for row in results:
    t = row["properties"]["Name of product"]["title"]
    nm = t[0]["plain_text"] if t else ""
    new = nm
    for pre in PREFIXES:
        if nm.startswith(pre):
            new = nm[len(pre):]
            break
    new = new.strip()  # also fixes stray leading/trailing whitespace
    if new != nm and new:
        print(f"'{nm}'  ->  '{new}'")
        changes += 1
        if APPLY:
            n.pages.update(page_id=row["id"], properties={
                "Name of product": {"title": [{"text": {"content": new}}]}})
            time.sleep(0.35)

print(f"\n{'APPLIED' if APPLY else 'DRY-RUN'}: {changes} names to rename")
