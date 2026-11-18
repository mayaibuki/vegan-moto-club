# Hosting on Cloudflare Pages

The site moved from Vercel to Cloudflare Pages in November 2026 after Vercel's free plan paused the account for using too much server CPU. It now ships as a static site, so visitors never start any server code; only the two suggestion forms and the Notion webhook run as small Pages Functions.

## How it works

1. `scripts/notion-snapshot.mjs` pulls the products, events and blog databases once and saves them to `.notion-snapshot/`. It downloads every photo and writes resized WebP files to `public/photos/` (`<hash>.webp` at 1200px, plus `-w256` and `-w600`). Unchanged photos are skipped.
2. `next build` (`output: 'export'`) renders every page to `out/` from the snapshot.
3. `scripts/write-cloudflare-files.mjs` adds `out/_redirects` (removed products) and `out/_headers` (photo caching).
4. `.github/workflows/deploy-cloudflare.yml` runs all of that and uploads `out/` plus `functions/` with Wrangler.

Data refreshes when:
- someone edits Notion by hand (the webhook starts the workflow; bot edits wait),
- every hour (the workflow checks Notion and deploys only if something changed),
- code is pushed to `main`.

## One-time setup

1. **Cloudflare account**: sign up at dash.cloudflare.com (free).
2. **Pages project**: Workers & Pages → Create → Pages → "Upload assets", name it `vegan-moto-club`, upload any file once. Or run `npx wrangler pages project create vegan-moto-club --production-branch main`.
3. **API token**: My Profile → API Tokens → Create token → "Custom": Account → Cloudflare Pages → Edit. Copy the Account ID from the Workers & Pages overview.
4. **GitHub secrets** (repo → Settings → Secrets and variables → Actions):
   `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`, `NOTION_API_KEY`, `NOTION_PRODUCTS_DB_ID`, `NOTION_EVENTS_DB_ID`, `NOTION_BLOG_DB_ID`.
   Optional variables: `CF_PAGES_PROJECT` (if the name differs), `CF_ANALYTICS_TOKEN` (Web Analytics, step 7).
5. **Function variables** (Pages project → Settings → Variables and Secrets, Production):
   `NOTION_API_KEY`, `NOTION_PRODUCTS_DB_ID`, `NOTION_EVENTS_DB_ID`, `NOTION_BLOG_DB_ID`, `NOTION_WEBHOOK_SECRET`, `GH_DISPATCH_TOKEN` (fine-grained GitHub token for this repo with Actions: read and write).
6. **Run the workflow once**: Actions → Deploy to Cloudflare Pages → Run workflow. The first run downloads every photo (about 10 minutes); later runs only fetch new ones. Check `https://vegan-moto-club.pages.dev`.
7. **Web Analytics** (optional): Cloudflare → Analytics & Logs → Web Analytics → add site → copy the token into the `CF_ANALYTICS_TOKEN` variable.
8. **Domain**: Pages project → Custom domains → add `www.veganmotoclub.com`. Easiest is to move the domain's nameservers from GoDaddy to Cloudflare (free; Cloudflare then handles the apex too). Add a Redirect Rule `veganmotoclub.com/*` → `https://www.veganmotoclub.com/$1` (301). If DNS stays at GoDaddy instead: CNAME `www` → `vegan-moto-club.pages.dev`, and use GoDaddy forwarding for the apex.
9. **Notion webhook**: point the existing subscription at `https://www.veganmotoclub.com/api/notion-webhook` (same secret).
10. **Vercel**: once the new site works, disconnect Git on the Vercel project (so pushes stop building there) and downgrade the team to Hobby before the next renewal.

## Local commands

```bash
npm run dev          # live Notion data, no snapshot
npm run build        # snapshot + static export into out/
npm run preview:cf   # serve out/ + functions/ the way Cloudflare does
```

## Free-tier limits to keep in mind

- 20,000 files per deploy. Photos use 3 files each (about 9,000 for ~3,000 photos today).
- 500 deploys a month. Hourly checks skip the deploy when nothing changed.
- Pages Functions: 100,000 requests a day, 10 ms CPU each. Static pages and photos do not count.
