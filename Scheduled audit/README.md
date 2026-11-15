# Scheduled Audit — Scripts Reference

Automation for maintaining and expanding the Vegan Moto Club Notion product database.
There are two categories of work here: **automatic enrichment** (a daily Claude Code scheduled
task) and **catalog expansion** scripts (run manually when adding a new brand or category).

---

## Automatic enrichment

The only automatic enrichment pass is the daily `vmc-product-enrichment` task below. New rows,
including site suggestions titled `User Suggestion - <host>`, wait for that run. The Notion
webhook (`app/api/notion-webhook/route.ts`) only refreshes the site cache; it does not start any
enrichment.

> **Retired 2026-11-14:** the Python audit (`vmc_new_product_audit.py`, its tests and
> `lib_anthropic.py`), its GitHub workflow (`product-audit.yml`) and the webhook dispatch to it
> were removed. They are in git history.

### `vmc-product-enrichment` (Claude Code desktop scheduled task)

A desktop scheduled task in Claude Code enriches new rows daily at 05:00 local while the Claude
app is open.
The rules live at `.claude/skills/vmc-product-enrichment/SKILL.md`, shared by both runners; the
manual entry point is `/refine-products [page ids]`. A cloud scheduled task (daily 19:00 UTC) is
the fallback for when the Mac is off; it skips when the Notion run log shows a run today. The
pasteable task bodies are `Scheduled audit/desktop-task-prompt.md` and
`Scheduled audit/cloud-task-prompt.md`.

Per row it runs three project subagents from `.claude/agents/`: `gear-researcher` (Reddit, forums,
YouTube and retailer reviews, with sponsored sources labelled and discounted), `gear-writer` (the
honest gear reviewer that turns maker copy into 4 to 6 plain sentences and the schema fields, each
backed by a quote) and `gear-verifier` (fails any claim without a source, any animal term missed,
any value outside the Notion option lists). Descriptions then pass the `humanizer` skill and a
batch `marketing:brand-review` against `docs/brand-voice.md`.

Queue: rows with a URL and a placeholder title, an empty or template description, or an empty
Brand, Category, Riding style, Season or Vegan Verified; oldest first, 10 per run. Photos are
HEAD-checked and topped up to 5 to 7. The row is renamed (which publishes it on the site) only when
it passes the green gate: real name, Brand, price, Category, Gender, protection level and a vegan
status set, no animal material in the spec, a verified description and at least 3 working photos.
Report: `Scheduled audit/audit/YYYY-MM-DD/enrichment-YYYY-MM-DD.md` (gitignored).

### Monthly SEO audit: `vmc-seo-audit` (Claude Code desktop scheduled task)

A read-only desktop scheduled task that audits veganmotoclub.com for SEO and GEO (AI search
visibility) on the first Monday of each month at 09:00 local, while the Claude app is open. Its
prompt lives at `~/.claude/scheduled-tasks/vmc-seo-audit/SKILL.md`. The cron is weekly
(`0 9 * * 1`) with a day-of-month guard at the top of the prompt, because the app's cron parser
does not combine day-of-month with weekday.

Scope per run: home, `/products`, the seven category pages from `CATEGORY_PAGES` in
`lib/constants.ts`, `/verification`, `/about`, five product pages picked at random from
`/feed.xml`, plus `robots.txt`, `sitemap.xml` and the product JSON-LD. It checks titles, meta
descriptions, H1s, canonical and OG tags, internal links, alt text, structured data, Core Web
Vitals (PageSpeed Insights; falls back to curl timings when the keyless quota is exhausted, add
`PAGESPEED_API_KEY` to `.env.local` to avoid that), the canonical host (apex vs www), AI crawler
access for Googlebot, Bingbot, PerplexityBot, GPTBot and ClaudeBot, answer-first copy and FAQ
schema opportunities. Keyword research (15 to 25 keywords with intent and a rough current
position) uses web search only; no Ahrefs or Similarweb connector is involved.

Tools: the local `seo-geo` skill (`.agents/skills/seo-geo/scripts/seo_audit.py`, no API key)
and the `marketing:seo-audit` skill with every input pre-filled. Everything runs on the Claude
Code subscription. The task never edits the site, never writes to Notion, never commits or opens
a PR; fixes are proposed in the report for the owner to pick up.

Report: `Scheduled audit/audit/YYYY-MM-DD/seo-audit-YYYY-MM-DD.md` (gitignored), with an
executive summary, an issues table with severity, a keyword table, a technical checklist, GEO
notes and a prioritized action plan. To run it by hand, click Run now on the task in the
Scheduled sidebar; `run_scheduled_task` from a session is refused by the auto-mode classifier.

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
| `export_revit_source.py` | Exports cleaned body_html feature text for each REV'IT! model to a local JSON file, for use when writing descriptions outside the enrichment task. |

---

## Environment Variables

All scripts read from `.env.local` at the project root.

| Variable | Required by | Description |
|---|---|---|
| `NOTION_API_KEY` | Catalog expansion + data quality scripts | Notion integration token |
| `NOTION_PRODUCTS_DB_ID` | All scripts | Products database ID |

```bash
# Load all env vars for a manual run
set -a && source ./.env.local && set +a
```

---

## Vercel Environment Variables (webhook handler)

| Variable | Description |
|---|---|
| `NOTION_WEBHOOK_SECRET` | Shared secret for verifying the `x-notion-signature` header. Needed for the cache refresh. |

---

## Known Limitations

- The enrichment task handles 10 rows per run. Large backlogs take several days.
