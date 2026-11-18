// Runs before `next build`. Pulls the products, events and blog databases from
// Notion once, saves them to .notion-snapshot/, and turns every photo into
// pre-resized WebP files in public/photos/.
//
// Why: the site is a static export (Cloudflare Pages). Nothing may run per
// visitor, so photos cannot be resized on request the way the old
// /api/notion-image route did; that route is what used up Vercel's CPU quota.
// Notion-hosted file URLs also expire after an hour, so the build keeps its own
// copies under stable names.
//
// Photo files are named by a hash of the source URL (without Notion's signing
// query), so an unchanged photo keeps its name across builds and is skipped,
// and a replaced photo gets a new name. Keep public/photos/ between builds
// (the GitHub Action caches it) and only new photos are downloaded.
//
// Usage: node scripts/notion-snapshot.mjs
// Needs NOTION_API_KEY, NOTION_PRODUCTS_DB_ID, NOTION_EVENTS_DB_ID, NOTION_BLOG_DB_ID
// (read from .env.local when present).

import { Client } from "@notionhq/client"
import sharp from "sharp"
import crypto from "node:crypto"
import fs from "node:fs"
import path from "node:path"

try {
  process.loadEnvFile(".env.local")
} catch {
  /* CI passes env vars directly */
}

const SNAPSHOT_DIR = ".notion-snapshot"
const PHOTO_DIR = path.join("public", "photos")
// Must match notionImageUrl() in lib/utils.ts. The full-size file doubles as
// the 1200px variant (and the social/structured-data image), which keeps a
// deploy at 3 files per photo, well under Cloudflare's 20,000-file limit.
const WIDTHS = [256, 600]
const FULL_WIDTH = 1200
const CONCURRENCY = 6

const DATABASES = [
  { name: "products", id: process.env.NOTION_PRODUCTS_DB_ID, fileProps: ["Photos"] },
  { name: "events", id: process.env.NOTION_EVENTS_DB_ID, fileProps: ["Event poster"] },
  { name: "blog", id: process.env.NOTION_BLOG_DB_ID, fileProps: ["Thumbnail Image"] },
]

if (!process.env.NOTION_API_KEY || DATABASES.some((db) => !db.id)) {
  console.error("Missing NOTION_API_KEY or one of the NOTION_*_DB_ID variables.")
  process.exit(1)
}

const notion = new Client({ auth: process.env.NOTION_API_KEY })
const bareId = (id) => id.replace(/-/g, "").toLowerCase()
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms))

async function withRetry(fn, attempts = 5) {
  let lastError
  for (let attempt = 0; attempt < attempts; attempt++) {
    try {
      return await fn()
    } catch (error) {
      lastError = error
      const retryAfter = Number(error?.headers?.get?.("retry-after"))
      const wait = Number.isFinite(retryAfter) && retryAfter > 0 ? retryAfter * 1000 : 1000 * 2 ** attempt
      if (attempt < attempts - 1) await sleep(Math.min(wait, 30000) + Math.random() * 500)
    }
  }
  throw lastError
}

async function queryAll(databaseId) {
  const pages = []
  let cursor
  do {
    const res = await withRetry(() =>
      notion.databases.query({ database_id: databaseId, start_cursor: cursor, page_size: 100 })
    )
    pages.push(...res.results)
    cursor = res.has_more ? res.next_cursor : undefined
  } while (cursor)
  return pages.filter((page) => !page.archived && !page.in_trash)
}

/** Stable identity for a file: Notion's signed URLs change every hour, their path does not. */
function sourceKey(file) {
  if (file.type === "file" && file.file?.url) {
    const u = new URL(file.file.url)
    return { url: file.file.url, stable: `${u.host}${u.pathname}` }
  }
  if (file.type === "external" && file.external?.url) {
    return { url: file.external.url, stable: file.external.url }
  }
  return null
}

const variantPath = (hash, width) => path.join(PHOTO_DIR, width ? `${hash}-w${width}.webp` : `${hash}.webp`)
const allVariants = (hash) => [variantPath(hash), ...WIDTHS.map((w) => variantPath(hash, w))]

async function writeAtomic(file, buffer) {
  const tmp = `${file}.${process.pid}.tmp`
  await fs.promises.writeFile(tmp, buffer)
  await fs.promises.rename(tmp, file)
}

async function processPhoto(hash, url) {
  if (allVariants(hash).every((f) => fs.existsSync(f))) return "cached"
  const res = await fetch(url, {
    headers: { "User-Agent": "Mozilla/5.0 (compatible; VeganMotoClubBuild/1.0)", Accept: "image/*" },
    signal: AbortSignal.timeout(30000),
  })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  const input = Buffer.from(await res.arrayBuffer())
  const encode = (width) =>
    sharp(input).rotate().resize({ width, withoutEnlargement: true }).webp({ quality: 80, effort: 4 }).toBuffer()
  await writeAtomic(variantPath(hash), await encode(FULL_WIDTH))
  for (const width of WIDTHS) await writeAtomic(variantPath(hash, width), await encode(width))
  return "new"
}

async function runPool(items, worker) {
  let next = 0
  await Promise.all(
    Array.from({ length: CONCURRENCY }, async () => {
      while (next < items.length) await worker(items[next++])
    })
  )
}

async function main() {
  fs.mkdirSync(SNAPSHOT_DIR, { recursive: true })
  fs.mkdirSync(PHOTO_DIR, { recursive: true })

  // key "<pageId>:<prop>:<idx>" -> { hash, url, external }
  const photos = new Map()

  for (const db of DATABASES) {
    const pages = await queryAll(db.id)
    fs.writeFileSync(path.join(SNAPSHOT_DIR, `${bareId(db.id)}.json`), JSON.stringify(pages))
    for (const page of pages) {
      for (const prop of db.fileProps) {
        const files = page.properties?.[prop]?.files ?? []
        files.forEach((file, idx) => {
          const src = sourceKey(file)
          if (!src) return
          const hash = crypto.createHash("sha1").update(src.stable).digest("hex").slice(0, 16)
          photos.set(`${page.id}:${prop}:${idx}`, { hash, url: src.url, external: file.type === "external" })
        })
      }
    }
    console.log(`[snapshot] ${db.name}: ${pages.length} pages`)
  }

  const unique = new Map()
  for (const p of photos.values()) if (!unique.has(p.hash)) unique.set(p.hash, p.url)

  const failed = new Set()
  const counts = { cached: 0, new: 0, failed: 0 }
  await runPool([...unique.entries()], async ([hash, url]) => {
    try {
      counts[await processPhoto(hash, url)]++
    } catch (error) {
      failed.add(hash)
      counts.failed++
      console.warn(`[snapshot] photo failed (${error.message}): ${url.split("?")[0]}`)
    }
  })
  console.log(`[snapshot] photos: ${counts.new} new, ${counts.cached} cached, ${counts.failed} failed`)

  // Pages read this map at build time. A missing key means "no local copy": the
  // site then shows an external photo from its source URL, or skips a Notion one.
  const manifest = {}
  for (const [key, p] of photos) if (!failed.has(p.hash)) manifest[key] = `/photos/${p.hash}.webp`
  fs.writeFileSync(path.join(SNAPSHOT_DIR, "photos.json"), JSON.stringify(manifest))

  // Drop photos nothing points at any more, so the cache does not grow forever.
  const keep = new Set([...unique.keys()].flatMap((h) => allVariants(h).map((f) => path.basename(f))))
  let pruned = 0
  for (const name of fs.readdirSync(PHOTO_DIR)) {
    if (!keep.has(name)) {
      fs.rmSync(path.join(PHOTO_DIR, name))
      pruned++
    }
  }
  if (pruned) console.log(`[snapshot] pruned ${pruned} unused photo files`)
}

main().catch((error) => {
  console.error("[snapshot] failed:", error)
  process.exit(1)
})
