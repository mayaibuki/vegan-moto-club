# Vegan Moto Club

## Overview

A curated database of vegan motorcycle gear. Next.js 14 site pulling product, event, and blog data from Notion databases via the Notion API, deployed on Vercel.

- **Live URL**: https://vegan-moto-club.vercel.app
- **GitHub**: https://github.com/mayaibuki/vegan-moto-club
- **Vercel**: Auto-deploys on push to `main`

## Commands

```bash
npm run dev      # Local dev server (port 3000)
npm run build    # Production build (229 pages)
npm run start    # Serve production build
```

## Architecture

```
app/               Server components (pages, layouts)
  products/        Product listing + [id] detail pages
  events/          Events listing
  blog/            Blog listing + [id] detail pages
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
```

### Data Flow

1. Notion databases (Products, Events, Blog) are queried via `@notionhq/client`
2. Results are cached with `unstable_cache` (1hr production, 1min dev)
3. Server components fetch data at build time (ISR with revalidation)
4. `ProductGrid` is the only client component doing filtering/pagination

### Key Patterns

- **Server-first**: All pages are server components except `ProductGrid`, `Navbar`
- **Typed Notion responses**: Custom `NotionPage`, `NotionRichText`, `NotionFile` interfaces in `lib/notion.ts`
- **shadcn/ui + Radix**: Accessible primitives with Tailwind styling
- **Theme**: Stone base + Lime accent, light/dark toggle via `.dark` class on `<html>`

## Environment Variables

```
NOTION_API_KEY          # Notion integration token
NOTION_PRODUCTS_DB_ID   # Products database ID
NOTION_EVENTS_DB_ID     # Events database ID
NOTION_BLOG_DB_ID       # Blog database ID
NEXT_PUBLIC_SITE_URL    # Production URL (https://veganmotoclub.com)
```

## Audit Log

### February 8, 2026 — Performance, Accessibility, SEO, Code Quality Audit

**Performance:**
- Wrapped `ProductCard` in `React.memo` to prevent unnecessary re-renders
- Extracted static `seasonEmojis` object outside component body
- Added `useCallback` to Navbar `toggleTheme` function
- Added pagination to blog post fetching (was limited to 100 posts)

**Accessibility:**
- Events page: Added `aria-label` with "(opens in new tab)" on external links
- Events page: Wrapped decorative emojis in `<span aria-hidden="true">`
- Product detail: Changed 6 misused `<h2>` metadata labels to `<p>` (fixed heading hierarchy)
- Product detail: Changed `<div role="img">` to semantic `<figure>`
- Blog listing: Added `aria-label` on post links for screen readers
- Navbar: Added focus management — mobile menu focuses first link on open, returns focus to toggle on close

**SEO:**
- Fixed JSON-LD currency from `EUR` to `USD` on product detail pages
- Fixed sitemap static page timestamps (was regenerating every build)
- Added `Event` structured data (JSON-LD) to events page
- Added `ItemList` structured data (JSON-LD) to blog listing page
- Updated Footer social links to actual URLs (Discord, Instagram)
- Updated Organization schema `sameAs` with social profiles
- Updated copyright year to 2026

**Code Quality:**
- Replaced ~20 `any` types in `lib/notion.ts` with proper interfaces (`NotionPage`, `NotionRichText`, `NotionSelectOption`, `NotionFile`, `NotionPageProperties`)
- Added `Product` type to `filterProducts()` and `getUniqueBrands()` in `lib/utils.ts`
- Added `console.error` logging to all 5 silent catch blocks in `lib/notion.ts`
- Fixed `formatPrice()` to show decimals when present ($149.99) and hide when whole ($150)

**Visual regression:** 30 before/after screenshots captured at 3 breakpoints x 2 themes — no layout regressions.

## Design System

### Rules

1. **Read specs before writing UI code.** Before creating or modifying any component, read the relevant spec file in `specs/components/` and the foundation files in `specs/foundations/`. These define the anatomy, tokens, states, and accessibility requirements.
2. **Use only tokens from `tokens.css`.** Never use hardcoded color values (`text-red-600`, `bg-white`, `#hex`), arbitrary Tailwind values (`h-[30px]`, `z-[100]`, `rounded-[6px]`), or raw CSS pixel values. Map every visual value to a semantic token or standard Tailwind scale class.
3. **Run the token audit script before committing.** Execute `node scripts/token-audit.js` and confirm zero errors. The script scans `app/` and `components/` for hardcoded visual values and returns exit code 1 if violations are found.
4. **Zero errors required.** The audit must pass with 0 errors before any PR is merged.

### Token Architecture

```
Layer 1 — Primitives (--ds-*)     Raw values: --ds-stone-900, --ds-lime-400
Layer 2 — Semantic (--color-*)    Aliases:    --color-text, --color-accent
Layer 3 — Components              Consume Layer 2 via Tailwind classes or var()
```

- Primitives live in `app/tokens.css` under `:root`
- Semantic aliases live in `app/tokens.css` under `:root` (light) and `.dark` (dark)
- shadcn/ui bridge variables (e.g., `--background`, `--foreground`) live in `app/globals.css`
- Tailwind classes (`bg-card`, `text-destructive`, `text-success`) are the preferred interface

### Spec Directory

```
specs/
  foundations/    color.md, spacing.md, typography.md, radius.md, elevation.md, motion.md
  tokens/         token-reference.md  (master map of every CSS variable)
  components/     One file per component (button, card, badge, input, checkbox,
                  radio-group, select, navbar, footer, product-card, product-grid,
                  suggest-product-form, logo)
```

### Audit Script

```bash
node scripts/token-audit.js       # Scan for hardcoded values
                                   # Exit 0 = pass, Exit 1 = errors found
```

## Remaining TODOs

- [ ] Add donations section with PayPal integration (allow supporters to donate to the project)
- [ ] Manual color contrast check (muted-foreground on backgrounds — near WCAG AA threshold)
- [ ] Add `/public/favicon.ico` (currently 404)
- [ ] Add actual `/public/og-image.png` for OpenGraph previews
- [x] ~~Connect GoDaddy domain (`veganmotoclub.com`) to Vercel~~ **DONE** — DNS propagated, domain live
- [ ] Configure ESLint (not yet set up — `npm run lint` prompts for config)
