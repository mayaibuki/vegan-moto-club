# Scheduled Audit — Scripts Reference

Automation scripts for maintaining and expanding the Vegan Moto Club Notion product database.
There are two categories of work here: the **live audit** (runs automatically on a GitHub Actions
cron + webhook) and **catalog expansion** scripts (run manually when adding a new brand or category).

---

## Live Audit

### `vmc_new_product_audit.py`

The only script that runs automatically. Triggered two ways:

1. **Webhook mode** — a user submits a product via the form on veganmotoclub.com, Notion fires
   a webhook to `app/api/notion-webhook/route.ts`, which dispatches the GitHub Action
   `.github/workflows/product-audit.yml` with a `page_id` argument. The script processes
   that one page immediately.
2. **Batch mode** — a weekly cron (Mondays 09:00 UTC) runs the same script without `--page-id`,
   picking up to 20 entries where Description is still empty.

**What it does per product:**

- Scrapes the product URL with `requests` + `BeautifulSoup`
- Detects Shopify-backed brands (e.g. REV'IT! on `revitsport.com`) and reads their
  structured `tags` field via `/products/{handle}.json` for authoritative Gender, Riding style,
  and Level of Waterproof — more reliable than scraping page text
- Checks for a maker "Vegan" label in label-like HTML elements (headings, spec cells,
  sustainability sections) and sets `Vegan Verified = Confirmed Vegan by maker` when found
- Keyword-infers Brand, Category, Materials, Season, Protection from page text as a fallback
- Writes only to fields that are currently empty in Notion — never overwrites curated data
- Downloads and uploads up to 7 product photos as external file links
- Generates a dated `.md` and `.html` report saved to `WORKSPACE_DIR`

**Key design decisions:**

- Never creates new Notion select options. All field values are validated against the hardcoded
  `VALID` dict before writing.
- Non-destructive: `build_notion_props` receives the current page properties and skips any
  field that already has a value.
- Shopify tags take priority over scraped text for gender, riding style, and waterproofing.
  Avoids false positives like footer cross-sell links tagging unrelated products.

**Run manually:**

```bash
# from the project root
set -a && source ./.env.local && set +a
python3 "Scheduled audit/vmc_new_product_audit.py"

# single-product (webhook-equivalent)
python3 "Scheduled audit/vmc_new_product_audit.py" --page-id <notion-page-id>
```

### `lib_anthropic.py`

Thin wrapper around the Anthropic SDK used by the audit for description writing and vegan
adjudication. Both helpers fall back to deterministic stubs when `ANTHROPIC_API_KEY` is not
set, so the audit keeps working without an API key. Currently running in fallback mode.

---

## Catalog Expansion Pattern

When adding products from a new brand or category, the workflow is:

1. **Fetch** — scrape the brand's Shopify collection into a local JSON file
2. **Review** — inspect the JSON, confirm vegan filtering logic
3. **Upload** — read the JSON, cross-reference Notion for duplicates, create new pages

### Add scripts (fetch + filter + upload in one)

| Script | Brand / scope |
|---|---|
| `add_revit_jackets.py` | REV'IT! men's motorcycle jackets |
| `add_aerostich_vegan.py` | Aerostitch full catalog (vegan filter applied) |

These are the canonical templates for adding a new brand. Copy the nearest one and adapt
the collection URL, `NON_VEGAN_KW` list, and field mappings.

### Fetch scripts (Shopify collection scrapers)

Each script hits a Shopify `/collections/.../products.json` endpoint, deduplicates by base
model name, filters for vegan products, and writes the result to a local JSON file.

| Script | Category |
|---|---|
| `fetch_women_revit.py` | REV'IT! women's jackets |
| `fetch_men_gloves.py` | Men's gloves |
| `fetch_women_gloves.py` | Women's gloves |
| `fetch_men_pants.py` | Men's pants |
| `fetch_women_pants.py` | Women's pants |
| `fetch_jeans.py` | Motorcycle jeans |
| `fetch_layers.py` | Base layers / mid layers |
| `fetch_men_boots.py` | Men's boots |
| `fetch_men_shoes.py` | Men's shoes |
| `fetch_women_shoes.py` | Women's shoes |

Run any fetch script, inspect the JSON it produces, then run the matching upload script.
The JSON files are not committed to git (generated artifacts).

### Upload scripts (Notion writers)

Read the JSON produced by the matching fetch script, skip duplicates already in Notion,
and create new product pages with all fields populated.

| Script | What it adds |
|---|---|
| `upload_revit_descriptions.py` | Feature-focused descriptions for the 73 REV'IT! men's jackets (Pro-authored, run once) |
| `upload_women_revit.py` | REV'IT! women's jacket product pages |
| `upload_men_gloves.py` | Men's gloves |
| `upload_women_gloves.py` | Women's gloves |
| `upload_men_pants.py` | Men's pants / trousers |
| `upload_women_pants.py` | Women's pants / trousers |
| `upload_jeans.py` | Motorcycle jeans |
| `upload_layers.py` | Base / mid layers |

---

## Data Quality Scripts

Run manually when specific fields across a set of products need correcting.

### `fix_revit_fields.py`

Re-derives Gender, Riding style, Level of Waterproof, Level of Protection, and Brand for
all REV'IT! products by matching their name against the live Shopify collection tags.
Used after the automated audit corrupted Brand on ~9 entries. Also serves as the reference
implementation for tag-based field mapping.

```bash
set -a && source ./.env.local && set +a
python3 "Scheduled audit/fix_revit_fields.py"
```

### `revit_maker_vegan.py`

Checks each REV'IT! model's rendered product page for a "Vegan" entry in the Sustainability
tab and upgrades matching Notion entries to `Confirmed Vegan by maker`. Run once after
adding a batch of REV'IT! products to apply the stronger label where the maker claims it.

```bash
set -a && source ./.env.local && set +a
python3 "Scheduled audit/revit_maker_vegan.py"
```

---

## Utilities

| Script | Purpose |
|---|---|
| `resolve_shopify.py` | Resolves a product name to its Shopify handle across multiple brand storefronts. Used when a product URL is known but the handle is not. |
| `dealer_photos.py` | Manually verified product-to-dealer mappings (`pid, name, base, handle`). Fetches and writes photos for products whose brand storefront does not carry good images. Add new entries to the `MAP` list and re-run. |
| `apply_shopify_photos.py` | Fetches photos from a Shopify storefront and applies them to existing Notion pages. |
| `export_revit_source.py` | Exports cleaned body_html feature text for each REV'IT! model to a local JSON file, for use when writing descriptions outside the audit. |

---

## Environment Variables

All scripts read from `.env.local` at the project root.

| Variable | Required by | Description |
|---|---|---|
| `NOTION_API_KEY` | Catalog expansion + data quality scripts | Notion integration token |
| `NOTION_TOKEN` | `vmc_new_product_audit.py` | Same token, different name used by the audit |
| `NOTION_PRODUCTS_DB_ID` | All scripts | Products database ID |
| `ANTHROPIC_API_KEY` | `lib_anthropic.py` | Optional. Enables LLM descriptions and vegan adjudication. Falls back to stubs if absent. |

```bash
# Load all env vars for a manual run
set -a && source ./.env.local && set +a
```

---

## GitHub Actions Secrets

| Secret | Description |
|---|---|
| `NOTION_TOKEN` | Notion integration token |
| `NOTION_DB_ID` | Products database ID (has default) |
| `ANTHROPIC_API_KEY` | Anthropic API key (optional) |

## Vercel Environment Variables (webhook handler)

| Variable | Description |
|---|---|
| `NOTION_WEBHOOK_SECRET` | Shared secret for verifying the `x-notion-signature` header |
| `GH_DISPATCH_TOKEN` | Fine-grained GitHub PAT with `actions:write` on the repo |
| `GH_OWNER`, `GH_REPO`, `GH_WORKFLOW` | Optional overrides; default to `mayaibuki/vegan-moto-club` and `product-audit.yml` |

---

## Known Limitations

- Keyword-based field inference (Brand, Category, Materials) can misclassify edge cases —
  for example, a page mentioning "leather" in a "no leather used" context will still trigger
  the animal-material flag. Shopify tag-based inference (Gender, Riding style, Waterproof)
  does not have this problem.
- Descriptions are currently written manually (Pro-quota) or via the fallback stub in
  `lib_anthropic.py`. LLM-quality descriptions require a working `ANTHROPIC_API_KEY`.
- Batch limit of 20 products per audit run. Large backlogs need multiple runs.
- Photo scraping relies on CSS selectors and URL patterns that differ across e-commerce
  platforms. Some images may be missed.
