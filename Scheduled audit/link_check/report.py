#!/usr/bin/env python3
"""
report.py: the owner's summary of a link audit run, as Markdown.

Input   <run>/decisions.json, changes.json, discontinued.json, review.md,
        the latest changelog-*.csv that was APPLIED (falls back to the latest dry run)
Output  <run>/REPORT.md
"""
import os, csv, glob, json, argparse, datetime
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))


def cell(s):
    return str(s if s is not None else "").replace("|", "\\|").replace("\n", " ")


def money(v):
    try:
        v = float(v)
    except (TypeError, ValueError):
        return str(v)
    return f"${v:,.0f}" if v.is_integer() else f"${v:,.2f}"


def latest_changelog(run):
    rows, mode = [], "dry run"
    for path in sorted(glob.glob(os.path.join(run, "changelog-*.csv")), reverse=True):
        with open(path) as f:
            got = list(csv.DictReader(f))
        if any(r["result"] == "applied" for r in got):
            return got, "applied"
        if not rows and got and got[0]["field"] != "(page)":
            rows = got
    return rows, mode


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    run = ap.parse_args().run
    dec = json.load(open(os.path.join(run, "decisions.json")))
    disc = json.load(open(os.path.join(run, "discontinued.json")))
    log, mode = latest_changelog(run)
    counts = Counter(d["outcome"] for d in dec)
    url_rows = [r for r in log if r["field"] == "URL"]
    price_rows = [r for r in log if r["field"] == "Price"]
    done = lambda r: r["result"] in ("applied", "dry run")
    skipped = [r for r in log if r["result"].startswith("SKIPPED")]
    today = datetime.date.today().isoformat()

    L = [f"# Store link audit ({today})\n\n",
         f"All {len(dec)} products in the Notion database were checked. Notion changes: **{mode}**.\n\n",
         "| | Products |\n|---|---|\n",
         f"| Link works and shows the right product | {counts['OK']} |\n",
         f"| Link fixed | {sum(1 for r in url_rows if done(r) and r['after'] not in ('', 'None'))} |\n",
         f"| Link cleared (store domain now a spam site) | {sum(1 for r in url_rows if done(r) and r['after'] in ('', 'None'))} |\n",
         f"| Price updated to the store's regular price | {sum(1 for r in price_rows if done(r))} |\n",
         f"| Discontinued, waiting for your decision | {len(disc)} |\n",
         f"| Left for a human look | {counts['REVIEW']} |\n\n"]

    nowhere = sum(1 for d in disc if not d["still_sold_at"])
    L.append("## Your decision: discontinued products\n\n"
             f"Nothing has been trashed. {nowhere} of these {len(disc)} can't be bought anywhere; the other "
             f"{len(disc) - nowhere} are still sold by some store (often old stock). Reply with the numbers to move "
             "to Notion trash (restorable for 30 days), or a shortcut: \"trash all\" or \"trash the ones nobody sells\". "
             "Everything else stays. For the ones you keep, I'll clear the link so the \"View on Store\" button hides, "
             "unless you'd rather point it at a store that still has stock.\n\n"
             "| # | Product | Brand | Price | Still sold at | Newer model |\n|---|---|---|---|---|---|\n")
    for i, d in enumerate(disc, 1):
        still = "<br>".join(d["still_sold_at"][:2]) if d["still_sold_at"] else "nowhere found"
        L.append(f"| {i} | {cell(d['name'])} | {cell(d['brand'])} | {money(d['price'])} | {cell(still)} | {cell(d['successor'])} |\n")
    L.append("\nWhy each one is on the list: see `discontinued.md` (one line of evidence per product).\n\n")

    fixed = [r for r in url_rows if done(r) and r["after"] not in ("", "None")]
    if fixed:
        L.append(f"## Links fixed ({len(fixed)})\n\n| Product | Old link | New link |\n|---|---|---|\n")
        for r in fixed:
            L.append(f"| {cell(r['product'])} | {cell(r['before'])} | {cell(r['after'])} |\n")
        L.append("\n")
    cleared = [r for r in url_rows if done(r) and r["after"] in ("", "None")]
    if cleared:
        L.append("## Links cleared\n\n")
        for r in cleared:
            L.append(f"- {r['product']}: {r['before']} ({r['reason']})\n")
        L.append("\n")

    prices = [r for r in price_rows if done(r)]
    if prices:
        def delta(r):
            try:
                return float(r["after"]) - float(r["before"])
            except ValueError:
                return 0
        prices.sort(key=lambda r: -abs(delta(r)))
        L.append(f"## Prices updated ({len(prices)})\n\nRegular (non-sale) price, in USD. Largest changes first.\n\n"
                 "| Product | Before | After | Source |\n|---|---|---|---|\n")
        for r in prices:
            L.append(f"| {cell(r['product'])} | {money(r['before'])} | {money(r['after'])} | {cell(r['reason'])} |\n")
        L.append("\n")

    if skipped:
        L.append("## Not written because the row changed in Notion since the snapshot\n\n")
        for r in skipped:
            L.append(f"- {r['product']} ({r['field']}): {r['result']}\n")
        L.append("\n")

    L.append(f"## Left for a human look ({counts['REVIEW']})\n\nDetails in `review.md`: low-confidence matches, "
             "links no agent could confirm, and price drops over 25% that look like sales.\n\n")
    L.append("## Undo\n\nEvery change is logged in the changelog CSV next to this file. To restore every URL and price "
             f"to its value before the audit: `APPLY=1 python3 apply.py --run \"{run}\" --rollback`.\n")
    open(os.path.join(run, "REPORT.md"), "w").writelines(L)
    print(os.path.join(run, "REPORT.md"))


if __name__ == "__main__":
    main()
