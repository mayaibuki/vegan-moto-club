# Product Audit Automations

## Overview

Two Python scripts for daily automated auditing and enrichment of the Notion product database. Both scripts scrape product URLs submitted by users, map the scraped data onto the fixed Notion schema using keyword matching, and generate dated reports for human review.

## Scripts

### vmc_product_audit.py -- Existing Product Audit

Audits existing Notion product entries for completeness and consistency.

- Queries the Notion database for entries that have a `userDefined:URL` but an empty `Description`
- Scrapes each product URL using `requests` + `BeautifulSoup`
- Extracts: product name, description, price, photos, and full page text
- Maps scraped data onto the Notion schema via keyword matching (`match_option`, `match_multi`)
- Infers vegan status from page text (`infer_vegan_status`) -- checks for phrases like "confirmed vegan", "synthetic", "textile", etc.
- Updates Notion page properties and uploads up to 5 product photos as external file links
- Never creates new select options -- only matches against the hardcoded `VALID` dict of known brands, categories, materials, genders, protection levels, waterproof levels, riding styles, and seasons
- Sleeps 1.5s between requests to be polite to product servers
- Key functions: `scrape_product`, `map_fields`, `build_notion_props`, `update_entry`, `run_audit`

### vmc_new_product_audit.py -- New Product Enrichment

Finds new user-submitted entries (URL present, Description empty) and enriches them with scraped data, a generated description, and downloaded photos.

- Queries Notion for entries where `userDefined:URL` is not empty and `Description` is empty, sorted by `Created time` ascending
- Batch limit: 20 products per run (`BATCH_LIMIT = 20`)
- Has a `TRUSTED_DOMAINS` allowlist of 16 known retailer/brand domains (RevZilla, Dainese, Alpinestars, REV'IT, Klim, etc.)
- Runs an `is_actively_for_sale` liveness check on each URL -- looks for discontinued/sold-out signals and verifies a price or add-to-cart button exists
- Scrapes product name, price, and up to 7 photos; checks each photo URL with a HEAD request to detect broken images
- Downloads working photos to `WORKSPACE_DIR/Photos/<brand-slug>/<product-slug>/`
- Writes a humanized 4-6 sentence product description using `write_description` (template-based, no LLM call required)
- Sets `Vegan Verified` to one of: "Confirmed Vegan by maker", "Verified Vegan by AI", or "Waiting for confirmation as Vegan" based on page text analysis
- Auto-applies all changes to Notion, then writes two report files:
  - `new-product-audit-YYYY-MM-DD.md` -- markdown summary with per-product status
  - `new-product-audit-YYYY-MM-DD.html` -- interactive review page with Apply/Skip buttons per product
- Same schema constraint: never creates new select options
- Key functions: `process_entry`, `get_new_entries`, `build_notion_props`, `build_md_report`, `build_html_review`, `run_audit`

## Environment Variables

### Required (both scripts)

| Variable | Description |
|---|---|
| `NOTION_TOKEN` | Notion integration token (starts with `secret_...`) |

### Optional (both scripts)

| Variable | Default | Description |
|---|---|---|
| `NOTION_DB_ID` | `3323ccff-5165-4a31-93bc-232407c82454` | Notion products database ID |

### Optional (vmc_new_product_audit.py only)

| Variable | Default | Description |
|---|---|---|
| `WORKSPACE_DIR` | `/sessions/gifted-confident-shannon/mnt/Scheduled audit` | Directory for saving reports and downloaded photos |

Note: `OPENAI_API_KEY` is mentioned in the `vmc_product_audit.py` docstring as optional for LLM-assisted field mapping, but is not actually used in the current code. Neither script calls an external LLM.

## Schema Constraints

Both scripts maintain a hardcoded `VALID` dictionary containing every allowed select/multi-select option for the Notion database. When mapping scraped data to Notion fields, the scripts use keyword matching (substring search, case-insensitive) to find the closest match from the existing options. If no match is found, the field is left blank.

This is a deliberate design decision: the Notion database has a curated taxonomy of brands, materials, categories, and other properties. Allowing scripts to create new options would pollute the taxonomy with duplicates, typos, and inconsistent naming. By restricting to existing options only, the scripts preserve the integrity of the database.

The tradeoff is that keyword matching can misclassify edge cases or miss valid matches when the page text does not contain the expected keywords.

## Running

### Manual / batch mode

```bash
NOTION_TOKEN=secret_... python "Scheduled audit/vmc_product_audit.py"
NOTION_TOKEN=secret_... python "Scheduled audit/vmc_new_product_audit.py"
```

### Single-product mode (event-driven)

```bash
NOTION_TOKEN=secret_... python "Scheduled audit/vmc_new_product_audit.py" --page-id <notion-page-id>
```

This skips the database query and processes one page directly. Used by the
Notion webhook flow (see below).

### Event-driven flow

1. User submits a product via the form on veganmotoclub.com (writes a row to Notion).
2. Notion fires a webhook to `POST /api/notion-webhook` (handler at `app/api/notion-webhook/route.ts`).
3. Handler verifies the signature, then calls GitHub's `workflow_dispatch` API to run `.github/workflows/product-audit.yml` with `page_id` set.
4. The action runs `vmc_new_product_audit.py --page-id <id>` which scrapes, enriches, writes back to Notion, and uploads the markdown + HTML report as a workflow artifact.

A weekly cron in the same workflow (Mondays 09:00 UTC) runs full batch mode as a safety net for anything the webhook missed.

## LLM integration

`lib_anthropic.py` is a thin wrapper around the Anthropic SDK used by the new product audit:

- **Description writing** - replaces the old template stub. Calls Haiku 4.5 with the humanizer rules baked into a cached system prompt.
- **Vegan adjudication** - only triggered when the keyword pass returns an ambiguous result (both animal and synthetic signals, or neither). Returns one of the three canonical statuses.

Both helpers fall back to deterministic stubs when `ANTHROPIC_API_KEY` is not set, so the script keeps working without the key.

## Dependencies

- `requests`
- `beautifulsoup4`
- `notion-client`
- `anthropic` (optional; needed for LLM-powered descriptions and vegan adjudication)

## Required secrets (GitHub Actions)

| Secret | Description |
|---|---|
| `NOTION_TOKEN` | Notion integration token |
| `NOTION_DB_ID` | Products database id (optional, has default) |
| `ANTHROPIC_API_KEY` | Anthropic API key for description writing |

## Vercel env vars (webhook handler)

| Variable | Description |
|---|---|
| `NOTION_WEBHOOK_SECRET` | Shared secret used to verify the `x-notion-signature` header |
| `GH_DISPATCH_TOKEN` | Fine-grained GitHub PAT with `actions:write` on the repo |
| `GH_OWNER`, `GH_REPO`, `GH_WORKFLOW` | Optional overrides; default to `mayaibuki/vegan-moto-club` and `product-audit.yml` |

## Known Limitations

- Field mapping is keyword-based and may misclassify edge cases (e.g., a product page that mentions "leather" in a "no leather" context will trigger the animal-material flag)
- The `write_description` function in the new product script generates a template-based description rather than using an LLM, so descriptions are formulaic
- Batch limit of 20 products per run on the new product audit -- large backlogs require multiple runs
- Photo detection relies on CSS selectors and URL patterns that vary across e-commerce platforms; some product images may be missed
- Future improvement: replace keyword matching with LLM-based extraction for better accuracy in field mapping and vegan verification
