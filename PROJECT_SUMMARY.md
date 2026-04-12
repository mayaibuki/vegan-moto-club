# Vegan Moto Club — Project Reference

## Overview
Curated database of vegan motorcycle gear. Live at https://veganmotoclub.com. Next.js 14 App Router, Notion API, Vercel.

## Pages
- `/` — Homepage: hero ("Ride motorcycles, love animals"), Staff Picks carousel, Upcoming Events (EventCard), Instagram Gallery (Behold widget), Suggest Product Form. JSON-LD: WebSite + FAQPage.
- `/products` — Product listing with ProductGrid (client component): filters (brand, category, gender, riding style), search, pagination, URL param sync. Dynamic import for performance.
- `/products/[slug]` — Product detail with breadcrumbs, related products, JSON-LD breadcrumb. Human-readable slugs via generateSlug().
- `/events` — Events with upcoming/past separation (1-week grace period). EventCard with poster, date overlay, price pill. SuggestEventForm. JSON-LD ItemList of Events.
- `/blog` — Blog listing with featured images, date formatting. JSON-LD ItemList.
- `/blog/[id]` — Individual blog post.
- `/about` — Static about page.

## API Routes
- `app/api/suggest/route.ts` — Product suggestion: accepts URL, writes to Notion Products DB. Honeypot + rate limiting.
- `app/api/suggest-event/route.ts` — Event suggestion: accepts description + URL, writes to Notion Events DB.
- `app/api/notion-image/route.ts` — Stable proxy for Notion-hosted images. Prevents Vercel image optimizer cache key rotation when Notion rotates signed URLs. Pattern: `/api/notion-image?pageId=...&prop=...&idx=...`

## Components
- ProductGrid (client) — filters, search, pagination, URL sync
- ProductCard (React.memo) — product display card
- ProductCardImage — image handling for product cards
- EventCard — poster image + date overlay + price pill (matches Figma)
- Breadcrumbs — dynamic breadcrumb navigation
- RelatedProducts — related product suggestions on detail page
- InstagramGallery — Behold widget embed
- SuggestProductForm — native product suggestion (honeypot spam protection)
- SuggestEventForm — native event suggestion
- Navbar (client) — theme toggle, mobile hamburger menu
- Footer (server) — navigation links, social links
- Logo — SVG logo with size variants
- ui/ — shadcn/ui primitives (Button, Card, Badge, Input, Select, etc.)

## Lib
- `notion.ts` — Notion API client with typed interfaces (Product, Event, BlogPost, NotionPage, NotionRichText, NotionFile). Cached fetchers via `unstable_cache` (1hr prod, 1min dev). Pagination support. Stable image proxy URL generation.
- `utils.ts` — cn() (Tailwind merge), formatPrice(), formatDate(), formatRelativeDate(), formatEventMonth(), formatEventDay() (UTC-safe), isSameEventDay() (UTC-safe), filterProducts(), generateSlug(), getUniqueBrands()

## Design System
- 3-layer token architecture: primitives (--ds-*) -> semantic (--color-*) -> component classes (bg-card, text-destructive)
- Theme: Stone base + Lime accent, DM Sans font
- Dark mode via .dark class on html
- Specs in `specs/foundations/` (color, spacing, typography, radius, elevation, motion) and `specs/components/` (13 component specs)
- Token reference: `specs/tokens/token-reference.md`
- Automated audit: `node scripts/token-audit.js` (exit 0 required)
- Bridge variables for shadcn/ui in `app/globals.css`

## SEO
- Human-readable product slugs
- JSON-LD: Organization, FAQPage, breadcrumb, Event, ItemList
- `app/robots.ts` — allowlists AI bots (GPTBot, Google-Extended, etc.)
- `app/sitemap.xml` — dynamic sitemap with product categories
- Rich openGraph + twitter metadata on all pages

## Performance
- AVIF + WebP image optimization via next.config
- minimumCacheTTL: 2678400 (31 days)
- ISR: revalidate = 3600 on all data pages
- ProductGrid dynamically imported (keeps /products static shell fast)
- Vercel Analytics + Speed Insights installed
- Stable notion-image proxy prevents cache churn

## Automations (Scheduled audit/)
Two Python scripts run daily:
1. `vmc_product_audit.py` — Audits existing Notion product entries. Scrapes product URLs with BeautifulSoup, maps fields using keyword matching (never creates new select options), writes dated .md + .html reports.
2. `vmc_new_product_audit.py` — Enriches new user-submitted products (URL present, Description empty). Scrapes, writes humanized description, downloads photos, sets Vegan Verified = "Verified Vegan by AI". Batch limit 20/run. Outputs daily reports.
See `Scheduled audit/README.md` for full details.

## Environment Variables
```
NOTION_API_KEY          # Notion integration token
NOTION_PRODUCTS_DB_ID   # Products database ID
NOTION_EVENTS_DB_ID     # Events database ID
NOTION_BLOG_DB_ID       # Blog database ID
NEXT_PUBLIC_SITE_URL    # https://veganmotoclub.com
```

## Commands
```bash
npm run dev                    # Dev server
npm run build                  # Production build
npm run start                  # Serve build
node scripts/token-audit.js    # Token audit
```
