"""Print Riding style / Season / Materials / Category options + list existing jeans-ish rows."""
import os, json
from notion_client import Client

n = Client(auth=os.environ["NOTION_API_KEY"])
DB = os.environ["NOTION_PRODUCTS_DB_ID"]
DS = n.databases.retrieve(DB)["data_sources"][0]["id"]
schema = n.data_sources.retrieve(DS)["properties"]

for field in ["Riding style", "Season", "Category", "Level of Protection", "Level of Waterproof"]:
    p = schema.get(field, {})
    kind = p.get("type")
    opts = p.get(kind, {}).get("options", []) if kind in ("select", "multi_select") else []
    print(f"\n{field} ({kind}): {[o['name'] for o in opts]}")

# Materials (just print so I can match)
mp = schema.get("Materials", {})
print(f"\nMaterials: {[o['name'] for o in mp.get('multi_select', {}).get('options', [])]}")

# existing rows whose name suggests jeans/chino/leggings/worker/cargo
results, cursor = [], None
while True:
    kw = {"data_source_id": DS, "page_size": 100}
    if cursor: kw["start_cursor"] = cursor
    r = n.data_sources.query(**kw)
    results += r["results"]
    if not r.get("has_more"): break
    cursor = r["next_cursor"]

print(f"\nTotal rows: {len(results)}")
names = []
for row in results:
    t = row["properties"]["Name of product"]["title"]
    names.append(t[0]["plain_text"] if t else "")
hits = [x for x in names if any(k in x.lower() for k in ["jean","chino","legging","worker","cargo","moto","carlin","detroit","piston","lombard","ortes","micah","keegan","rilan","lewis","brant","dean","mason","davis","terry","ellison","talia","harper","violet","marzia","shelby"])]
print("Possible existing jeans matches:", hits)
