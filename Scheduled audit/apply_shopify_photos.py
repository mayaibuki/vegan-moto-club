import os, json
from notion_client import Client

n = Client(auth=os.environ["NOTION_API_KEY"])
db = os.environ["NOTION_PRODUCTS_DB_ID"]
DS = n.databases.retrieve(db)["data_sources"][0]["id"]

data = json.load(open("Scheduled audit/resolved_shopify.json"))
# low-confidence matches manually verified correct -> approved for write
ACCEPT_LOW = {
    "26bb6886-a574-4d71-b7ab-0a41739b4d1e",  # SMX 6 v2 -> SMX-6 V2 Drystar boots
    "23462c99-eba4-4e3d-8ee2-83734532477b",  # Stella Faster 3 Drystar -> Stella Faster-3 shoes
    "14760fc1-4ea5-43d9-ac03-f08d0e66af5c",  # Whitby -> REV'IT Sweater Whitby
    "d41c41dd-1b50-48d9-bf0b-20cd0733d27d",  # Fury V Jeggings -> Ladies Fury skinny jeans
    "0279ea56-7986-4bf1-9a08-8a57067565ee",  # RokkerTech -> ROKKERTECH Mid Straight
}
hi = [o for o in data if o.get("imgs_ok") and
      (o.get("conf") == "high" or o["pid"] in ACCEPT_LOW)]
print("applying photos to", len(hi), "products\n")

for o in hi:
    imgs = o["imgs_ok"][:8]
    name = o["name"][:90]
    files = [{"type": "external", "name": name, "external": {"url": u}} for u in imgs]
    n.pages.update(page_id=o["pid"], properties={"Photos": {"files": files}})
    print(f'  {o["name"]:<45} {len(imgs)} photos  ({o["used"]})')

print("\nDONE")
