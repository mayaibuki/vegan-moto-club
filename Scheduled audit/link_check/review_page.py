#!/usr/bin/env python3
"""
review_page.py: build the owner's phone-friendly review page for a link audit run.

Input   <run>/discontinued.json, decisions.json, price_review.json, the applied changelog CSV,
        optional review_notes.json ({product name: plain-language note} for "needs a look" items)
Output  <run>/review.html  (published as an Artifact with capabilities {db: {}})

The page lists every discontinued product with a Trash / Keep choice. Choices are
saved to the artifact database at review/discontinued as
{choices: {page_id: "trash" | "keep"}, updated_at}, which Claude reads back with read_db.
"""
import os, re, csv, glob, json, argparse, datetime
from urllib.parse import urlparse

def host(u):
    h = urlparse(u or "").netloc.lower()
    return h[4:] if h.startswith("www.") else h


def split_url(s):
    """'https://x.com/p (closeout, out of stock)' -> (url, note)."""
    m = re.search(r"https?://[^\s,;]+", s or "")
    if not m:
        return None, (s or "").strip()
    url = m.group(0).rstrip(").,;")
    note = (s[:m.start()] + " " + s[m.end():]).strip(" ()-,;:")
    note = re.sub(r"^\(|\)$", "", note).strip()
    return url, note


def latest_applied(run):
    for path in sorted(glob.glob(os.path.join(run, "changelog-*.csv")), reverse=True):
        rows = list(csv.DictReader(open(path)))
        if any(r["result"] == "applied" for r in rows):
            return os.path.basename(path), [r for r in rows if r["result"] == "applied"]
    return None, []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    run = ap.parse_args().run
    # Optional plain-language notes for the "needs a look" items: {product name: note}.
    notes_path = os.path.join(run, "review_notes.json")
    notes = json.load(open(notes_path)) if os.path.exists(notes_path) else {}
    disc = json.load(open(os.path.join(run, "discontinued.json")))
    dec = json.load(open(os.path.join(run, "decisions.json")))
    price_review = json.load(open(os.path.join(run, "price_review.json")))
    log_name, log = latest_applied(run)

    items = []
    for i, d in enumerate(disc, 1):
        still = []
        for s in d.get("still_sold_at") or []:
            url, note = split_url(s)
            if not (url or note):
                continue
            oos = bool(re.search(r"out of stock|sold out|unavailable|no stock", s or "", re.I))
            still.append({"url": url, "host": host(url) if url else "",
                          "note": note if url else (s or "").strip(), "oos": oos})
        succ_url, succ_name = split_url(d.get("successor") or "")
        items.append({
            "n": i, "id": d["page_id"], "name": d["name"], "brand": d["brand"] or "Other",
            "price": d["price"], "category": ", ".join(d.get("category") or []),
            "gender": ", ".join(d.get("gender") or []), "vegan": d.get("vegan_verified") or "",
            "url": d.get("url") or "", "url_host": host(d.get("url")),
            "link": d.get("link_status") or "", "still": still,
            "successor": {"name": succ_name, "url": succ_url} if (succ_name or succ_url) else None,
            "evidence": d.get("evidence") or "",
            "notion": "https://www.notion.so/" + d["page_id"].replace("-", ""),
        })

    fixed = [{"product": r["product"], "before": r["before"], "after": r["after"],
              "before_host": host(r["before"]), "after_host": host(r["after"])}
             for r in log if r["field"] == "URL" and r["after"] not in ("", "None")]
    cleared = [{"product": r["product"], "before_host": host(r["before"]), "reason": r["reason"]}
               for r in log if r["field"] == "URL" and r["after"] in ("", "None")]
    prices = []
    for r in log:
        if r["field"] != "Price":
            continue
        try:
            b, a = float(r["before"]), float(r["after"])
        except ValueError:
            continue
        prices.append({"product": r["product"], "before": b, "after": a, "reason": r["reason"]})
    prices.sort(key=lambda p: -abs(p["after"] - p["before"]))

    review = []
    for d in dec:
        if d["outcome"] == "REVIEW":
            review.append({"product": d["name"], "brand": d["brand"], "url": d["url"],
                           "note": notes.get(d["name"], "No agent could confirm the right link.")})
    for p in price_review:
        review.append({"product": p.get("name"), "brand": "", "url": "",
                       "note": notes.get(p.get("name"), p.get("reason"))})

    outcome = {k: sum(1 for d in dec if d["outcome"] == k) for k in ("OK", "URL_FIXED", "DISCONTINUED", "REVIEW")}
    data = {
        "date": datetime.date.today().strftime("%-d %b %Y"),
        "checked": len(dec), "ok": outcome["OK"], "fixed": len(fixed), "cleared": len(cleared),
        "prices": len(prices), "nobody": sum(1 for x in items if not x["still"]),
        "changelog": log_name, "items": items, "fixedLinks": fixed, "clearedLinks": cleared,
        "priceChanges": prices, "review": review,
    }
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    html = TEMPLATE.replace("__DATA__", payload)
    out = os.path.join(run, "review.html")
    open(out, "w").write(html)
    print(out, f"{len(items)} products, {len(fixed)} fixed, {len(cleared)} cleared, {len(prices)} prices, {len(review)} review")


TEMPLATE = r"""<title>Discontinued Vegan Moto Gear</title>
<meta name="description" content="Trash or keep each discontinued product in the Vegan Moto Club catalog.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,700&display=swap">
<style>
:root {
  --bg: hsl(0 0% 98%);
  --surface: hsl(0 0% 100%);
  --surface-2: hsl(12 6.5% 96.5%);
  --text: hsl(12 8.7% 11.8%);
  --muted: hsl(12 6.5% 42%);
  --line: hsl(12 6.3% 91%);
  --line-strong: hsl(12 5.4% 80%);
  --accent: hsl(77.9 54.4% 47.4%);
  --accent-soft: hsl(79.9 84.6% 80.2% / .32);
  --on-accent: hsl(12 8.3% 7.2%);
  --link: hsl(84 70% 24%);
  --trash: hsl(0 68% 44%);
  --trash-soft: hsl(0 85% 96%);
  --on-trash: hsl(0 0% 100%);
  --focus: hsl(84 70% 30%);
  --sans: "DM Sans", ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif;
  --mono: "DM Mono", ui-monospace, "SF Mono", Menlo, Consolas, monospace;
  color-scheme: light;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: hsl(12 8.3% 7.2%);
    --surface: hsl(12 8.7% 10.5%);
    --surface-2: hsl(12 7% 13%);
    --text: hsl(30 10% 94%);
    --muted: hsl(12 4.9% 64%);
    --line: hsl(12 6.3% 17%);
    --line-strong: hsl(12 5% 27%);
    --accent: hsl(79.1 64.5% 57.5%);
    --accent-soft: hsl(79 55% 45% / .16);
    --on-accent: hsl(12 8.3% 7.2%);
    --link: hsl(79.7 77.9% 69.7%);
    --trash: hsl(0 78% 66%);
    --trash-soft: hsl(0 60% 35% / .2);
    --on-trash: hsl(12 8.3% 7.2%);
    --focus: hsl(79.7 77.9% 69.7%);
    color-scheme: dark;
  }
}
:root[data-theme="dark"] {
  --bg: hsl(12 8.3% 7.2%);
  --surface: hsl(12 8.7% 10.5%);
  --surface-2: hsl(12 7% 13%);
  --text: hsl(30 10% 94%);
  --muted: hsl(12 4.9% 64%);
  --line: hsl(12 6.3% 17%);
  --line-strong: hsl(12 5% 27%);
  --accent: hsl(79.1 64.5% 57.5%);
  --accent-soft: hsl(79 55% 45% / .16);
  --on-accent: hsl(12 8.3% 7.2%);
  --link: hsl(79.7 77.9% 69.7%);
  --trash: hsl(0 78% 66%);
  --trash-soft: hsl(0 60% 35% / .2);
  --on-trash: hsl(12 8.3% 7.2%);
  --focus: hsl(79.7 77.9% 69.7%);
  color-scheme: dark;
}

* { box-sizing: border-box; }
body {
  background: var(--bg);
  color: var(--text);
  font-family: var(--sans);
  font-size: 1rem;
  line-height: 1.5;
  padding-inline: 16px;
  padding-block: 28px 112px;
  -webkit-font-smoothing: antialiased;
}
a { color: var(--link); text-underline-offset: 2px; }
a:focus-visible, button:focus-visible, summary:focus-visible, textarea:focus-visible {
  outline: 2px solid var(--focus); outline-offset: 2px; border-radius: 4px;
}
.wrap { max-width: 46rem; margin-inline: auto; display: grid; gap: 40px; }
.mono { font-family: var(--mono); font-variant-numeric: tabular-nums; }

/* Masthead */
.mast { display: grid; gap: 14px; }
.kicker {
  margin: 0; font-size: .75rem; font-weight: 500; letter-spacing: .08em;
  text-transform: uppercase; color: var(--muted);
}
.kicker b { color: var(--text); font-weight: 700; letter-spacing: .06em; }
h1 {
  margin: 0; font-size: clamp(1.75rem, 5vw, 2.25rem); line-height: 1.1;
  font-weight: 700; letter-spacing: -.02em; text-wrap: balance;
}
.lede { margin: 0; max-width: 62ch; color: var(--muted); }
.lede strong { color: var(--text); font-weight: 500; }
.tally {
  margin: 6px 0 0; display: flex; flex-wrap: wrap; gap: 8px 28px;
  padding-top: 14px; border-top: 1px solid var(--line);
}
.tally div { display: grid; gap: 0; }
.tally dt { font-size: .75rem; color: var(--muted); letter-spacing: .02em; }
.tally dd { margin: 0; font-family: var(--mono); font-size: 1.25rem; font-variant-numeric: tabular-nums; }

/* Toolbar */
.decide { display: grid; gap: 18px; }
.decide-head { display: grid; gap: 6px; }
h2 { margin: 0; font-size: 1.25rem; line-height: 1.25; font-weight: 700; letter-spacing: -.01em; text-wrap: balance; }
.hint { margin: 0; color: var(--muted); font-size: .9375rem; max-width: 62ch; }
.toolbar { display: flex; flex-wrap: wrap; gap: 10px; align-items: center; justify-content: space-between; }
.seg {
  display: inline-flex; padding: 3px; gap: 2px; border-radius: 10px;
  background: var(--surface-2); border: 1px solid var(--line);
}
.seg button {
  font: inherit; font-size: .875rem; border: 0; background: transparent; color: var(--muted);
  padding: 6px 11px; border-radius: 7px; cursor: pointer; white-space: nowrap;
}
.seg button .mono { font-size: .8125rem; margin-left: 4px; }
.seg button[aria-pressed="true"] { background: var(--surface); color: var(--text); box-shadow: 0 1px 2px hsl(12 8% 10% / .12); }
.bulk {
  font: inherit; font-size: .875rem; cursor: pointer; padding: 7px 12px; border-radius: 8px;
  background: transparent; color: var(--trash); border: 1px solid currentColor;
}
.bulk:hover { background: var(--trash-soft); }

/* Brand groups and rows */
.brand { display: grid; }
.brand-name {
  display: flex; align-items: baseline; gap: 8px; margin: 0; padding: 18px 0 8px;
  font-size: .75rem; letter-spacing: .08em; text-transform: uppercase; font-weight: 700; color: var(--muted);
  border-bottom: 1px solid var(--line-strong);
}
.brand-name .mono { font-weight: 400; letter-spacing: 0; }
.item { padding: 14px 10px; margin-inline: -10px; border-bottom: 1px solid var(--line); display: grid; gap: 8px; border-radius: 6px; }
.item[data-state="trash"] { background: var(--trash-soft); }
.item[data-state="keep"] { background: var(--accent-soft); }
.item-head { display: grid; grid-template-columns: 2.25rem 1fr auto; gap: 4px 10px; align-items: start; }
.num { font-family: var(--mono); font-size: .8125rem; color: var(--muted); padding-top: 3px; font-variant-numeric: tabular-nums; }
.title { min-width: 0; }
.title h3 { margin: 0; font-size: 1.0625rem; font-weight: 500; line-height: 1.3; overflow-wrap: anywhere; }
.meta { margin: 2px 0 0; font-size: .8125rem; color: var(--muted); }
.meta .mono { color: var(--text); }
.choice { display: inline-flex; gap: 6px; }
.choice button {
  font: inherit; font-size: .875rem; font-weight: 500; cursor: pointer; min-width: 4.75rem;
  padding: 7px 12px; border-radius: 8px; background: var(--surface); color: var(--text);
  border: 1px solid var(--line-strong);
}
.choice button[data-v="trash"][aria-pressed="true"] { background: var(--trash); border-color: var(--trash); color: var(--on-trash); }
.choice button[data-v="keep"][aria-pressed="true"] { background: var(--accent); border-color: var(--accent); color: var(--on-accent); }
.avail { margin: 0 0 0 calc(2.25rem + 10px); font-size: .8125rem; display: flex; flex-wrap: wrap; gap: 6px 10px; align-items: center; }
.chip { display: inline-block; padding: 2px 8px; border-radius: 999px; font-size: .75rem; font-weight: 500; border: 1px solid var(--line-strong); color: var(--muted); }
.chip.sold { border-color: transparent; background: var(--accent-soft); color: var(--text); }
details.why { margin-left: calc(2.25rem + 10px); font-size: .875rem; }
details.why summary { cursor: pointer; color: var(--link); width: fit-content; }
.why-body { display: grid; gap: 8px; padding: 8px 0 2px; color: var(--muted); max-width: 62ch; }
.why-body p { margin: 0; }
.why-body b { color: var(--text); font-weight: 500; }
.stores { margin: 0; padding: 0; list-style: none; display: grid; gap: 4px; }
.stores .mono { font-size: .8125rem; }
.note { color: var(--muted); }
.item.hidden, .brand.hidden { display: none; }

/* Reply */
.reply { display: grid; gap: 10px; padding: 18px; border: 1px solid var(--line); border-radius: 12px; background: var(--surface); }
.state { margin: 0; font-size: .9375rem; }
.state[data-kind="on"] { color: var(--text); }
.state[data-kind="off"], .state[data-kind="error"] { color: var(--trash); }
.reply textarea {
  width: 100%; min-height: 5.5rem; resize: vertical; font-family: var(--mono); font-size: .8125rem;
  color: var(--text); background: var(--surface-2); border: 1px solid var(--line); border-radius: 8px; padding: 10px;
}

/* What changed */
.changes { display: grid; gap: 10px; }
.changes details { border-top: 1px solid var(--line); padding-top: 10px; }
.changes summary { cursor: pointer; font-weight: 500; }
.changes summary .mono { color: var(--muted); font-weight: 400; margin-left: 6px; }
.clist { list-style: none; margin: 10px 0 4px; padding: 0; display: grid; gap: 10px; }
.clist li { display: grid; gap: 2px; font-size: .875rem; }
.clist .p { font-weight: 500; }
.clist .d { color: var(--muted); overflow-wrap: anywhere; }
.clist .d .mono { color: var(--text); }
s { color: var(--muted); }
.undo { font-size: .8125rem; color: var(--muted); max-width: 62ch; margin: 0; }

/* Bottom bar */
.bar {
  position: fixed; left: 0; right: 0; bottom: 0; z-index: 5;
  background: var(--surface); border-top: 1px solid var(--line-strong);
  padding-inline: 16px; padding-block: 10px calc(10px + env(safe-area-inset-bottom));
}
.bar-in { max-width: 46rem; margin-inline: auto; display: flex; flex-wrap: wrap; gap: 4px 18px; align-items: center; justify-content: space-between; font-size: .875rem; }
.counts { display: flex; gap: 14px; font-variant-numeric: tabular-nums; }
.counts .t { color: var(--trash); }
.counts b { font-family: var(--mono); font-weight: 500; }
.bar .state { font-size: .8125rem; color: var(--muted); }

@media (max-width: 560px) {
  .item-head { grid-template-columns: 2rem 1fr; }
  .choice { grid-column: 2; }
  .avail, details.why { margin-left: calc(2rem + 10px); }
  .toolbar { align-items: stretch; }
}
@media (prefers-reduced-motion: no-preference) {
  .item { transition: background-color .15s ease; }
  .choice button, .seg button { transition: background-color .12s ease, color .12s ease; }
}
</style>

<div class="wrap">
  <header class="mast">
    <p class="kicker"><b>Vegan Moto Club</b> &middot; store link audit &middot; <span id="date"></span></p>
    <h1>Discontinued gear review</h1>
    <p class="lede" id="lede"></p>
    <dl class="tally" id="tally"></dl>
  </header>

  <section class="decide" aria-labelledby="decide-h">
    <div class="decide-head">
      <h2 id="decide-h">Trash or keep</h2>
      <p class="hint">Tap one choice per product. Tap it again to undo. Your choices save as you go; when you're done, tell Claude in the chat and the ones marked Trash move to Notion trash (restorable for 30 days). Products you keep lose their "View on Store" button unless you ask for a store link.</p>
    </div>
    <div class="toolbar">
      <div class="seg" role="group" aria-label="Show">
        <button type="button" id="f-all" data-f="all" aria-pressed="true">All<span class="mono" id="c-all"></span></button>
        <button type="button" id="f-nobody" data-f="nobody" aria-pressed="false">Nobody sells it<span class="mono" id="c-nobody"></span></button>
        <button type="button" id="f-sold" data-f="sold" aria-pressed="false">Listed somewhere<span class="mono" id="c-sold"></span></button>
      </div>
      <button type="button" class="bulk" id="bulk">Mark every "nobody sells it" as Trash</button>
    </div>
    <div id="list"></div>
  </section>

  <section class="reply" aria-labelledby="reply-h">
    <h2 id="reply-h">Your answer</h2>
    <p class="state" id="state" data-kind="pending">Connecting&hellip;</p>
    <label for="reply-text" class="hint">If saving isn't available, copy this into the chat instead:</label>
    <textarea id="reply-text" readonly></textarea>
  </section>

  <section class="changes" aria-labelledby="changes-h">
    <h2 id="changes-h">What changed in Notion overnight</h2>
    <details id="d-fixed"><summary>Links fixed<span class="mono" id="n-fixed"></span></summary><ul class="clist" id="l-fixed"></ul></details>
    <details id="d-cleared"><summary>Unsafe links cleared<span class="mono" id="n-cleared"></span></summary><ul class="clist" id="l-cleared"></ul></details>
    <details id="d-prices"><summary>Prices corrected<span class="mono" id="n-prices"></span></summary><ul class="clist" id="l-prices"></ul></details>
    <details id="d-review" open><summary>Left for a human look<span class="mono" id="n-review"></span></summary><ul class="clist" id="l-review"></ul></details>
    <p class="undo" id="undo"></p>
  </section>
</div>

<div class="bar" role="status">
  <div class="bar-in">
    <div class="counts"><span class="t">Trash <b id="b-trash">0</b></span><span>Keep <b id="b-keep">0</b></span><span>To decide <b id="b-left">0</b></span></div>
    <span class="state" id="bar-state"></span>
  </div>
</div>

<script type="application/json" id="data">__DATA__</script>
<script>
(function () {
  const D = JSON.parse(document.getElementById("data").textContent);
  const KEY = "vmc-discontinued-choices";
  const byId = {};
  D.items.forEach(it => { byId[it.id] = it; });
  let choices = {};
  try { choices = JSON.parse(localStorage.getItem(KEY) || "{}") || {}; } catch (e) { choices = {}; }
  let filter = "all";
  let docRef = null;
  let saveTimer = null;
  let dbKind = "pending";

  const esc = s => String(s == null ? "" : s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const money = v => { const n = Number(v); return isFinite(n) ? "$" + (Number.isInteger(n) ? n.toLocaleString("en-US") : n.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })) : ""; };
  const $ = id => document.getElementById(id);

  // Masthead
  $("date").textContent = D.date;
  $("lede").innerHTML = "Overnight, every “View on Store” link in the catalog was opened and checked against its Notion row. " +
    "<strong>" + D.items.length + " products are no longer sold by their maker.</strong> " +
    D.nobody + " of them can’t be bought anywhere; the rest are only left as old stock at a few shops.";
  $("tally").innerHTML = [
    ["Products checked", D.checked], ["Links fixed", D.fixed], ["Unsafe links cleared", D.cleared], ["Prices corrected", D.prices]
  ].map(([k, v]) => "<div><dt>" + esc(k) + "</dt><dd>" + v + "</dd></div>").join("");
  $("c-all").textContent = D.items.length;
  $("c-nobody").textContent = D.nobody;
  $("c-sold").textContent = D.items.length - D.nobody;
  $("bulk").textContent = "Mark all " + D.nobody + " “nobody sells it” as Trash";

  // Decision list, grouped by brand in report order
  function rowHTML(it) {
    const meta = [money(it.price) ? '<span class="mono">' + money(it.price) + "</span>" : "", esc(it.category), esc(it.gender), esc(it.vegan)].filter(Boolean).join(" &middot; ");
    const inStock = it.still.filter(s => !s.oos).length;
    const plural = n => n + (n === 1 ? " store" : " stores");
    const avail = !it.still.length ? '<span class="chip">Nobody sells it</span>'
      : inStock ? '<span class="chip sold">Still sold at ' + plural(inStock) + "</span>"
      : '<span class="chip">Listed at ' + plural(it.still.length) + ", out of stock</span>";
    const linkNote = it.link.startsWith("cleared") ? '<span class="note">Link already cleared: the store’s domain now shows an unrelated site</span>' : "";
    const stores = it.still.map(s => "<li>" + (s.url
      ? '<a class="mono" href="' + esc(s.url) + '" target="_blank" rel="noopener noreferrer">' + esc(s.host) + "</a>" + (s.note ? ' <span class="note">(' + esc(s.note) + ")</span>" : "")
      : esc(s.note)) + "</li>").join("");
    const succ = it.successor
      ? "<p><b>Newer model:</b> " + (it.successor.url ? '<a href="' + esc(it.successor.url) + '" target="_blank" rel="noopener noreferrer">' + esc(it.successor.name || it.successor.url) + "</a>" : esc(it.successor.name)) + ' <span class="note">(vegan status not checked; it’s a different product)</span></p>'
      : "";
    return '<article class="item" data-id="' + esc(it.id) + '" data-avail="' + (it.still.length ? "sold" : "nobody") + '">' +
      '<div class="item-head"><span class="num">#' + it.n + "</span>" +
      '<div class="title"><h3>' + esc(it.name) + '</h3><p class="meta">' + meta + "</p></div>" +
      '<div class="choice" role="group" aria-label="' + esc(it.name) + '">' +
      '<button type="button" data-v="trash" aria-pressed="false">Trash</button>' +
      '<button type="button" data-v="keep" aria-pressed="false">Keep</button></div></div>' +
      '<p class="avail">' + avail + linkNote + "</p>" +
      '<details class="why"><summary>Why it’s on the list</summary><div class="why-body">' +
      "<p>" + esc(it.evidence) + "</p>" +
      (stores ? "<div><b>Still sold at</b><ul class=\"stores\">" + stores + "</ul></div>" : "") + succ +
      '<p class="note">Old link: <span class="mono">' + esc(it.url_host || "none") + "</span> &middot; " +
      '<a href="' + esc(it.notion) + '" target="_blank" rel="noopener noreferrer">Open in Notion</a></p>' +
      "</div></details></article>";
  }
  const groups = [];
  D.items.forEach(it => {
    let g = groups[groups.length - 1];
    if (!g || g.brand !== it.brand) { g = { brand: it.brand, items: [] }; groups.push(g); }
    g.items.push(it);
  });
  $("list").innerHTML = groups.map(g =>
    '<section class="brand" data-brand="' + esc(g.brand) + '"><h3 class="brand-name">' + esc(g.brand) +
    ' <span class="mono">' + g.items.length + "</span></h3>" + g.items.map(rowHTML).join("") + "</section>").join("");

  function paint() {
    let t = 0, k = 0;
    document.querySelectorAll(".item").forEach(el => {
      const c = choices[el.dataset.id] || "";
      if (c === "trash") t++; else if (c === "keep") k++;
      el.dataset.state = c;
      el.querySelectorAll(".choice button").forEach(b => b.setAttribute("aria-pressed", String(b.dataset.v === c)));
      el.classList.toggle("hidden", filter !== "all" && el.dataset.avail !== filter);
    });
    document.querySelectorAll(".brand").forEach(sec => {
      sec.classList.toggle("hidden", !sec.querySelector(".item:not(.hidden)"));
    });
    $("b-trash").textContent = t;
    $("b-keep").textContent = k;
    $("b-left").textContent = D.items.length - t - k;
    const nums = v => D.items.filter(it => choices[it.id] === v).map(it => "#" + it.n).join(", ");
    $("reply-text").value = "Trash: " + (nums("trash") || "none") + "\nKeep: " + (nums("keep") || "none") +
      "\nUndecided: " + (D.items.length - t - k);
  }

  function showState(kind, text, short) {
    dbKind = kind;
    $("state").dataset.kind = kind;
    $("state").textContent = text;
    $("bar-state").textContent = short;
  }

  function clean() {
    const out = {};
    Object.keys(choices).forEach(id => { if (byId[id] && (choices[id] === "trash" || choices[id] === "keep")) out[id] = choices[id]; });
    return out;
  }

  function persist() {
    try { localStorage.setItem(KEY, JSON.stringify(clean())); } catch (e) {}
    if (!docRef) return;
    showState("on", "Saving…", "Saving…");
    clearTimeout(saveTimer);
    saveTimer = setTimeout(save, 700);
  }

  async function save(retried) {
    try {
      await docRef.set({ choices: clean(), updated_at: new Date().toISOString() });
      showState("on", "Saved for Claude. When you're done, say so in the chat.", "Saved");
    } catch (e) {
      const code = e && e.code;
      if (code === "unavailable" && !retried) { setTimeout(() => save(true), 800 + Math.random() * 800); return; }
      showState("error", "Couldn't save (" + (code || "error") + "). Your choices are kept on this device; copy the answer below into the chat.", "Not saved");
    }
  }

  $("list").addEventListener("click", ev => {
    const b = ev.target.closest(".choice button");
    if (!b) return;
    const id = b.closest(".item").dataset.id;
    if (choices[id] === b.dataset.v) delete choices[id]; else choices[id] = b.dataset.v;
    paint();
    persist();
  });
  document.querySelectorAll(".seg button").forEach(b => b.addEventListener("click", () => {
    filter = b.dataset.f;
    document.querySelectorAll(".seg button").forEach(x => x.setAttribute("aria-pressed", String(x === b)));
    paint();
  }));
  $("bulk").addEventListener("click", () => {
    D.items.forEach(it => { if (!it.still.length && !choices[it.id]) choices[it.id] = "trash"; });
    paint();
    persist();
  });

  // What changed
  const li = (p, d) => '<li><span class="p">' + esc(p) + '</span><span class="d">' + d + "</span></li>";
  $("n-fixed").textContent = D.fixedLinks.length;
  $("l-fixed").innerHTML = D.fixedLinks.map(f => li(f.product,
    '<s class="mono">' + esc(f.before_host) + '</s> → <a class="mono" href="' + esc(f.after) + '" target="_blank" rel="noopener noreferrer">' + esc(f.after_host) + "</a>")).join("");
  $("n-cleared").textContent = D.clearedLinks.length;
  $("l-cleared").innerHTML = D.clearedLinks.map(c => li(c.product, '<span class="mono">' + esc(c.before_host) + "</span> &middot; " + esc(c.reason))).join("");
  $("n-prices").textContent = D.priceChanges.length;
  $("l-prices").innerHTML = D.priceChanges.map(p => li(p.product,
    '<span class="mono">' + money(p.before) + " → " + money(p.after) + "</span> &middot; " + esc(p.reason))).join("");
  $("n-review").textContent = D.review.length;
  $("l-review").innerHTML = D.review.map(r => li(r.product + (r.brand ? " (" + r.brand + ")" : ""), esc(r.note))).join("");
  $("undo").textContent = "Every change is recorded in " + (D.changelog || "the run's changelog") +
    ". Claude can put every link and price back to its pre-audit value in one step if anything looks wrong.";

  paint();
  showState("pending", "Connecting…", "");

  // Saved choices live in the artifact database so Claude can read them back.
  (async function connect() {
    const db = window.claude && window.claude.use ? await window.claude.use("db") : null;
    if (!db) {
      showState("off", "Saving isn't available in this view. Copy the answer below into the chat when you're done.", "Not saved");
      return;
    }
    docRef = db.doc("review/discontinued");
    showState("on", "Connected. Choices save as you go.", "Saved");
    docRef.onSnapshot(snap => {
      if (snap.metadata && snap.metadata.hasPendingWrites) return;
      if (snap.exists) {
        const remote = (snap.data() || {}).choices || {};
        if (JSON.stringify(remote) !== JSON.stringify(clean())) {
          choices = Object.assign({}, remote);
          try { localStorage.setItem(KEY, JSON.stringify(choices)); } catch (e) {}
          paint();
        }
      } else if (Object.keys(clean()).length) {
        save();
      }
    }, err => {
      showState("error", "Lost the connection to saving (" + ((err && err.code) || "error") + "). Copy the answer below into the chat.", "Not saved");
    });
  })();
})();
</script>
"""

if __name__ == "__main__":
    main()
