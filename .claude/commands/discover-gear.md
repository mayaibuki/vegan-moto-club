---
description: Discover new vegan motorcycle gear from one brand's Shopify store (argument = store base URL, e.g. https://revitsport.com/en-us). Scout, vegan screen, research, write, verify and photos are staged locally for owner review. Nothing is written to Notion before approval.
allowed-tools: Agent, Skill, WebFetch, WebSearch, Bash, Read, Write, Artifact, mcp__a0fe616a-ee45-48ad-826a-40d1bb70fdfe__notion-fetch, mcp__a0fe616a-ee45-48ad-826a-40d1bb70fdfe__notion-query-data-sources, mcp__a0fe616a-ee45-48ad-826a-40d1bb70fdfe__notion-create-pages, mcp__a0fe616a-ee45-48ad-826a-40d1bb70fdfe__notion-update-page, mcp__a0fe616a-ee45-48ad-826a-40d1bb70fdfe__notion-create-file-upload, mcp__a0fe616a-ee45-48ad-826a-40d1bb70fdfe__notion-get-file-download-urls
---

Store: `$ARGUMENTS`. Work in /Users/mayaibuki/Documents/Claude/vegan-moto-club. Read its CLAUDE.md and `docs/brand-voice.md` first.

Field mapping, description rules, photo rules and the green gate live in `~/.claude/scheduled-tasks/vmc-product-enrichment/SKILL.md` (steps 1, 2b, 4, 5, 6, 7). Follow them. Do not keep a second copy here.

## Hard rules

- Nothing is written to Notion before the owner approves a wave. A row with a real name is public within the hour, and a placeholder row would be picked up by the daily task. Staging is local.
- Never create select options, Materials included. Use the live option lists only.
- One row per model. Colourways of a model are duplicates. Men's and women's versions, and a jacket and its matching pants, are separate models.
- You coordinate only. You do not scrape or draft. Every agent call passes `model: "opus"`.
- Never call the Anthropic API or `Scheduled audit/lib_anthropic.py`.
- New agent files register only at session start. If `gear-vegan-expert` or `gear-photo-finder` is not available as a subagent type, use `general-purpose` with `model: "opus"` and tell it to read the matching file in `.claude/agents/` and follow it.

## Waves

- Wave 0: steps 1 to 3 for the whole catalog. Ends with the shortlist.
- Wave 1: a pilot of 10 shortlisted products through steps 4 to 7. Stop for approval.
- Later waves: about 15 products each, only after the pilot is approved.

## Steps

1. **Scout.** Brand slug `<brand>` (for example `revit`), run folder `Scheduled audit/discovery/<brand>/<YYYY-MM-DD>/`. Run `Scheduled audit/discovery/harvest_shopify.py`:
   - `catalog --base $ARGUMENTS --out <run>`
   - `models --run <run>`: keeps US-sellable products, groups colourways, sets scope and the leather pre-filter, prints the summary.
   - `specs --run <run>`: one paced fetch per surviving model. Run it in the background with nohup, logging to `<run>/specs.log`. It is resumable. On repeated 429s, rerun with `--pause 4`. Never run two fetchers at once: Shopify limits by IP across all stores.
2. **Duplicate check.** Query the whole data source `collection://3323ccff-5165-4a31-93bc-232407c82454` once (SQL mode). Drop a model when any colourway matches an existing row on: URL lowercased without query string or trailing slash; the handle (last URL path segment); or Brand plus normalised name (lowercase, without ®, ™, spaces, hyphens, periods, apostrophes). Record each drop with the matching Notion URL.
3. **Vegan screen.** `gear-vegan-expert` in batches of about 25 models, up to 3 batches in parallel. Pass spec file paths and catalog facts. Only `confirmed_by_maker` and `vegan_by_ai` continue. Save `<run>/vegan_screen.json` and a shortlist with counts per verdict.
4. **Per product, up to 3 in parallel:** `gear-researcher`, then `gear-writer` (give it the vegan verdict and quotes, the live option lists, the colourway handles, the EUR and GBP rates), then `gear-verifier`. A failed verification goes back to the writer once with the findings; a second fail blocks the product. Then `gear-photo-finder` with the colourway image URLs and the destination folder. Map `confirmed_by_maker` to "Confirmed Vegan by maker" and `vegan_by_ai` to "Verified Vegan by AI".
5. **Voice pass.** `humanizer` skill in embedded mode on each description, then one batched `marketing:brand-review` over all of them against `docs/brand-voice.md`. Apply High and Medium fixes. Final check: 4 to 6 sentences, under 900 characters, no em or en dashes.
6. **Review page.** One local HTML page per wave in the run folder: photos, every field, description, vegan evidence quotes, verifier result, store link, green gate result. Then lists of rejected, unknown and blocked models. Publish it as a private artifact and give the owner the link.
7. **STOP.** Wait for the owner to approve the wave, product by product if they choose.
8. **After approval only.** For each approved product that passes the green gate: create the row fully populated with its real name using `notion-create-pages`. Then attach photos: `notion-create-file-upload`, upload the file (curl needs `;type=image/jpeg` on the file part), then `notion-update-page` with `file_upload` objects, because create-pages rejects uploads. Fetch each row back to confirm, and check the product page on www.veganmotoclub.com after the cache refreshes. Rows that miss the gate are not created.

## Report

Write `<run>/wave-N-report.md`: counts per step, the duplicate drops, the vegan verdict counts, every product with its gate result, blocked items with the reason, and tool failures. Finish with a 5-line chat summary and the review page link.

## Notes from the first run (REV'IT!, 2026-11-13)

- Scripted page fetches come first. If the store throttles them (REV'IT! allowed about one product page per 15 minutes), switch to ONE scout agent reading pages in the browser at about one page every 5 to 6 seconds. Drawer contents are in the DOM without clicking; also capture the Description block and the Highlights list, which sit outside the drawers. Do not burst-fetch sample pages during reconnaissance.
- Working files of that run are the template: `Scheduled audit/discovery/revit/2026-11-13/` has `extract.js`, `save_spec.py`, `facts.py`, `prep_products.py`, `vegan/BRIEF.md`, the stage briefs in `pipeline/`, `hold.json` and `morning-report.md`.
- Photos: `distinct_count` counts image files. Pool other colourways and studio on-model shots to reach 3. The photo agent also does a vegan visual check (cuff prints, waistband patches); a flag blocks publishing.
- Extra vegan rules found in practice: jeans need the maker's Vegan label or a stated leather-free patch; plain "suede" or "nubuck" is animal; "PrimaLoft" alone is not proof of a synthetic fill (the Solar 2 cuff print says Down Blend).
- Publishing without a review stop happens only when the owner says so for that run (they did on 2026-11-13). The default stays: stage locally and stop.
- The Notion row-query allowance is small. Do the whole-DB duplicate query once, save it locally, and use `notion-search` plus the local file for per-product checks.
