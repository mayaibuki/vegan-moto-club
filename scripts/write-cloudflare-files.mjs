// Runs after `next build`. Writes the Cloudflare Pages config files into out/:
//   _redirects  old product URLs -> category pages (from lib/removed-products.json),
//               the job next.config.js redirects() did on Vercel
//   _headers    long browser/CDN caching for hashed photo files
// Usage: node scripts/write-cloudflare-files.mjs
import { readFileSync, writeFileSync, existsSync } from "node:fs"

if (!existsSync("out")) {
  console.error("out/ is missing: run `next build` first.")
  process.exit(1)
}

const removed = JSON.parse(readFileSync("lib/removed-products.json", "utf8"))
const redirects = Object.entries(removed).map(([slug, dest]) => `/products/${slug} ${dest} 301`)
writeFileSync("out/_redirects", redirects.join("\n") + "\n")

// Photo names change whenever the photo does (see scripts/notion-snapshot.mjs), so they never go stale.
writeFileSync(
  "out/_headers",
  ["/photos/*", "  Cache-Control: public, max-age=31536000, immutable", ""].join("\n")
)

console.log(`[cloudflare] wrote ${redirects.length} redirects and _headers`)
