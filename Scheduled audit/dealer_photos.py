import os, requests
from notion_client import Client

n = Client(auth=os.environ["NOTION_API_KEY"])
db = os.environ["NOTION_PRODUCTS_DB_ID"]
H = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}

def norm(u):
    return "https:" + u if u.startswith("//") else u

def images(base, handle):
    r = requests.get(f"{base}/products/{handle}.js", headers=H, timeout=15)
    if r.status_code != 200:
        return []
    d = r.json()
    return [norm(i["src"] if isinstance(i, dict) else i) for i in d.get("images", [])]

def ok(u):
    try:
        r = requests.head(u, headers=H, timeout=12, allow_redirects=True)
        if r.status_code in (403, 405):
            r = requests.get(u, headers=H, timeout=15, stream=True)
        return r.status_code == 200
    except Exception:
        return False

# (pid, name, dealer base, handle) -- each manually verified to be the correct product
MAP = [
    ("fad2f823-1f49-4b8c-9b44-8fd7cc99f7c1", "SIDI ST Air", "https://motorcyclegear.com", "sidi-st-air-boots"),
    ("c11fc548-5554-4e09-9850-85c633ac2164", "Twenty-Niner", "https://motorcyclegear.com", "icon-womens-twenty-niner-gloves"),
    ("994eb371-78ea-4902-a39e-4ccf7da4191e", "Skrub Women's Gloves", "https://motorcyclegear.com", "scorpion-exo-skrub-ii-gloves-for-women"),
    ("57e488ee-8b6f-4cb8-a1f8-c369f02dee83", "Chicane Air", "https://motorcyclegear.com", "cortech-chicane-air-shoes-for-women"),
    ("f46ebdde-8de3-471e-a680-696973b95a5e", "K Fifty 1 Jeans", "https://motorcyclegear.com", "klim-k-fifty-1-jean"),
    ("54a7da03-ab82-4ba2-b382-3bdc55253e6c", "MIG 3 Air Tex Gloves", "https://motorcyclegear.com", "dainese-mig-3-air-tex-gloves"),
    ("eb76ba65-c811-49a0-b346-bb1b334649dc", "Street Darker Gore-Tex", "https://shop.highroadmotorsports.com", "dainese-street-darker-shoes"),
    # batch 2 -- verified title match before writing
    ("67d0bfc3-d288-4579-8fe6-c70ceb89cf1c", "Air Maze Gloves", "https://bkmotoparts.com", "dainese-air-maze-gloves"),
    ("f9673614-dcb4-4356-a22c-c1f25271d40a", "Airi 2.0 Women's Gloves", "https://admsport.com", "gant-airi-20-pour-femme"),
    ("057dabf7-f5eb-4a41-97a1-f9b56ade1666", "Airium 2.0 Gloves", "https://admsport.com", "gant-airium-20"),
    ("e4571dc2-6196-4ed5-8e83-a2020f66afef", "Virium 2.0 GTX Gloves", "https://admsport.com", "gant-virium-20"),
    ("eb26916f-16a4-48f7-bd87-f10bde4d7c6f", "Gavia Gore-Tex Women's Boots", "https://motorcyclegear.com", "sidi-gavia-gore-tex-boots-for-women"),
    ("7cf3e83b-ae76-4a1b-98de-91b6e9e88be9", "Flash CE Gloves", "https://admsport.com", "gants-flash-ce"),
]

for pid, name, base, handle in MAP:
    imgs = [u for u in images(base, handle) if ok(u)][:8]
    if not imgs:
        print(f"  SKIP {name}: no verified images")
        continue
    files = [{"type": "external", "name": name[:90], "external": {"url": u}} for u in imgs]
    n.pages.update(page_id=pid, properties={"Photos": {"files": files}})
    print(f"  {name:28} {len(imgs)} photos ({base.split('//')[1]})")

print("DONE")
