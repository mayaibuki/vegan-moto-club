# Store link audit

Checks every product's "View on Store" link and price in the Notion products database, fixes broken links, corrects prices, and lists discontinued products for the owner to decide on. First run: September 2026, 443 products.

Needs `NOTION_API_KEY` and `NOTION_PRODUCTS_DB_ID` (read from the repo's `.env.local` if not set), Python 3.9+, `requests`, `beautifulsoup4`, `notion-client` 3.x and `playwright` with Chromium. Run data goes in `runs/<date>/`, which is gitignored.

## Pipeline

1. **Harvest.** `python3 harvest.py --all` saves `runs/<date>/snapshot.json` (every row's URL and price before any change, the rollback source) and fetches every link. If stores rate-limit, finish with `python3 harvest.py --all --resume --run runs/<date>`.
2. **Enrich and batch.** `python3 harvest.py --enrich --run runs/<date>` fills missing Shopify currencies and page-checks catalog prices that differ from Notion. `python3 harvest.py --batches --run runs/<date>` splits rows into agent batches (`batches/index.json`).
3. **Agent review.** Run `workflow.js` with Claude Code's Workflow tool. Args: `{run, tool, triage, match, fix}`, where `run` is the absolute run folder, `tool` the absolute path to `harvest.py`, and the rest are batch labels from `batches/index.json`. Haiku triages unclear pages and reads prices; Sonnet matches products, finds replacement links and confirms them independently; Opus double-checks anything headed for the discontinued list. Save each returned JSON into the run folder.
4. **Aggregate.** `python3 aggregate.py --run runs/<date> --result <file1>,<file2>` merges the verdicts (a later file wins for the same product; `overrides.json` records manual corrections with their reason) and writes `changes.json`, `discontinued.json`, `review.md` and the price files, using the rules in `prices.py`.
5. **Apply.** `python3 apply.py --run runs/<date>` is a dry run; add `APPLY=1` to write. Only `URL` and `Price` are ever written, and a row edited in Notion since the snapshot is skipped. Also: `--trash <ids or file.json>`, `--changes <file.json>`, `--rollback`.
6. **Owner review.** `python3 report.py --run ...` writes `REPORT.md`. `python3 review_page.py --run ...` builds the Trash/Keep page, published as an artifact with the `db` capability; the owner's choices land in the `review/discontinued` document.

## Rules the owner set

- **Prices:** the store's regular (non-sale) price, in USD. Other currencies are converted at the day's ECB rate, and a converted price within 5% of Notion is left alone. Drops over 25% and moves over 60% go to review.
- **Links:** the brand's own US store first; a major US retailer only when the brand doesn't sell online itself. A product the brand stopped listing counts as discontinued. It is not swapped for leftover retailer stock, another country's store, or a newer model, because vegan status is specific to each product.
- **Trash:** nothing is trashed without the owner's choice.

## Things that bite

- Shopify rate-limits a visitor's IP across all Shopify stores at once. `harvest.py` gives every Shopify host one shared request slot (1.5 s apart) and reads big stores' catalogs from `/products.json` instead of loading a page per product.
- Shopify Markets: REV'IT! prices its root domain in EUR and `/en-us/` in USD, so product and cart endpoints are called under the same market folder as the page.
- Some stores (REV'IT!) show a sale only on the page, never as a Shopify compare-at price. The enrich step exists for that.
- Every command except `harvest.py --all` needs `--run`, so a run can't silently switch folders at midnight.
