# Vegan Moto Club

## Overview

A curated database of vegan motorcycle gear. Next.js 14 site pulling product, event, and blog data from Notion databases via the Notion API, deployed on Vercel.

- **Live URL**: https://veganmotoclub.com
- **GitHub**: https://github.com/mayaibuki/vegan-moto-club
- **Vercel**: Auto-deploys on push to `main`

## Commands

```bash
npm run dev      # Local dev server (port 3000)
npm run build    # Production build
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

**Patterns:** Server-first — only `ProductGrid` and `Navbar` are client components. Notion data cached via `unstable_cache` (1hr prod, 1min dev), fetched at build time with ISR. Typed via `NotionPage`, `NotionRichText`, `NotionFile` interfaces in `lib/notion.ts`. Theme: Stone base + Lime accent, dark mode via `.dark` on `<html>`.

## Environment Variables

```
NOTION_API_KEY          # Notion integration token
NOTION_PRODUCTS_DB_ID   # Products database ID
NOTION_EVENTS_DB_ID     # Events database ID
NOTION_BLOG_DB_ID       # Blog database ID
NEXT_PUBLIC_SITE_URL    # Production URL (https://veganmotoclub.com)
```

## Design System

### Rules

1. **Read specs before writing UI code.** Read the relevant file in `specs/components/` and `specs/foundations/` first.
2. **Use only tokens from `tokens.css`.** No hardcoded colors (`text-red-600`, `bg-white`, `#hex`), no arbitrary values (`h-[30px]`, `z-[100]`). Use semantic Tailwind classes or standard scale.
3. **Run audit before committing.** `node scripts/token-audit.js` must return exit code 0.
4. **Zero errors required** before any PR is merged.

### Token Layers

- **Layer 1 — Primitives** (`--ds-*`): Raw values in `app/tokens.css` under `:root`
- **Layer 2 — Semantic** (`--color-*` etc.): Aliases in `app/tokens.css`, light + `.dark` variants
- **Layer 3 — Components**: Tailwind classes (`bg-card`, `text-destructive`, `text-success`) — preferred over raw `var()`
- shadcn/ui bridge variables (`--background`, `--foreground`, etc.) live in `app/globals.css`

### Specs

See `specs/` — `foundations/` (color, spacing, typography, radius, elevation, motion), `tokens/token-reference.md`, `components/` (one file per component).

## Remaining TODOs

- [ ] Add donations section with PayPal integration
- [ ] Manual color contrast check (muted-foreground on backgrounds — near WCAG AA threshold)
- [ ] Add `/public/favicon.ico` (currently 404)
- [ ] Add actual `/public/og-image.png` for OpenGraph previews
- [ ] Configure ESLint (not yet set up — `npm run lint` prompts for config)
