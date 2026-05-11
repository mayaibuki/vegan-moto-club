---
description: Refine VMC product rows in Notion that the Python audit script left with template descriptions or empty inferred fields. Uses Claude Code (Pro quota) instead of the Anthropic API.
allowed-tools: WebFetch, Bash, mcp__a0fe616a-ee45-48ad-826a-40d1bb70fdfe__notion-search, mcp__a0fe616a-ee45-48ad-826a-40d1bb70fdfe__notion-fetch, mcp__a0fe616a-ee45-48ad-826a-40d1bb70fdfe__notion-update-page
---

You are upgrading product entries in the Vegan Moto Club Notion database that were enriched by the deterministic Python audit script (`Scheduled audit/vmc_new_product_audit.py`). Those rows currently have a **template fallback description** and **empty structured fields** (Brand, Category, Riding style, Season) because the Anthropic API key has no credits. Your job is to fill them in properly using your own reasoning, then write back to Notion.

## Database

- **Workspace**: veganmotoclub
- **Products DB ID**: `3323ccff-5165-4a31-93bc-232407c82454`
- **Title property**: `Name of product`
- **Properties to refine**: `Description`, `Brand`, `Category`, `Gender`, `Riding style`, `Season`, `Level of Protection`, `Level of Waterproof`, `Materials`, `Vegan Verified`

## Step 1 — Read the schema constraints

The Python script enforces a strict "never invent new options" rule. The authoritative allowed-option lists live in `Scheduled audit/vmc_new_product_audit.py` in the `VALID` dict (around line 56). Open that file and read those lists into memory before doing anything else. You MUST only write values that appear in those lists. Values not in the list will cause the Notion API to 400.

The one exception is the `Materials` multi-select, where new options are acceptable — but prefer matches against existing options when possible.

## Step 2 — Find rows needing refinement

Use `mcp__a0fe616a-...__notion-search` or `notion-fetch` to query the products database. A row needs refinement if **any** of these are true:

- Description starts with `"The "` and contains `"is a"` and `"designed for riders who want synthetic, animal-free construction"` (the template fallback signature — see the `_fallback_description` function in `Scheduled audit/lib_anthropic.py` for the exact wording)
- Brand is empty AND URL is filled
- Category is empty AND URL is filled
- Riding style is empty AND URL is filled
- Season is empty AND URL is filled

**Process at most 10 rows per invocation** to keep the session manageable. Tell the user how many were eligible and how many you're tackling.

## Step 3 — For each row, fetch the product page

Use the `WebFetch` tool to pull the product URL. Ask the model to extract:

- Real product name (the page's h1, not the Notion title)
- Brand (actual maker, not retailer)
- Stated category, gender, riding style, season cues
- Materials mentioned in the spec sheet
- Stated protection certifications (CE Level 1/2, AAA/AA/A)
- Waterproofing technology (Gore-tex, D-Dry, Drystar, NextDry, Hydratex, generic waterproof, water resistant, none)
- Any explicit vegan claim, OR animal materials (leather, suede, wool, down, fur, nubuck, sheepskin, kangaroo)
- Price in original currency

## Step 4 — Map to schema

For every field you intend to write:

1. Check the value against the allowed list from Step 1.
2. If it doesn't match exactly, either find the closest match in the list or leave the field empty. **Never invent.**
3. Multi-select fields (Category, Gender, Riding style, Season, Materials) take an array.
4. Single-select fields (Brand, Level of Protection, Level of Waterproof, Vegan Verified) take one string or null.

### Vegan Verified mapping

- `Confirmed Vegan by maker` — brand or page explicitly says vegan / animal-free
- `Verified Vegan by AI` — all listed materials are clearly synthetic, no animal material mentioned
- `Waiting for confirmation as Vegan` — uncertain or mixed signals (default)

Do NOT use `Not vegan` even if you spot animal materials. The user reviews and archives manually.

## Step 5 — Write the description (humanizer rules)

4–6 sentences, plain prose. Strictly avoid:

- Em dashes (`—`) or double hyphens (`--`)
- Bullet points or headers
- AI vocabulary: `seamlessly`, `elevate`, `delve`, `cutting-edge`, `robust`, `transformative`, `leverage`, `harness`, `tapestry`, `multifaceted`, `pivotal`, `nuanced`, `comprehensive`, `intricate`, `spearhead`, `paradigm`, `underscored`, `underpin`
- Negative parallelisms (`not just X but Y`, `not only X but also Y`)
- Repeated rule-of-three lists
- Conjunctive pile-ups (`moreover`, `furthermore`, `additionally` stacked)
- Emojis
- Hype

Mix short and longer sentences. Active voice. Honest tone — include sizing quirks, limitations, or worth-knowing context where the source page mentions them. End the description with a useful detail, not a marketing flourish.

## Step 6 — Write back to Notion

Use `mcp__a0fe616a-...__notion-update-page` to PATCH each page. The property shape for Notion writes:

```json
{
  "Description":           {"rich_text":    [{"text": {"content": "..."}}]},
  "Brand":                 {"select":       {"name": "Atwyld"}},
  "Category":              {"multi_select": [{"name": "Pants"}]},
  "Gender":                {"multi_select": [{"name": "Women"}]},
  "Riding style":          {"multi_select": [{"name": "Commute / Street"}]},
  "Season":                {"multi_select": [{"name": "🌦 Mid season"}]},
  "Materials":             {"multi_select": [{"name": "Cordura® (Synhtetic fabric)"}]},
  "Level of Protection":   {"select":       {"name": "Moderately protective"}},
  "Level of Waterproof":   {"select":       {"name": "Water resistant"}},
  "Vegan Verified":        {"select":       {"name": "Verified Vegan by AI"}},
  "Price":                 {"number": 199}
}
```

Only include properties you are confident about. Omit ones you'd leave empty — don't pass `null`, just don't pass the property at all.

## Step 7 — Report

After all writes complete, print a markdown summary listing each refined row:

```
## Refined N products

- **{name}** ({notion url}) — Brand: {x} • Category: {x} • Riding style: {x} • Season: {x}
  Description: "{first sentence...}"
- ...

## Skipped

- ... (and why)
```

## Notes

- If `WebFetch` fails on a URL (404, 403, blocked), skip that row and note it.
- If the title is `Unknown product` or empty, treat the row as a fixable case — the real product name comes from the page's h1.
- If a row already has a non-template description AND most fields filled, skip it.
- If the user passes arguments to the slash command (e.g. a specific page id), refine just that page instead of querying for all needing refinement.
