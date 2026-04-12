# Vegan Moto Club

A curated database of vegan motorcycle gear. Built with Next.js 14 App Router, powered by Notion as a CMS, deployed on Vercel.

**Live:** https://veganmotoclub.com | **GitHub:** https://github.com/mayaibuki/vegan-moto-club

## Features

- Product database (220+ items) with filters (brand, category, gender, riding style), search, pagination, and human-readable slugs
- Events calendar with poster images, date overlays, price pills, and upcoming/past separation
- Blog with featured images
- Native suggestion forms (product URL and event description submitted directly to Notion)
- SEO: JSON-LD (Organization, FAQ, Event, ItemList, breadcrumb), sitemap, robots.ts with AI bot access rules
- Performance: AVIF/WebP images, ISR (revalidate=3600), dynamic imports, stable Notion image proxy
- Design system: 3-layer token architecture, component specs, automated token audit
- Dark mode, fully responsive
- Vercel Analytics and Speed Insights

## Tech Stack

Next.js 14, React 18, TypeScript, Tailwind CSS, shadcn/ui, Notion API (@notionhq/client), Vercel

## Quick Start

```bash
git clone https://github.com/mayaibuki/vegan-moto-club.git
cd vegan-moto-club
npm install
cp .env.example .env.local  # fill in values
npm run dev
```

Visit http://localhost:3000

## Environment Variables

```
NOTION_API_KEY          # Notion integration token
NOTION_PRODUCTS_DB_ID   # Products database ID
NOTION_EVENTS_DB_ID     # Events database ID
NOTION_BLOG_DB_ID       # Blog database ID
NEXT_PUBLIC_SITE_URL    # https://veganmotoclub.com
```

## Project Structure

```
app/                    Pages and layouts (App Router)
  products/             Listing + [slug] detail
  events/               Events listing
  blog/                 Blog listing + [id] detail
  about/                Static about page
  api/                  API routes (suggest, suggest-event, notion-image)
components/             React components
  ui/                   shadcn/ui primitives
  ProductGrid.tsx       Client — filters, search, pagination, URL sync
  ProductCard.tsx       Memoized product card
  EventCard.tsx         Poster + date overlay + price pill
  Breadcrumbs.tsx       Dynamic breadcrumbs
  SuggestProductForm    Native product suggestion form
  SuggestEventForm      Native event suggestion form
  InstagramGallery      Behold widget embed
  Navbar.tsx            Theme toggle, mobile menu
  Footer.tsx            Nav links, social
  Logo.tsx              Size variants
lib/
  notion.ts             Typed Notion client, unstable_cache fetchers
  utils.ts              Helpers (cn, formatPrice, filterProducts, generateSlug)
specs/                  Design system specs (foundations + components)
scripts/
  token-audit.js        Design token compliance checker
Scheduled audit/        Python automation scripts (product audit + enrichment)
```

## Commands

```bash
npm run dev                    # Dev server (port 3000)
npm run build                  # Production build
npm run start                  # Serve production build
node scripts/token-audit.js    # Design token audit (must exit 0)
```

## Design System

Three-layer token architecture: primitives (`--ds-*`), semantic (`--color-*`), and component-level Tailwind classes. Stone base with Lime accent, dark mode via `.dark` class. Full specs live in `specs/`. Compliance is enforced by `scripts/token-audit.js`. See `CLAUDE.md` for rules.

## Automations

Two Python scripts in `Scheduled audit/` handle daily product auditing and new product enrichment. See `Scheduled audit/README.md` for details.

## Documentation

- `PROJECT_SUMMARY.md` -- complete project reference
- `CASESTUDY.md` -- analytical case study
- `PLAN.md` -- roadmap
- `CLAUDE.md` -- AI assistant instructions

## License

All rights reserved -- Vegan Moto Club
