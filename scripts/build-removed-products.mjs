#!/usr/bin/env node
/**
 * Builds lib/removed-products.json: slug -> destination path for products
 * that were moved to Notion trash on 2026-09-14 (store link audit), so their
 * old /products/<slug> URLs 308-redirect to the matching category page instead
 * of returning 404. next.config.js reads the JSON in redirects().
 *
 * Inputs (committed in the audit run folder):
 *   Scheduled audit/link_check/runs/2026-09-13/trash_ids.json
 *   Scheduled audit/link_check/runs/2026-09-13/trash_louise.json
 *   Scheduled audit/link_check/runs/2026-09-13/discontinued.json  (page_id, name, category[])
 *   Scheduled audit/link_check/runs/2026-09-13/snapshot.json      (live catalog at the time, for collision checks)
 *
 * Caveat: if a trashed product is restored in Notion, remove its slug from the
 * JSON (or re-run after deleting the id from the input), otherwise the redirect
 * shadows the restored page.
 *
 * Usage: node scripts/build-removed-products.mjs
 */
import { readFileSync, writeFileSync } from "node:fs"
import { resolve } from "node:path"

const RUN = resolve("Scheduled audit/link_check/runs/2026-09-13")
const read = (f) => JSON.parse(readFileSync(resolve(RUN, f), "utf8"))

// Copy of generateSlug in lib/utils.ts (that module imports TS types, so it is
// not importable from a plain Node script). Keep the two in sync.
function generateSlug(name) {
  return name
    .toLowerCase()
    .trim()
    .replace(/[^\w\s-]/g, "")
    .replace(/\s+/g, "-")
    .replace(/-+/g, "-")
    .replace(/^-+|-+$/g, "")
}
if (generateSlug("REV'IT! Storm 2 WB") !== "revit-storm-2-wb") throw new Error("generateSlug drifted from lib/utils.ts")

// Category name -> category page slug (mirror of CATEGORY_PAGES in lib/constants.ts)
const CATEGORY_SLUGS = {
  Gloves: "/vegan-motorcycle-gloves",
  Jackets: "/vegan-motorcycle-jackets",
  Boots: "/vegan-motorcycle-boots",
  Pants: "/vegan-motorcycle-pants",
  "Racing Suits": "/vegan-motorcycle-racing-suits",
  Protection: "/vegan-motorcycle-protection",
  "Street wear": "/vegan-motorcycle-street-wear",
}

const trashedIds = new Set([...read("trash_ids.json"), ...read("trash_louise.json")])
const byId = new Map(read("discontinued.json").map((r) => [r.page_id, r]))
const liveNames = new Map(read("snapshot.json").filter((r) => !trashedIds.has(r.page_id)).map((r) => [generateSlug(r.name), r.name]))

const out = {}
for (const id of trashedIds) {
  const rec = byId.get(id)
  if (!rec) throw new Error(`trashed id ${id} not in discontinued.json`)
  const slug = generateSlug(rec.name)
  if (liveNames.has(slug)) throw new Error(`slug ${slug} collides with live product "${liveNames.get(slug)}"`)
  const cat = (rec.category || []).find((c) => CATEGORY_SLUGS[c])
  out[slug] = cat ? CATEGORY_SLUGS[cat] : "/products"
}
const sorted = Object.fromEntries(Object.entries(out).sort(([a], [b]) => a.localeCompare(b)))
writeFileSync(resolve("lib/removed-products.json"), JSON.stringify(sorted, null, 2) + "\n")
console.log(`${Object.keys(sorted).length} redirects written to lib/removed-products.json`)
for (const [slug, dest] of Object.entries(sorted)) console.log(`${slug} -> ${dest}`)
