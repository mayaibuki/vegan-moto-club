#!/usr/bin/env python3
"""
apply.py: write confirmed URL + Price changes to Notion, trash rows, or roll back.

Input  <run>/changes.json
       [{page_id, name, changes: {"URL": {before, after, reason, source},
                                  "Price": {before, after, reason, source}}}]
       "after": null on URL clears the link (hides the "View on Store" button).

Modes
  (default)       dry run: prints and writes a changelog, no Notion writes
  APPLY=1         write. A row is skipped if its current Notion value no longer
                  equals `before` (someone edited it since the snapshot).
  --trash IDS     move these pages to Notion trash (restorable for 30 days)
  --rollback      restore URL + Price from snapshot.json for every applied page

Only the URL and Price properties are ever written.
Ledgers: <run>/.applied_ledger.json, <run>/.trashed_ledger.json
Changelog: <run>/changelog-<stamp>.md / .csv
ENV: NOTION_API_KEY (read from the repo .env.local if unset)
"""
import os, csv, json, time, argparse, datetime
from notion_client import Client

from harvest import load_env, flatten

HERE = os.path.dirname(os.path.abspath(__file__))
TODAY = datetime.date.today().isoformat()
# Microseconds keep two runs started in the same second from sharing a changelog file.
STAMP = datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S-%f")
APPLY = os.environ.get("APPLY") == "1"
FIELDS = ("URL", "Price")


def client():
    load_env()
    return Client(auth=os.environ["NOTION_API_KEY"])


def ledger(run, name):
    path = os.path.join(run, name)
    try:
        return path, json.load(open(path))
    except Exception:
        return path, {}


def call_with_retry(fn, tries=5, **kw):
    """Notion call with backoff on 429/5xx. Updates set absolute values, so retrying is safe."""
    for attempt in range(1, tries + 1):
        try:
            return fn(**kw)
        except Exception as e:
            status = getattr(e, "status", None) or getattr(getattr(e, "response", None), "status_code", None)
            if status not in (429, 500, 502, 503, 504) or attempt == tries:
                raise
            wait = min(2 ** attempt, 30)
            print(f"    ! {status}; retry {attempt}/{tries - 1} in {wait}s")
            time.sleep(wait)


def to_prop(field, value):
    if field == "URL":
        return {"url": value or None}
    if field == "Price":
        return {"number": float(value)}
    raise ValueError(field)


def same(field, a, b):
    if field == "Price":
        try:
            return abs(float(a) - float(b)) < 0.005
        except (TypeError, ValueError):
            return a == b
    return (a or None) == (b or None)


def write_changelog(run, title, rows):
    """rows: [date, product, field, before, after, reason, source, result]"""
    csv_path = os.path.join(run, f"changelog-{STAMP}.csv")
    md_path = os.path.join(run, f"changelog-{STAMP}.md")
    with open(csv_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "product", "field", "before", "after", "reason", "source", "result"])
        w.writerows(rows)
    lines = [f"# {title} ({STAMP})\n\n", f"Mode: {'APPLIED' if APPLY else 'DRY RUN'} | {len(rows)} field changes\n\n",
             "| Product | Field | Before | After | Why | Result |\n|---|---|---|---|---|---|\n"]
    for d, prod, field, before, after, reason, source, result in rows:
        cell = lambda s: str(s).replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {cell(prod)} | {field} | {cell(before)} | {cell(after)} | {cell(reason)} | {result} |\n")
    open(md_path, "w").writelines(lines)
    print(f"Changelog: {md_path}\n           {csv_path}")


def apply_changes(run, changes_file="changes.json"):
    n = client()
    changes = json.load(open(os.path.join(run, changes_file)))
    lpath, done = ledger(run, ".applied_ledger.json")
    rows, applied, skipped = [], 0, 0
    for c in changes:
        pid, name = c["page_id"], c.get("name", "?")
        todo = {f: ch for f, ch in c["changes"].items() if f in FIELDS}
        if not todo:
            continue
        if pid in done and all(same(f, done[pid].get(f), ch["after"]) for f, ch in todo.items()):
            continue  # already applied in an earlier run
        cur = flatten(call_with_retry(n.pages.retrieve, page_id=pid)["properties"])
        props, result = {}, "applied" if APPLY else "dry run"
        for f, ch in todo.items():
            if not same(f, cur.get(f), ch["before"]):
                rows.append([TODAY, name, f, ch["before"], ch["after"], ch.get("reason", ""), ch.get("source", ""),
                             f"SKIPPED: Notion now has {cur.get(f)!r}"])
                continue
            props[f] = to_prop(f, ch["after"])
            rows.append([TODAY, name, f, ch["before"], ch["after"], ch.get("reason", ""), ch.get("source", ""), result])
        if not props:
            skipped += 1
            continue
        print(f"  [{'APPLY' if APPLY else 'WOULD'}] {name[:60]}: " +
              ", ".join(f"{f} {todo[f]['before']!r} -> {todo[f]['after']!r}" for f in props))
        if APPLY:
            call_with_retry(n.pages.update, page_id=pid, properties=props)
            done.setdefault(pid, {}).update({f: todo[f]["after"] for f in props})
            json.dump(done, open(lpath, "w"), indent=1)
            time.sleep(0.35)
        applied += 1
    write_changelog(run, "Store link + price audit", rows)
    print(f"\n{'APPLIED' if APPLY else 'DRY RUN'}: {applied} pages updated, {skipped} skipped")


def trash(run, ids):
    n = client()
    snap = {r["page_id"]: r for r in json.load(open(os.path.join(run, "snapshot.json")))}
    lpath, done = ledger(run, ".trashed_ledger.json")
    rows = []
    for pid in ids:
        name = snap.get(pid, {}).get("name", pid)
        print(f"  [{'TRASH' if APPLY else 'WOULD TRASH'}] {name}")
        if APPLY:
            try:
                call_with_retry(n.pages.update, page_id=pid, in_trash=True)
            except Exception:
                call_with_retry(n.pages.update, page_id=pid, archived=True)
            done[pid] = {"name": name, "url": snap.get(pid, {}).get("url"), "at": STAMP}
            json.dump(done, open(lpath, "w"), indent=1)
            time.sleep(0.35)
        rows.append([TODAY, name, "(page)", "live", "trash", "discontinued; approved by owner",
                     snap.get(pid, {}).get("url", ""), "applied" if APPLY else "dry run"])
    write_changelog(run, "Discontinued products moved to trash", rows)


def rollback(run):
    n = client()
    snap = {r["page_id"]: r for r in json.load(open(os.path.join(run, "snapshot.json")))}
    lpath, done = ledger(run, ".applied_ledger.json")
    rows = []
    for pid, fields in done.items():
        s = snap[pid]
        props = {f: to_prop(f, s["url"] if f == "URL" else s["price"]) for f in fields}
        print(f"  [{'RESTORE' if APPLY else 'WOULD RESTORE'}] {s['name']}: {list(props)}")
        if APPLY:
            call_with_retry(n.pages.update, page_id=pid, properties=props)
            time.sleep(0.35)
        for f in fields:
            rows.append([TODAY, s["name"], f, fields[f], s["url"] if f == "URL" else s["price"], "rollback", "", "applied" if APPLY else "dry run"])
    write_changelog(run, "Rollback", rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True, help="run folder, e.g. runs/2026-09-13")
    ap.add_argument("--trash", default="", help="comma-separated page ids, or a .json list file in the run folder")
    ap.add_argument("--changes", default="changes.json", help="changes file in the run folder")
    ap.add_argument("--rollback", action="store_true")
    args = ap.parse_args()
    if args.rollback:
        rollback(args.run)
    elif args.trash:
        if args.trash.endswith(".json"):
            ids = json.load(open(os.path.join(args.run, args.trash)))
        else:
            ids = [i.strip() for i in args.trash.split(",") if i.strip()]
        trash(args.run, ids)
    else:
        apply_changes(args.run, args.changes)


if __name__ == "__main__":
    main()
