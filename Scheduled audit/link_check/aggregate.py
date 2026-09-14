#!/usr/bin/env python3
"""
aggregate.py: merge the agent review (Workflow result) into apply-ready files.

Input   <run>/workflow_result.json  the Workflow return value: {"results": [per-batch objects]}
        <run>/snapshot.json, <run>/bundles/
Output  <run>/decisions.json        one final outcome per product
        <run>/price_reads.json      -> prices.build() -> price_updates.json / price_review.json
        <run>/changes.json          confirmed URL + price changes, the input of apply.py
        <run>/discontinued.json/.md the list the owner decides on
        <run>/review.md             everything left for a human

Outcome per product, first rule that applies:
  URL_FIXED     a confirmer CONFIRMED a replacement link (price read from that page)
  OK            the fixer found the current link fine after all, or the matcher said MATCH
  DISCONTINUED  the Opus double-check found no live listing on the brand's store
  REVIEW        anything else (low-confidence match, rejected fix, missing verdict)
"""
import os, re, json, argparse, datetime
from collections import defaultdict
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse

import prices

HERE = os.path.dirname(os.path.abspath(__file__))
TODAY = datetime.date.today().isoformat()
STAGES = ("triage", "match", "price", "fix", "confirm", "disc", "routed_to_fix")
DROP_PARAMS = re.compile(r"^(_pos|_psq|_ss|_v|_sid|_psid|_fid|utm_.*|gclid|fbclid|srsltid|ref|variant)$", re.I)


def clean_url(u):
    """Drop search/tracking params (Shopify search adds ?_pos=..&_psq=..) and fragments."""
    p = urlparse((u or "").strip())
    q = [(k, v) for k, v in parse_qsl(p.query, keep_blank_values=True) if not DROP_PARAMS.match(k)]
    return urlunparse(p._replace(query=urlencode(q), fragment=""))


UNSAFE = re.compile(r"casino|gambling|spam|hijack|malware|phishing|porn", re.I)


def load_results(path):
    res = json.load(open(path))
    if isinstance(res, dict) and "result" in res:  # raw Workflow output file
        res = res["result"]
    if isinstance(res, dict):
        res = res.get("results", [])
    return [r for r in res if r]


def availability(bundle):
    """True / False / None from Shopify or JSON-LD, for the sold-out note."""
    if not bundle:
        return None
    sh = bundle.get("shopify") or {}
    if sh.get("available_any") is not None:
        return bool(sh["available_any"])
    for p in bundle.get("jsonld") or []:
        for o in p.get("offers") or []:
            a = (o.get("availability") or "").lower()
            if "outofstock" in a or "discontinued" in a:
                return False
            if "instock" in a:
                return True
    return None


def md_cell(s):
    return str(s if s is not None else "").replace("|", "\\|").replace("\n", " ")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True, help="run folder, e.g. runs/2026-09-13")
    ap.add_argument("--result", default="")
    args = ap.parse_args()
    run = args.run
    snap = {r["page_id"]: r for r in json.load(open(os.path.join(run, "snapshot.json")))}
    dashless = {k.replace("-", ""): k for k in snap}
    bundles = {}
    bdir = os.path.join(run, "bundles")
    for f in os.listdir(bdir):
        if f.endswith(".json"):
            b = json.load(open(os.path.join(bdir, f)))
            bundles[b["page_id"]] = b

    by = defaultdict(lambda: defaultdict(list))
    paths = [p for p in (args.result or os.path.join(run, "workflow_result.json")).split(",") if p]
    for path in paths:
        # A later result file replaces everything earlier files said about the same product.
        fresh = defaultdict(lambda: defaultdict(list))
        for item in load_results(path):
            for stage in STAGES:
                for row in item.get(stage) or []:
                    pid = dashless.get(str(row.get("page_id", "")).replace("-", "").strip())
                    if pid:
                        fresh[pid][stage].append(row)
        for pid, stages in fresh.items():
            by[pid] = stages

    # Corrections of agent verdicts, each with its reason: {page_id: {why, still_sold_at, successor, clear_url}}.
    # Only "move to the discontinued list" is supported.
    ov_path = os.path.join(run, "overrides.json")
    overrides = {}
    if os.path.exists(ov_path):
        overrides = {dashless.get(k.replace("-", ""), k): v for k, v in json.load(open(ov_path)).items()}

    decisions, reads, url_changes, disc, review = [], [], [], [], []
    for pid, row in snap.items():
        s = by.get(pid, {})
        base = {k: row[k] for k in ("page_id", "name", "brand", "url", "price")}
        match = (s.get("match") or [None])[-1]
        fixes, discs = s.get("fix", []), s.get("disc", [])
        confirmed = [c for c in s.get("confirm", []) if c.get("verdict") == "CONFIRMED" and c.get("proposed_url")]
        current_ok = [f for f in fixes if f.get("outcome") == "CURRENT_OK"]
        trail = {
            "health": (bundles.get(pid) or {}).get("bucket"),
            "match": match and f"{match.get('verdict')} ({match.get('confidence')}): {match.get('evidence')}",
            "fix": "; ".join(f"{f.get('outcome')}: {f.get('notes')}" for f in fixes) or None,
            "confirm": "; ".join(f"{c.get('verdict')} {c.get('proposed_url')}: {c.get('reason')}" for c in s.get("confirm", [])) or None,
            "disc": "; ".join(f"{d.get('verdict')}: {d.get('evidence')}" for d in discs) or None,
        }
        ov = overrides.get(pid)
        if ov:
            trail["override"] = ov.get("why")
            if ov.get("clear_url") and row["url"]:
                url_changes.append({"page_id": pid, "name": row["name"], "before": row["url"], "after": None,
                                    "reason": ov.get("why"), "source": "override"})
            disc.append({**base, "category": row.get("category"), "gender": row.get("gender"),
                         "vegan_verified": row.get("vegan_verified"),
                         "link_status": "cleared" if ov.get("clear_url") else trail["health"],
                         "still_sold_at": ov.get("still_sold_at") or [], "successor": ov.get("successor") or "",
                         "evidence": ov.get("why") or ""})
            decisions.append({**base, "outcome": "DISCONTINUED", "trail": trail})
            continue
        if confirmed:
            c = confirmed[-1]
            new = clean_url(c["proposed_url"])
            outcome = "URL_FIXED" if new != row["url"] else "OK"
            if outcome == "URL_FIXED":
                url_changes.append({"page_id": pid, "name": row["name"], "before": row["url"], "after": new,
                                    "reason": c.get("reason") or "confirmed replacement link",
                                    "source": c.get("store_type") or "confirmer"})
            if c.get("regular_price") is not None:
                reads.append({"page_id": pid, "regular_price": c["regular_price"], "currency": c.get("currency"),
                              "confidence": c.get("confidence") or "medium", "source": f"confirmer on {new}"})
            decisions.append({**base, "outcome": outcome, "new_url": new, "trail": trail})
        elif current_ok:
            f = current_ok[-1]
            if f.get("regular_price") is not None:
                reads.append({"page_id": pid, "regular_price": f["regular_price"], "currency": f.get("currency"),
                              "confidence": "medium", "source": "fixer re-check of current link"})
            decisions.append({**base, "outcome": "OK", "trail": trail})
        elif match and match.get("verdict") == "MATCH":
            if match.get("confidence") == "low":
                review.append({**base, "why": "low-confidence product match; link and price left unchanged", "trail": trail})
                decisions.append({**base, "outcome": "REVIEW", "trail": trail})
                continue
            for p in s.get("price", []):
                reads.append({"page_id": pid, "regular_price": p.get("regular_price"), "currency": p.get("currency"),
                              "confidence": p.get("confidence"), "source": p.get("source")})
            decisions.append({**base, "outcome": "OK", "trail": trail})
        elif any(d.get("verdict") == "DISCONTINUED" for d in discs):
            d = [x for x in discs if x.get("verdict") == "DISCONTINUED"][-1]
            # A store domain taken over by a casino or spam site: clear the link now so the
            # button hides; the owner still decides keep or trash for the row itself.
            unsafe = bool(UNSAFE.search(" ".join(filter(None, [d.get("evidence"), trail["fix"]]))))
            if unsafe and row["url"]:
                url_changes.append({"page_id": pid, "name": row["name"], "before": row["url"], "after": None,
                                    "reason": "store domain now hosts an unrelated casino/spam site; link cleared",
                                    "source": "discontinued check"})
            disc.append({**base, "category": row.get("category"), "gender": row.get("gender"),
                         "vegan_verified": row.get("vegan_verified"),
                         "link_status": "cleared (domain now a spam site)" if unsafe else trail["health"],
                         "still_sold_at": d.get("still_sold_at") or [],
                         "successor": d.get("successor") or "", "evidence": d.get("evidence") or ""})
            decisions.append({**base, "outcome": "DISCONTINUED", "trail": trail})
        else:
            review.append({**base, "why": "no confirmed link and not proven discontinued" if s else "no agent verdict",
                           "trail": trail})
            decisions.append({**base, "outcome": "REVIEW", "trail": trail})

    json.dump(decisions, open(os.path.join(run, "decisions.json"), "w"), indent=1, ensure_ascii=False)
    json.dump(reads, open(os.path.join(run, "price_reads.json"), "w"), indent=1, ensure_ascii=False)
    json.dump(url_changes, open(os.path.join(run, "url_changes.json"), "w"), indent=1, ensure_ascii=False)
    updates, price_review = prices.build(run)

    changes = {}
    for u in url_changes:
        changes.setdefault(u["page_id"], {"page_id": u["page_id"], "name": u["name"], "changes": {}})["changes"]["URL"] = {
            "before": u["before"], "after": u["after"], "reason": u["reason"], "source": u["source"]}
    for p in updates:
        changes.setdefault(p["page_id"], {"page_id": p["page_id"], "name": p["name"], "changes": {}})["changes"]["Price"] = {
            "before": p["before"], "after": p["after"], "reason": p["reason"], "source": p["source"]}
    json.dump(list(changes.values()), open(os.path.join(run, "changes.json"), "w"), indent=1, ensure_ascii=False)

    # Discontinued list (numbered, for the owner's keep/trash decision)
    disc.sort(key=lambda d: ((d["brand"] or "").lower(), d["name"].lower()))
    json.dump(disc, open(os.path.join(run, "discontinued.json"), "w"), indent=1, ensure_ascii=False)
    lines = [f"# Discontinued products ({TODAY})\n\n",
             "Nothing here has been trashed. Reply with the numbers to move to Notion trash; the rest stay.\n\n",
             "| # | Product | Brand | Price | Link now | Still sold at | Successor | Evidence |\n|---|---|---|---|---|---|---|---|\n"]
    for i, d in enumerate(disc, 1):
        still = ", ".join(d["still_sold_at"][:3]) if d["still_sold_at"] else "nowhere found"
        lines.append(f"| {i} | {md_cell(d['name'])} | {md_cell(d['brand'])} | ${d['price']} | {md_cell(d['link_status'])} | "
                     f"{md_cell(still)} | {md_cell(d['successor'])} | {md_cell(d['evidence'])} |\n")
    soldout = [x for x in decisions if x["outcome"] in ("OK", "URL_FIXED") and availability(bundles.get(x["page_id"])) is False]
    if soldout:
        lines.append(f"\n## Sold out at the store right now ({len(soldout)}, not discontinued, no action needed)\n\n")
        for x in soldout:
            lines.append(f"- {x['name']} ({x['brand']})\n")
    open(os.path.join(run, "discontinued.md"), "w").writelines(lines)

    # Review list
    rl = [f"# Needs a human look ({TODAY})\n\n"]
    for r in review:
        rl.append(f"## {r['name']} ({r['brand']})\n- link: {r['url']}\n- why: {r['why']}\n")
        for k, v in r["trail"].items():
            if v:
                rl.append(f"- {k}: {md_cell(v)}\n")
        rl.append("\n")
    if price_review:
        rl.append("## Prices not applied\n\n| Product | Notion | Read | Currency | Reason |\n|---|---|---|---|---|\n")
        for p in price_review:
            rl.append(f"| {md_cell(p.get('name'))} | {p.get('notion_price')} | {p.get('regular_price')} | {p.get('currency')} | {md_cell(p.get('reason'))} |\n")
    open(os.path.join(run, "review.md"), "w").writelines(rl)

    counts = defaultdict(int)
    for d in decisions:
        counts[d["outcome"]] += 1
    print(dict(counts), f"| url changes {len(url_changes)} | price updates {len(updates)} | "
          f"price review {len(price_review)} | discontinued {len(disc)} | sold out {len(soldout)}")


if __name__ == "__main__":
    main()
