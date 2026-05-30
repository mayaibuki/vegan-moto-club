"""Inspect Notion schema options + existing REV'IT glove entries."""
import os
from notion_client import Client

n = Client(auth=os.environ["NOTION_API_KEY"])
DB = os.environ["NOTION_PRODUCTS_DB_ID"]
DS = n.databases.retrieve(DB)["data_sources"][0]["id"]
props = n.data_sources.retrieve(data_source_id=DS)["properties"]

for name in ["Category", "Level of Protection", "Level of Waterproof", "Riding style", "Season", "Materials", "Gender", "Brand", "Vegan Verified"]:
    p = props.get(name)
    if not p:
        print(f"[MISSING] {name}"); continue
    t = p["type"]
    opts = [o["name"] for o in p[t].get("options", [])] if t in ("select", "multi_select") else t
    print(f"{name} ({t}): {opts}")

# Existing gloves
print("\n=== EXISTING GLOVE ENTRIES ===")
res = n.data_sources.query(data_source_id=DS, filter={"property": "Category", "multi_select": {"contains": "Gloves"}})
for r in res["results"]:
    title = r["properties"]["Name of product"]["title"]
    nm = title[0]["plain_text"] if title else "(untitled)"
    url = r["properties"].get("URL", {}).get("url", "")
    print(f"  {nm}  |  {url}")
