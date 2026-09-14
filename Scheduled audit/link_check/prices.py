#!/usr/bin/env python3
"""
prices.py: turn store prices read by the agents into Notion price updates.

Input   <run>/price_reads.json  [{page_id, regular_price, currency, confidence, source, note}]
        <run>/snapshot.json     the Notion price of every row before the audit
Output  <run>/fx.json           USD exchange rates used (fetched once per run, then reused)
        <run>/price_updates.json  changes that pass the rules below
        <run>/price_review.json   reads that were not applied, with the reason

Rules (tune the constants):
  USD page:        update when |page - notion| >= USD_MIN_DIFF
  other currency:  convert at the ECB rate and round to whole dollars; update only
                   when the gap is more than FX_TOLERANCE of the Notion price
  any page:        low confidence, or a move bigger than MAX_SWING, goes to review
"""
import os, sys, json, argparse, datetime
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
TODAY = datetime.date.today().isoformat()

USD_MIN_DIFF = 1.0   # dollars
FX_TOLERANCE = 0.05  # 5% of the Notion price
MAX_SWING = 0.60     # a 60%+ move is more likely a wrong variant or bundle than a real change
MAX_DROP = 0.25      # a deeper cut is usually a sale (REV'IT! shows 30% off only on the page)

FX_SOURCES = [
    "https://api.frankfurter.dev/v1/latest?base=USD",
    "https://api.frankfurter.app/latest?from=USD",
]


def fx_rates(run):
    path = os.path.join(run, "fx.json")
    if os.path.exists(path):
        return json.load(open(path))
    for u in FX_SOURCES:
        try:
            r = requests.get(u, timeout=20)
            if r.status_code == 200:
                d = r.json()
                out = {"base": "USD", "date": d.get("date"), "source": u, "rates": d["rates"]}
                json.dump(out, open(path, "w"), indent=1)
                return out
        except Exception:
            continue
    sys.exit("Could not fetch exchange rates; refusing to guess.")


def to_usd(amount, currency, fx):
    cur = (currency or "USD").upper()
    if cur == "USD":
        return amount, 1.0
    rate = fx["rates"].get(cur)
    if not rate:
        return None, None
    return amount / rate, rate


def decide(snap_price, read, fx):
    """Return (update_dict | None, review_reason | None)."""
    try:
        amount = float(read.get("regular_price"))
    except (TypeError, ValueError):
        return None, "no readable price"
    if amount <= 0:
        return None, "no readable price"
    if (read.get("confidence") or "low") == "low":
        return None, "low-confidence price read"
    usd, rate = to_usd(amount, read.get("currency"), fx)
    if usd is None:
        return None, f"no exchange rate for {read.get('currency')}"
    cur = (read.get("currency") or "USD").upper()
    old = float(snap_price) if snap_price not in (None, "") else None
    new = round(usd, 2) if cur == "USD" else float(round(usd))
    if old is None or old == 0:
        return {"after": new, "rate": rate, "pct": None}, None
    pct = (new - old) / old
    if cur == "USD":
        if abs(new - old) < USD_MIN_DIFF:
            return None, None  # already right
    elif abs(pct) <= FX_TOLERANCE:
        return None, None      # conversion noise: leave as is
    if pct < -MAX_DROP:
        return None, f"price drop of {pct:+.0%} looks like a sale; left for review"
    if abs(pct) > MAX_SWING:
        return None, f"price move of {pct:+.0%} is too large to apply without review"
    return {"after": new, "rate": rate, "pct": round(pct, 4)}, None


def build(run):
    snap = {r["page_id"]: r for r in json.load(open(os.path.join(run, "snapshot.json")))}
    reads = json.load(open(os.path.join(run, "price_reads.json")))
    fx = fx_rates(run)

    updates, review, same = [], [], 0
    for rd in reads:
        row = snap.get(rd["page_id"])
        if not row:
            review.append({**rd, "reason": "page_id not in snapshot"})
            continue
        up, why = decide(row["price"], rd, fx)
        if why:
            review.append({**rd, "name": row["name"], "notion_price": row["price"], "reason": why})
        elif up:
            cur = (rd.get("currency") or "USD").upper()
            conv = "" if cur == "USD" else f" = ${up['after']:.0f} at {up['rate']:.4f} {cur}/USD (ECB {fx['date']})"
            updates.append({
                "page_id": rd["page_id"], "name": row["name"], "before": row["price"], "after": up["after"],
                "page_price": rd["regular_price"], "currency": cur, "fx_rate": up["rate"], "pct": up["pct"],
                "reason": f"store regular price {rd['regular_price']} {cur}{conv}",
                "source": rd.get("source") or "",
            })
        else:
            same += 1
    json.dump(updates, open(os.path.join(run, "price_updates.json"), "w"), indent=1, ensure_ascii=False)
    json.dump(review, open(os.path.join(run, "price_review.json"), "w"), indent=1, ensure_ascii=False)
    print(f"FX {fx['date']}: {len(updates)} price updates, {same} unchanged, {len(review)} to review")
    return updates, review


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True, help="run folder, e.g. runs/2026-09-13")
    build(ap.parse_args().run)


if __name__ == "__main__":
    main()
