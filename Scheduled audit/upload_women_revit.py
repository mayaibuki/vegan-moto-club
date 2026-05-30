"""
upload_women_revit.py
Create 24 new Notion rows for REV'IT! women's vegan jackets and update 1 existing row
(Sand 4 H2O Ladies, which had an old-format URL).

All products are all-synthetic / no leather — confirmed vegan by our review.
Descriptions are feature-focused with honest pros/cons; no vegan-material boilerplate.

Run:
  set -a && source ./.env.local && set +a
  python3 "Scheduled audit/upload_women_revit.py"
"""

import os, time
from notion_client import Client

n = Client(auth=os.environ["NOTION_API_KEY"])
DB = os.environ["NOTION_PRODUCTS_DB_ID"]

# ── Existing row to UPDATE (old-format URL, already in Notion) ──────────────
SAND4_PAGE_ID = "7fe4b5ab-ff84-457a-a042-21df7986ab50"

# ── Product data ─────────────────────────────────────────────────────────────
# Each dict contains all fields needed for a Notion page.
# 'action': 'update' uses an existing page_id; 'create' makes a new row.
PRODUCTS = [
    {
        "action": "update",
        "page_id": SAND4_PAGE_ID,
        "name": "Jacket Sand 4 H2O Ladies",
        "url": "https://revitsport.com/en-us/products/en-motorcycle-jacket-sand-4-h2o-ladies-black",
        "protection": "Highly protective",
        "waterproof": "Waterproof (Hydratex®)",
        "riding": ["Adventure / Touring"],
        "season": ["☀️ Summer", "🌦 Mid season", "❄️ Winter"],
        "materials": ["Polyester"],
        "img": "https://cdn.shopify.com/s/files/1/0664/7912/8749/files/091224093123_83598068083066084.jpg?v=1745550508",
        "description": (
            "The generation before the Sand 5 H2O Ladies and the longtime benchmark for women's adventure touring. "
            "Three fully removable layers — hydratex waterproof liner, thermal liner, and outer shell — can be configured "
            "independently for heat, cold, or rain. VCS ventilation opens front panels and arm zippers for aggressive airflow "
            "in warm weather. SEEFLEX CE-2 at shoulders and elbows with a connection zipper for pants attachment. "
            "CE Level AA. Now on outlet, which means meaningful price relief without a capability drop — the Sand 4 is still "
            "CE-compliant and built to last multiple around-the-world trips. "
            "If the Sand 5's slightly sportier geometry doesn't fit your body, the Sand 4's more traditional adventure cut "
            "may suit you better. No back protector included — add the SEESOFT insert."
        ),
    },
    {
        "action": "create",
        "name": "Jacket Sand 5 H2O Ladies",
        "url": "https://revitsport.com/en-us/products/en-motorcycle-jacket-sand-5-h2o-ladies-silver-anthracite",
        "protection": "Highly protective",
        "waterproof": "Waterproof (Hydratex®)",
        "riding": ["Adventure / Touring"],
        "season": ["☀️ Summer", "🌦 Mid season", "❄️ Winter"],
        "materials": ["Polyester"],
        "img": "https://cdn.shopify.com/s/files/1/0664/7912/8749/files/270225114531_83598068085080988.jpg?v=1765949817",
        "description": (
            "REV'IT!'s most iconic women's adventure jacket hits its fifth generation with a slightly sportier posture "
            "than the Sand 4 — reflecting how adventure bikes themselves have moved toward a more dynamic character. "
            "The standout feature is the over-and-under hydratex 3L waterproof liner: wear it outside the protective shell "
            "for a cleaner aesthetic and better membrane performance, or inside if you prefer. "
            "A lower-back pocket cutout routes a hydration pack hose under the arm — borrowed from REV'IT!'s Trail vest. "
            "SEEFLEX CE-2 at shoulders and elbows, airbag system-ready, CE Level AA. "
            "Recycled polyester throughout the outer shell, lining, and both removable liners. "
            "No back protector included — fit the SEESOFT CE-2 insert before riding."
        ),
    },
    {
        "action": "create",
        "name": "Jacket Flare 3 H2O Ladies",
        "url": "https://revitsport.com/en-us/products/en-motorcycle-jacket-flare-3-h2o-ladies-camo-dark-grey",
        "protection": "Highly protective",
        "waterproof": "Waterproof (Hydratex®)",
        "riding": ["Sport / Canyons", "Commute / Street"],
        "season": ["🌦 Mid season", "❄️ Winter"],
        "materials": ["Polyester"],
        "img": "https://cdn.shopify.com/s/files/1/0664/7912/8749/files/091224093918_83598068084809043_e28ab193-7ed3-4aca-8ed0-56e7a6cd4aea.jpg?v=1754569464",
        "description": (
            "Urban sport jacket built for cold, wet city riding — and designed to not look like one. "
            "The camo print hides ventilation zippers that run along the chest seams from collarbone to waist; "
            "functional design that reads as styling. The detachable hood snaps flat against the back or unzips entirely. "
            "Hydratex G-liner waterproofing and a detachable thermal liner make this a genuine three-season city jacket. "
            "SEESMART CE-1 at shoulders and elbows — note that's level 1, not level 2 limb armor. "
            "CE Level AA. If CE-2 limb protection matters to you, the Flare 3 H2O is outclassed by the Sand 5 or Lamina GTX. "
            "Recycled polyester outer shell and liners."
        ),
    },
    {
        "action": "create",
        "name": "Jacket Rosier H2O Ladies",
        "url": "https://revitsport.com/en-us/products/en-motorcycle-jacket-rosier-h2o-ladies-black",
        "protection": "Highly protective",
        "waterproof": "Waterproof (Hydratex®)",
        "riding": ["Commute / Street"],
        "season": ["🌦 Mid season", "❄️ Winter"],
        "materials": ["Polyester"],
        "img": "https://cdn.shopify.com/s/files/1/0664/7912/8749/files/091224094006_83598068084810231_7e4503bf-cac5-4136-bec7-1f1b9d5498d0.jpg?v=1765949884",
        "description": (
            "A city commuter jacket that earns the word chic honestly: sculpted hip-length silhouette, "
            "stretch polyester twill 3L outer shell for freedom of movement, and a hydratex 3L construction "
            "that's built in (not a separate liner), keeping the profile slim. "
            "A sleeve card-pocket means you can tap through without reaching into a bag. "
            "Detachable thermal liner handles cooler days; reflective stripe at the upper back aids low-light visibility. "
            "SEESMART CE-1 at shoulders and elbows, airbag system-ready. CE Level AA. "
            "No back protector included — add the SEESOFT insert before riding. "
            "The fixed liner means it's always waterproof but slightly heavier than a removable-liner design."
        ),
    },
    {
        "action": "create",
        "name": "Jacket Tornado 4 H2O Ladies",
        "url": "https://revitsport.com/en-us/products/en-motorcycle-jacket-tornado-4-h2o-ladies-silver-black",
        "protection": "Highly protective",
        "waterproof": "Waterproof (Hydratex®)",
        "riding": ["Adventure / Touring"],
        "season": ["☀️ Summer", "🌦 Mid season", "❄️ Winter"],
        "materials": ["Polyester", "Mesh fabric"],
        "img": "https://cdn.shopify.com/s/files/1/0664/7912/8749/files/091224094040_83598068084653728.jpg?v=1760366664",
        "description": (
            "A legitimate all-season women's adventure jacket. Strip both liners and the 3D air mesh "
            "chest, arms, and back panels breathe freely in summer heat; add the thermal for autumn cold; "
            "clip the over-and-under hydratex 3L liner for full waterproofing — worn inside or outside "
            "the protective shell per your preference. "
            "SEEFLEX CE-2 at shoulders and elbows, airbag system-ready, short connection zipper for pants. CE Level AA. "
            "The 'over-and-under' waterproof liner is a genuine flexibility advantage over single-position designs. "
            "One honest trade-off: running both liners installed adds meaningful bulk. "
            "If you only need waterproofing and rarely push into warm-weather mesh territory, the Outback 5 H2O Ladies "
            "may be a more focused choice."
        ),
    },
    {
        "action": "create",
        "name": "Jacket Voltiac 3 H2O Ladies",
        "url": "https://revitsport.com/en-us/products/en-motorcycle-jacket-voltiac-3-h2o-ladies-black-silver",
        "protection": "Moderately protective",
        "waterproof": "Waterproof (Hydratex®)",
        "riding": ["Adventure / Touring"],
        "season": ["🌦 Mid season", "❄️ Winter"],
        "materials": ["Polyester"],
        "img": "https://cdn.shopify.com/s/files/1/0664/7912/8749/files/091224093649_83598068083074455_bdebd21a-c4f4-4ec6-8b7e-d5ef1b37bfbe.jpg?v=1765949843",
        "description": (
            "REV'IT!'s most accessible women's adventure touring jacket. The 600D polyester shell is durable; "
            "the hydratex waterproof liner and thermal liner cover wet and cold conditions; "
            "two front vent panels open quickly for airflow when the sun comes out. "
            "Fit adjusts at the waist, cuffs, and upper arms. "
            "SEESMART CE-1 at shoulders and elbows — this is level 1, not level 2 limb armor. "
            "CE Level A (not AA). Those are the meaningful trade-offs vs the Sand 5 or Tornado 4 H2O: "
            "lower CE class and CE-1 limb protection in exchange for a lower price. "
            "No back protector included; add the SEESOFT CE-2 insert. "
            "Good all-weather tourer for everyday use; step up to the Tornado 4 H2O Ladies if CE-AA matters."
        ),
    },
    {
        "action": "create",
        "name": "Jacket Levante 2 H2O Ladies",
        "url": "https://revitsport.com/en-us/products/en-motorcycle-jacket-levante-2-h2o-ladies-black",
        "protection": "Highly protective",
        "waterproof": "Waterproof (Hydratex®)",
        "riding": ["Adventure / Touring", "Sport / Canyons"],
        "season": ["☀️ Summer", "🌦 Mid season"],
        "materials": ["Polyester", "Mesh fabric"],
        "img": "https://cdn.shopify.com/s/files/1/0664/7912/8749/files/091224093504_83598068083071067.jpg?v=1765949906",
        "description": (
            "A mesh-first adventure jacket that doesn't force you to choose between breathability and waterproofing. "
            "The detachable hydratex Lite liner stores in the back pocket when not needed — "
            "a roadside swap takes seconds. Large mesh panels on the front, back, and arms circulate air aggressively. "
            "SEEFLEX CE-2 at shoulders and elbows — strong protection spec for a jacket at this price point. CE Level AA. "
            "No thermal liner means cold-weather riding is not in scope — this is a spring-through-autumn jacket. "
            "Older SS22 model, currently on outlet. "
            "A strong value option if the mesh-plus-detachable-waterproof setup matches your riding conditions."
        ),
    },
    {
        "action": "create",
        "name": "Jacket Afterburn H2O Ladies",
        "url": "https://revitsport.com/en-us/products/en-motorcycle-jacket-afterburn-h2o-ladies-dark-navy",
        "protection": "Moderately protective",
        "waterproof": "Waterproof (Hydratex®)",
        "riding": ["Sport / Canyons", "Commute / Street"],
        "season": ["🌦 Mid season", "❄️ Winter"],
        "materials": ["Polyester"],
        "img": "https://cdn.shopify.com/s/files/1/0664/7912/8749/files/091224093027_83598068083066153_aada8bf3-1e63-4920-a53a-d00d9495abd2.jpg?v=1745550339",
        "description": (
            "A sport-urban jacket with a detachable hood — an uncommon combination in this category. "
            "Clean lines and a non-motorcycle aesthetic mean it transitions off the bike without looking out of place. "
            "Vent zippers let you open the shell without removing the liner; the hydratex G-liner waterproofs; "
            "the detachable thermal extends the cold-weather range. Connection zipper attaches to REV'IT! trousers. "
            "SEESMART CE-1 at shoulders and elbows. CE Level A — not AA, which is the key limitation here. "
            "The Afterburn H2O suits daily urban and sport riding but isn't the pick if protection rating is the priority. "
            "Older FW20 model on outlet clearance."
        ),
    },
    {
        "action": "create",
        "name": "Jacket Airwave 4 Ladies",
        "url": "https://revitsport.com/en-us/products/en-motorcycle-jacket-airwave-4-ladies-grey-pink",
        "protection": "Highly protective",
        "waterproof": "Not waterproof",
        "riding": ["Adventure / Touring", "Sport / Canyons"],
        "season": ["☀️ Summer"],
        "materials": ["Polyester", "Mesh fabric"],
        "img": "https://cdn.shopify.com/s/files/1/0664/7912/8749/files/091224094120_83598068084655546_ca933548-68b7-403f-a2eb-b87b4481f4c0.jpg?v=1761550814",
        "description": (
            "A pure summer adventure jacket — no waterproof liner, no thermal, just aggressive ventilation. "
            "The 3D air mesh chest, back, and arm panels push airflow directly to the body. "
            "Softshell, ripstop, PWR|Shell Mesh, and ballistic mesh combine for a structured feel that still breathes well. "
            "SEESMART CE-1 at shoulders and elbows, airbag system-ready. CE Level AA — strong for a warm-weather mesh jacket. "
            "Laminated reflection at the lower arms, shoulders, and back. "
            "Best choice when heat is the main enemy and you carry a packable rain layer separately. "
            "If you want a jacket that handles rain without extra gear, the Tornado 4 H2O Ladies or Voltiac 3 H2O Ladies "
            "are the right alternatives."
        ),
    },
    {
        "action": "create",
        "name": "Jacket Control Air H2O Ladies",
        "url": "https://revitsport.com/en-us/products/en-motorcycle-jacket-control-air-h2o-ladies-white-black",
        "protection": "Highly protective",
        "waterproof": "Waterproof (Hydratex®)",
        "riding": ["Sport / Canyons", "Commute / Street"],
        "season": ["☀️ Summer", "🌦 Mid season"],
        "materials": ["Polyester", "Mesh fabric"],
        "img": "https://cdn.shopify.com/s/files/1/0664/7912/8749/files/091224093944_83598068084651016_bd5fd8d7-3f75-4232-a88d-8b68e56dfbeb.jpg?v=1760366644",
        "description": (
            "About two-thirds of the front and back is PWR|Mesh — this is one of REV'IT!'s most ventilated women's jackets. "
            "For wet days, a separately wearable hydratex 2L waterproof membrane adds waterproofing without being attached to the jacket; "
            "unlike an integrated liner, you can also wear the membrane as a standalone rain layer. "
            "Diamond gradient graphics on the sleeve backs distinguish it from the Control H2O visually. "
            "SEESMART CE-1 at shoulders and elbows, airbag system-ready. CE Level AA. "
            "No back protector included; no thermal liner means cold weather is out of scope. "
            "A summer-to-autumn jacket for sport and city riders who prioritize airflow but want a wet-day contingency."
        ),
    },
    {
        "action": "create",
        "name": "Jacket Eclipse 2 Ladies",
        "url": "https://revitsport.com/en-us/products/en-motorcycle-jacket-eclipse-2-ladies-silver",
        "protection": "Moderately protective",
        "waterproof": "Not waterproof",
        "riding": ["Commute / Street"],
        "season": ["☀️ Summer"],
        "materials": ["Polyester", "Mesh fabric"],
        "img": "https://cdn.shopify.com/s/files/1/0664/7912/8749/files/091224093614_83598068083073484_479399b1-a3a0-45e5-bb0f-77acc6ee148f.jpg?v=1768390846",
        "description": (
            "A lightweight summer city jacket built for one thing: keeping you cool in urban heat. "
            "Breathable mesh panels at the front, back, and inner arms route airflow around the full upper body. "
            "600D polyester shell for abrasion resistance; adjustable tabs at the waist, cuffs, and biceps let you tune the fit. "
            "SEESMART CE-1 at shoulders and elbows — upgrade with the SEESOFT CE-2 back insert. CE Level A. "
            "No waterproofing, no thermal liner: this is a warm-weather-only jacket. "
            "If summer rain is part of your commute, layer a packable rain jacket over it or step up "
            "to the Shade 2 H2O Ladies or Eclipse 2 paired with a separate membrane. "
            "Recycled polyester in the outer shell and inner lining."
        ),
    },
    {
        "action": "create",
        "name": "Jacket Torque 2 H2O Ladies",
        "url": "https://revitsport.com/en-us/products/en-motorcycle-jacket-torque-2-h2o-ladies-black-light-grey",
        "protection": "Moderately protective",
        "waterproof": "Waterproof (Hydratex®)",
        "riding": ["Sport / Canyons", "Commute / Street"],
        "season": ["☀️ Summer", "🌦 Mid season"],
        "materials": ["Polyester", "Mesh fabric"],
        "img": "https://cdn.shopify.com/s/files/1/0664/7912/8749/files/091224093411_83598068083071138_620560cc-3e03-4ce4-9526-eead2c5eb466.jpg?v=1745549618",
        "description": (
            "Mesh-and-hydratex women's sport-urban jacket from the SS22 generation, now on outlet. "
            "Fully ventilated shell keeps you cool in warm weather; the detachable hydratex G-liner "
            "snaps in for rain. A wind catcher behind the front zipper blocks cold from reaching the chest. "
            "Adjustment points at the waist and arms tune the female-specific fit. "
            "SEESMART CE-1 at shoulders and elbows, connection zipper for pants. CE Level A. "
            "The current-generation replacement is the Torque 3 H2O Ladies (CE AA, CE-1 armor). "
            "Buy the Torque 2 if the clearance price is significantly lower and CE-AA certification isn't a requirement."
        ),
    },
    {
        "action": "create",
        "name": "Jacket Control H2O Ladies",
        "url": "https://revitsport.com/en-us/products/en-motorcycle-jacket-control-h2o-ladies-black-silver",
        "protection": "Highly protective",
        "waterproof": "Waterproof (Hydratex®)",
        "riding": ["Sport / Canyons", "Commute / Street"],
        "season": ["🌦 Mid season", "❄️ Winter"],
        "materials": ["Polyester"],
        "img": "https://cdn.shopify.com/s/files/1/0664/7912/8749/files/091224094001_83598068084652425.jpg?v=1760367014",
        "description": (
            "The waterproof counterpart to the Control Air H2O Ladies — same diamond gradient aesthetic, "
            "same CE Level AA construction, but tuned for cooler and wetter conditions rather than peak airflow. "
            "The hydratex G-liner is fixed; the detachable thermal adds warmth for colder days. "
            "Exhaust vents at the lower sleeves and upper back provide some airflow when the temperature rises. "
            "SEESMART CE-1 at shoulders and elbows, airbag system-ready, short connection zipper. "
            "On outlet (SS24 model). Good option for sport and city riders who primarily need waterproofing "
            "with occasional ventilation, rather than the other way around."
        ),
    },
    {
        "action": "create",
        "name": "Jacket Lamina GTX Ladies",
        "url": "https://revitsport.com/en-us/products/en-motorcycle-jacket-lamina-gtx-ladies-blue-blue",
        "protection": "Highly protective",
        "waterproof": "Waterproof (Gore-tex®) ",
        "riding": ["Adventure / Touring"],
        "season": ["🌦 Mid season", "❄️ Winter"],
        "materials": ["Polyester", "Gore-tex (waterproof fabric)"],
        "img": "https://cdn.shopify.com/s/files/1/0664/7912/8749/files/091224093837_83598068084474305_a9bdbf31-8772-4572-8c6a-d88dbf67a7ea.jpg?v=1766065758",
        "description": (
            "REV'IT!'s flagship women's adventure jacket, designed from a blank sheet for female riders — "
            "not a men's jacket re-fitted. The 2L GORE-TEX shell is laminated directly to the fabric "
            "rather than loose inside, keeping the jacket lean and packable without sacrificing waterproof performance. "
            "TIZIP waterproof front zipper eliminates the weak point where most waterproof jackets leak. "
            "SEEFLEX CE-2 at shoulders and elbows, and the SEESOFT CE-2 back protector ships included in the box — "
            "one of the few REV'IT! jackets that doesn't require a separate purchase for back protection. "
            "Airbag system-ready. CE Level AA. "
            "The Lamina GTX is the right choice for serious multi-day adventure travel in variable conditions. "
            "It earns its premium price. No thermal liner included — layer your own underneath in cold weather."
        ),
    },
    {
        "action": "create",
        "name": "Jacket Flare 2 Ladies",
        "url": "https://revitsport.com/en-us/products/en-motorcycle-jacket-flare-2-ladies-camo-black-grey",
        "protection": "Moderately protective",
        "waterproof": "Waterproof (Hydratex®)",
        "riding": ["Sport / Canyons", "Commute / Street"],
        "season": ["🌦 Mid season", "❄️ Winter"],
        "materials": ["Polyester"],
        "img": "https://cdn.shopify.com/s/files/1/0664/7912/8749/files/091224093003_83598068083066162_04c94f86-d4c4-459b-a56e-1a7f23c55548.jpg?v=1745428545",
        "description": (
            "The predecessor to the Flare 3 H2O Ladies (FW20), now on clearance. "
            "Notable for Knox® Flexiform armor at the shoulders and elbows — Knox is well-regarded "
            "for thin-profile, flexible protection, and a welcome alternative to REV'IT!'s own SEESMART. "
            "Hydratex G-liner waterproofing, detachable thermal liner, and a connection zipper for pants. "
            "A 'true feminine race fit' per REV'IT! — cut to create a shaped silhouette both on and off the bike. "
            "CE Level A (not AA). "
            "The Flare 3 H2O Ladies is the current-gen replacement with CE-AA and a detachable hood. "
            "The Flare 2 is a clearance pick if Knox armor appeals and CE-AA certification isn't essential."
        ),
    },
    {
        "action": "create",
        "name": "Jacket Shade H2O Ladies",
        "url": "https://revitsport.com/en-us/products/en-motorcycle-jacket-shade-h2o-ladies-black",
        "protection": "Moderately protective",
        "waterproof": "Waterproof (Hydratex®)",
        "riding": ["Commute / Street"],
        "season": ["🌦 Mid season"],
        "materials": ["Polyester"],
        "img": "https://cdn.shopify.com/s/files/1/0664/7912/8749/files/091224093212_83598068083070463_65274c44-af28-498f-9c43-7ddc3b118426.jpg?v=1745550941",
        "description": (
            "An entry-level city waterproof jacket designed after the Eclipse Ladies — back-to-basics "
            "with a female-specific fit and a not-too-tight silhouette that works on the bike and walking around. "
            "The hydratex G-liner is built into the jacket (not detachable), delivering reliable wet-weather coverage "
            "without a liner management step. "
            "SEESMART CE-1 at shoulders and elbows. CE Level A. "
            "No thermal liner included and no back protector in the box; the scope is mild-to-wet urban commuting. "
            "Older FW21 model, available in multiple colorways on outlet. "
            "The Shade 2 H2O Ladies is the current-gen upgrade — CE-AA, thermal liner, airbag-ready."
        ),
    },
    {
        "action": "create",
        "name": "Jacket Arc H2O Ladies",
        "url": "https://revitsport.com/en-us/products/en-motorcycle-jacket-arc-h2o-ladies-black",
        "protection": "Moderately protective",
        "waterproof": "Waterproof (Hydratex®)",
        "riding": ["Sport / Canyons", "Commute / Street"],
        "season": ["🌦 Mid season", "❄️ Winter"],
        "materials": ["Polyester"],
        "img": "https://cdn.shopify.com/s/files/1/0664/7912/8749/files/091224092852_83598068083066334_80931f2b-e0ee-4d24-9cff-14d7b09b7ad7.jpg?v=1745549647",
        "description": (
            "A sport-to-street crossover jacket from 2019 with a race-inspired silhouette and a female-specific fit. "
            "The hydratex G-liner keeps rain out; the detachable thermal liner extends the cold-weather range. "
            "Adjustment points at the waist and wrists let you dial in the fit. "
            "SEESMART CE-1 at shoulders and elbows; upgradable with the SEESOFT CE-2 back insert. CE Level A. "
            "This is an older model (SS19) on clearance — the CE-1 limb armor and CE-A class reflect a previous generation "
            "of protection standards. It still meets CE requirements, but current-gen alternatives "
            "like the Control H2O Ladies or Flare 3 H2O Ladies offer CE-AA and comparable waterproofing. "
            "A reasonable clearance buy if the price difference is substantial."
        ),
    },
    {
        "action": "create",
        "name": "Jacket Voltiac 2 Ladies",
        "url": "https://revitsport.com/en-us/products/en-motorcycle-jacket-voltiac-2-ladies-black-silver",
        "protection": "Moderately protective",
        "waterproof": "Waterproof (Hydratex®)",
        "riding": ["Adventure / Touring"],
        "season": ["🌦 Mid season", "❄️ Winter"],
        "materials": ["Polyester"],
        "img": "https://cdn.shopify.com/s/files/1/0664/7912/8749/files/091224092848_83598068083066357.jpg?v=1745549076",
        "description": (
            "The first-generation Voltiac in women's cut (SS19), six model years back. "
            "Softshell chest panels for wind resistance; hydratex G-liner waterproofing; "
            "detachable thermal liner; VCS ventilation zippers; reflective striping. "
            "SEESMART CE-1 at shoulders and elbows. CE Level A. "
            "The Voltiac 3 H2O Ladies is the current-generation replacement with a 600D polyester shell "
            "and unchanged CE-1/CE-A spec. "
            "Buy the Voltiac 2 only if the clearance price gap is significant — there's no capability gain here "
            "over its successor, only a lower price."
        ),
    },
    {
        "action": "create",
        "name": "Jacket Arc Air Ladies",
        "url": "https://revitsport.com/en-us/products/en-motorcycle-jacket-arc-air-ladies-black-white",
        "protection": "Moderately protective",
        "waterproof": "Not waterproof",
        "riding": ["Sport / Canyons", "Commute / Street"],
        "season": ["☀️ Summer"],
        "materials": ["Polyester", "Mesh fabric"],
        "img": "https://cdn.shopify.com/s/files/1/0664/7912/8749/files/091224092843_83598068083066404.jpg?v=1745550516",
        "description": (
            "A summer-only mesh sport jacket with no waterproofing — it exists to keep you cool "
            "on hot canyon and city rides. PWR|mesh and 600D polyester construction balances airflow with abrasion resistance. "
            "SEESMART CE-1 at shoulders and elbows; connection zipper for pants; jeans loops. CE Level A. "
            "No liner, no hood, no waterproofing: pack a separate rain layer if there's any chance of wet weather. "
            "Older SS19 model on clearance. The Eclipse 2 Ladies is the current urban mesh equivalent "
            "if you don't need the connection zipper."
        ),
    },
    {
        "action": "create",
        "name": "Jacket Outback 3 Ladies",
        "url": "https://revitsport.com/en-us/products/en-motorcycle-jacket-outback-3-ladies-black-silver",
        "protection": "Highly protective",
        "waterproof": "Waterproof (Hydratex®)",
        "riding": ["Adventure / Touring"],
        "season": ["☀️ Summer", "🌦 Mid season", "❄️ Winter"],
        "materials": ["Polyester"],
        "img": "https://cdn.shopify.com/s/files/1/0664/7912/8749/files/091224092903_83598068083066307.jpg?v=1745549159",
        "description": (
            "Third generation of REV'IT!'s workhorse women's adventure jacket, now on outlet (SS19). "
            "Three-layer construction: outer shell, detachable hydratex G-liner, and detachable thermal "
            "— all removable for warm-weather riding. SEEFLEX CE-2 at shoulders and elbows — "
            "strong limb protection for an outlet-priced jacket. CE Level AA. "
            "Multiple adjustment points, connection zipper, back pocket large enough to store both liners. "
            "The Outback 5 H2O Ladies is the current generation with improved chest ventilation and a waist-belt adjuster. "
            "If budget is the priority, the Outback 3 on outlet remains CE-compliant and capable. "
            "No back protector included; no thermal or waterproof protectors come standard."
        ),
    },
    {
        "action": "create",
        "name": "Jacket Shade 2 H2O Ladies",
        "url": "https://revitsport.com/en-us/products/en-motorcycle-jacket-shade-2-h2o-ladies-sand",
        "protection": "Highly protective",
        "waterproof": "Waterproof (Hydratex®)",
        "riding": ["Commute / Street"],
        "season": ["🌦 Mid season", "❄️ Winter"],
        "materials": ["Polyester"],
        "img": "https://cdn.shopify.com/s/files/1/0664/7912/8749/files/080725104909_83598068085110374.jpg?v=1755595319",
        "description": (
            "The current-generation city waterproof jacket for women, upgraded significantly from the original Shade H2O. "
            "Fully softshell construction for stretch and comfort; hydratex G-liner waterproofing; "
            "detachable thermal liner; SEESMART CE-1 at shoulders and elbows. Airbag system-ready. CE Level AA. "
            "Understated ton-sur-ton colorways with minimal contrast zippers — a deliberately unfussy aesthetic "
            "that suits riders who want protection without a loud motorcycle-jacket look. "
            "The jump from Shade H2O to Shade 2 H2O is meaningful: CE class goes from A to AA, "
            "you gain a thermal liner and airbag compatibility, and you get a current FW25 model. "
            "No back protector included; add the SEESOFT insert."
        ),
    },
    {
        "action": "create",
        "name": "Jacket Outback 5 H2O Ladies",
        "url": "https://revitsport.com/en-us/products/en-motorcycle-jacket-outback-5-h2o-ladies-black",
        "protection": "Highly protective",
        "waterproof": "Waterproof (Hydratex®)",
        "riding": ["Adventure / Touring"],
        "season": ["☀️ Summer", "🌦 Mid season", "❄️ Winter"],
        "materials": ["Polyester"],
        "img": "https://cdn.shopify.com/s/files/1/0664/7912/8749/files/021225114720_83598068085279802.jpg?v=1767880145",
        "description": (
            "The fifth and current generation of REV'IT!'s benchmark women's adventure jacket — "
            "ridden around the world since the series launched. "
            "The same proven three-layer construction (detachable hydratex liner, detachable thermal, outer shell) "
            "gets improved chest ventilation and a new integrated waist-belt adjuster for a more secure adventure fit. "
            "SEEFLEX CE-2 at shoulders and elbows; optional SEESOFT CE-1 chest protectors "
            "and CE-2 back protector upgrades available. Airbag system-ready. CE Level AA. "
            "As an all-synthetic jacket in an adventure touring category historically dominated by leather, "
            "the Outback 5 H2O Ladies is one of the more significant vegan options in the segment — "
            "full CE-AA adventure spec with no animal materials whatsoever."
        ),
    },
    {
        "action": "create",
        "name": "Jacket Convergent H2O Ladies",
        "url": "https://revitsport.com/en-us/products/en-motorcycle-jacket-convergent-h2o-ladies-red-black",
        "protection": "Highly protective",
        "waterproof": "Waterproof (Hydratex®)",
        "riding": ["Adventure / Touring"],
        "season": ["🌦 Mid season", "❄️ Winter"],
        "materials": ["Polyester"],
        "img": "https://cdn.shopify.com/s/files/1/0664/7912/8749/files/021225114613_83598068085277189.jpg?v=1767879848",
        "description": (
            "An entry point into REV'IT!'s women's adventure touring range — rally-inspired aesthetic, "
            "competitive price, and a carefully chosen feature set. "
            "The hydratex G-liner is fixed (not detachable), so the jacket is always waterproof — "
            "useful if you tend to forget liners at home, but it limits hot-weather breathability. "
            "Detachable thermal liner for cold days. Large ventilation panel behind the front zipper. "
            "SEEFLEX CE-2 at shoulders and elbows, connection zipper, waterproof pockets, adjustable collar. CE Level AA. "
            "Positioned below the Outback 5 in price. New SS26 model. "
            "The trade-off vs the Outback 5 H2O Ladies: fixed liner instead of over-and-under detachable, "
            "and no airbag system compatibility."
        ),
    },
    {
        "action": "create",
        "name": "Jacket Highcrest H2O Ladies",
        "url": "https://revitsport.com/en-us/products/en-motorcycle-jacket-highcrest-h2o-ladies-black",
        "protection": "Highly protective",
        "waterproof": "Waterproof (Hydratex®)",
        "riding": ["Commute / Street"],
        "season": ["☀️ Summer", "🌦 Mid season"],
        "materials": ["Polyester", "Mesh fabric"],
        "img": "https://cdn.shopify.com/s/files/1/0664/7912/8749/files/021225114944_83598068085287227.jpg?v=1768390688",
        "description": (
            "A city mesh jacket paired with a separate over-and-under hydratex 3L rain jacket — "
            "two wearable pieces in one purchase. Ride the ventilated mesh base in warm weather; "
            "when rain arrives, the packable hydratex rain jacket goes on top (or underneath) in seconds. "
            "SEEFLEX CE-2 at shoulders and elbows; reflective elements on both pieces. CE Level AA. "
            "Jeans loops, short connection zipper, urban aesthetic. New SS26 model. "
            "The two-piece system is flexible, but it does add a step vs a single jacket with a fixed liner. "
            "If you want one jacket that handles everything without swapping, the Shade 2 H2O Ladies is simpler. "
            "No back protector included."
        ),
    },
    {
        "action": "create",
        "name": "Jacket Torque 3 H2O Ladies",
        "url": "https://revitsport.com/en-us/products/en-motorcycle-jacket-torque-3-h2o-ladies-grey-pink",
        "protection": "Highly protective",
        "waterproof": "Waterproof (Hydratex®)",
        "riding": ["Sport / Canyons", "Commute / Street"],
        "season": ["☀️ Summer", "🌦 Mid season"],
        "materials": ["Polyester", "Mesh fabric"],
        "img": "https://cdn.shopify.com/s/files/1/0664/7912/8749/files/021225114853_83598068085284855.jpg?v=1768310063",
        "description": (
            "The current-generation women's urban sport jacket — direct successor to the Torque 2 H2O Ladies "
            "with the CE class upgraded from A to AA. "
            "Fully ventilated mesh construction keeps you cool; the detachable hydratex G-liner "
            "adds waterproofing when it rains. SEESMART CE-1 at shoulders and elbows. CE Level AA. "
            "Clean sport silhouette with a short connection zipper for pants attachment. "
            "New SS26 model, current pricing. No back protector included — add the SEESOFT CE-2 insert. "
            "If CE-2 limb armor is important, the Control H2O Ladies or Flare 3 H2O offer better limb protection "
            "in exchange for less ventilation."
        ),
    },
]


# ── Notion property builder ───────────────────────────────────────────────────
def build_props(p):
    props = {
        "Name of product": {"title": [{"text": {"content": p["name"]}}]},
        "URL": {"url": p["url"]},
        "Brand": {"select": {"name": "REV'IT!"}},
        "Gender": {"multi_select": [{"name": "Women"}]},
        "Category": {"multi_select": [{"name": "Jackets"}]},
        "Level of Protection": {"select": {"name": p["protection"]}},
        "Level of Waterproof": {"select": {"name": p["waterproof"]}},
        "Riding style": {"multi_select": [{"name": s} for s in p["riding"]]},
        "Season": {"multi_select": [{"name": s} for s in p["season"]]},
        "Materials": {"multi_select": [{"name": m} for m in p["materials"]]},
        "Vegan Verified": {"select": {"name": "Verified Vegan by us"}},
        "Description": {"rich_text": [{"text": {"content": p["description"]}}]},
    }
    if p.get("img"):
        props["Photos"] = {
            "files": [{
                "type": "external",
                "name": p["name"],
                "external": {"url": p["img"]}
            }]
        }
    return props


# ── Run ───────────────────────────────────────────────────────────────────────
created, updated, errors = 0, 0, []

for p in PRODUCTS:
    try:
        props = build_props(p)
        if p["action"] == "update":
            # For update, exclude name field (title) if you want to preserve it,
            # but we're normalising the name here too
            n.pages.update(page_id=p["page_id"], properties=props)
            print(f"UPDATED  {p['name']}")
            updated += 1
        else:
            n.pages.create(parent={"database_id": DB}, properties=props)
            print(f"CREATED  {p['name']}")
            created += 1
        time.sleep(0.4)   # stay well under Notion rate limits
    except Exception as e:
        print(f"ERROR    {p['name']}: {e}")
        errors.append(p["name"])

print()
print(f"Done — {created} created, {updated} updated, {len(errors)} errors")
if errors:
    print("Failed:", errors)
