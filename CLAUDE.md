# Vegan Moto Club

## Overview

A curated database of vegan motorcycle gear. Next.js 14 site pulling product, event, and blog data from Notion databases via the Notion API, built as a static export and hosted on Cloudflare Pages (moved off Vercel in Nov 2026, see `docs/cloudflare-pages.md`).

- **Live URL**: https://www.veganmotoclub.com (apex 308-redirects to www)
- **GitHub**: https://github.com/mayaibuki/vegan-moto-club
- **Cloudflare Pages**: `.github/workflows/deploy-cloudflare.yml` deploys on push to `main`, on Notion webhook, and hourly when Notion data changed. The Vercel project is kept only as a fallback.

## Commands

```bash
npm run dev         # Local dev server (port 3000), live Notion data
npm run build       # Notion snapshot + photo resize + static export to out/
npm run preview:cf  # Serve out/ and functions/ like Cloudflare does
```

## Architecture

```
app/               Server components (pages, layouts)
  products/        Product listing + [id] detail pages
  events/          Events listing
  blog/            "Guides and FAQ" hub: Notion FAQ rows grouped by category + posts + [id] detail
  guides/          Static explainer guides from `lib/guides.ts` (index + [slug])
  about/           Static about page
components/        React components
  ui/              shadcn/ui primitives (Button, Card, Badge, etc.)
  ProductGrid.tsx  Client component — filters, search, pagination
  ProductCard.tsx  Memoized product card (React.memo)
  Navbar.tsx       Client component — theme toggle, mobile menu
  Footer.tsx       Server component — nav, social links
  Logo.tsx         Logo with size variants
lib/
  notion.ts        Notion API client, typed interfaces, cached fetchers
  utils.ts         cn(), formatPrice(), formatDate(), filterProducts()
docs/brand-voice.md   Voice rules for product copy (used by .claude/agents/gear-writer and marketing:brand-review)
docs/category-rules.md  Which Notion Category a product gets (Jackets, Pants, Protection, Other, ...)
.claude/agents/       gear-researcher, gear-writer, gear-verifier subagents for the enrichment task
```

**Patterns:** Server-first — only `ProductGrid` and `Navbar` are client components. Static export only: no API routes, middleware, ISR or image optimizer in `app/`. Production builds read `.notion-snapshot/` written by `scripts/notion-snapshot.mjs`, which also writes resized photos to `public/photos/` (use `notionImageUrl()` for sizes). Server code lives in `functions/api/` (Cloudflare Pages Functions: fetch and Web Crypto only, helpers in `lib/cloudflare/shared.ts`). Typed via `NotionPage`, `NotionRichText`, `NotionFile` interfaces in `lib/notion.ts`. Theme: Stone base + Lime accent, dark mode via `.dark` on `<html>`.

## Environment Variables

```
NOTION_API_KEY          # Notion integration token
NOTION_PRODUCTS_DB_ID   # Products database ID
NOTION_EVENTS_DB_ID     # Events database ID
NOTION_BLOG_DB_ID       # Blog database ID
NEXT_PUBLIC_SITE_URL    # Canonical origin (https://www.veganmotoclub.com); code falls back to the same
```

## Design System

### Rules

The rules live in `AGENTS.md` so every coding agent reads the same ones: reuse existing components before building, spec first for anything new, tokens only, run the audit. Read them before writing UI code.

@AGENTS.md

### Token Layers

- **Layer 1 — Primitives** (`--ds-*`): Raw values in `app/tokens.css` under `:root`
- **Layer 2 — Semantic** (`--color-*` etc.): Aliases in `app/tokens.css`, light + `.dark` variants
- **Layer 3 — Components**: Tailwind classes (`bg-card`, `text-destructive`, `text-success`) — preferred over raw `var()`
- shadcn/ui bridge variables (`--background`, `--foreground`, etc.) live in `app/globals.css`

### Specs

See `specs/` — `foundations/` (color, spacing, typography, radius, elevation, motion), `tokens/token-reference.md`, `components/` (one file per component).

## Remaining TODOs

- [ ] Add donations section (Venmo / PayPal.me link — no complex checkout)
- [ ] Newsletter (Buttondown) hooked to the new `/feed.xml` RSS feed
- [ ] Move user suggestions out of the products DB (own DB or Status property; currently filtered out by name prefix in `lib/notion.ts`)
- [ ] Configure ESLint (not yet set up — `npm run lint` prompts for config)
- [ ] Discord → Notion event sync (GitHub Action polling Discord API)
- [ ] Webflow portfolio case study (mayaibuki.com)
- [ ] Project folder cleanup

## Shipped TODOs

- [x] Moved to Cloudflare Pages as a static export after Vercel Hobby paused the account for Active CPU (2026-11-17); photos pre-resized at build, forms and webhook as Pages Functions

- [x] FAQ sections fed by the Notion Blog DB (`Type`/`Category` selects, `getFaqs()`, `components/FaqSection.tsx`, one FAQPage block per page), CE standards in category intros and `/verification`, three guides under `/guides`
- [x] Canonical host is www: `NEXT_PUBLIC_SITE_URL` set in Vercel, code fallback matches, apex redirects 308; shared `components/JsonLd.tsx` escapes JSON-LD
- [x] Product enrichment second pass: daily Claude Code scheduled task `vmc-product-enrichment` + `.claude/agents/gear-*` + `docs/brand-voice.md` (see `Scheduled audit/README.md`)
- [x] Monthly SEO/GEO audit: read-only Claude Code scheduled task `vmc-seo-audit`, report in `Scheduled audit/audit/` (see `Scheduled audit/README.md`)
- [x] Favicon + app icons
- [x] Vercel Analytics (replaced by Cloudflare Web Analytics, Nov 2026)
- [x] Speed Insights
- [x] Image cost optimization (AVIF, ISR, notion-image proxy)
- [x] UTC-safe event date formatting
- [x] Human-readable product slugs
- [x] Native suggestion forms (product + event)
- [x] Design system tokenization + audit script
- [x] Event card redesign (Figma spec)
- [x] Color contrast fix (light-mode muted-foreground now WCAG AA, stone-600 primitive)
- [x] Notion fetch resilience (retries, no caching of failures — fixes empty-catalog outages)
- [x] Edge-cache image proxy responses (s-maxage — sharp runs once per image, not per visitor)
- [x] Server-rendered product grid + price/protection/season/waterproof filters, sort, search synonyms
- [x] Branded 404 + root error boundary
- [x] Static category landing pages (`app/[category]/page.tsx`, config in `lib/constants.ts` CATEGORY_PAGES)
- [x] "How we verify" page (`/verification`), product badges link to it
- [x] RSS feed of newly added products (`/feed.xml`)
- [x] OG image (`/public/og-image.png`, generator script pattern: sharp + SVG)
- [x] Store link + price audit pipeline (`Scheduled audit/link_check/`, see its README)
- [x] Grain gradient shader page background (`components/ShaderBackground.tsx`, Paper Shaders, colours from `--background` + `--primary`)
- [x] Retired the webhook-triggered Python product audit (2026-11-14); the daily `vmc-product-enrichment` task is the only enrichment pass, the Notion webhook only refreshes the site cache

<!-- claude-reflect: learned rules (saved from the band; edit freely) -->
## Learned rules
- Rate Level of Protection: level 1 armor is moderately protective; level 2 armor or AA is mostly protected; AAA or level 2 racing gear is most protective.
- Treat all Anderson Mountain Bags products as confirmed vegan by maker, since the brand and its owner are vegan.
<!-- end claude-reflect -->
