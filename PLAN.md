# Vegan Moto Club — Roadmap

## Shipped

Condensed timeline of what's been built:

**Jan–Feb 2026 — Initial Build**
- Next.js 14 + Notion API integration (Products, Events, Blog databases)
- Full product grid with filters, search, pagination
- Events page, blog, about page
- Custom branding: Stone + Lime palette, DM Sans font
- Dark mode, responsive design
- shadcn/ui component library
- Deployed to Vercel at veganmotoclub.com

**Feb–Mar 2026 — Launch & Polish**
- Native suggestion forms (product + event → Notion) with honeypot spam protection
- SEO pass: human-readable product slugs, breadcrumbs, JSON-LD schemas (Organization, FAQ, Event, ItemList, breadcrumb), sitemap, robots.ts with AI bot access
- Design system audit + tokenization: 3-layer token architecture, component specs, automated token-audit.js
- Vercel Analytics + Speed Insights

**Mar–Apr 2026 — Performance & Automation**
- Image optimization: AVIF/WebP, minimumCacheTTL 31d, stable notion-image proxy for signed URL rotation
- ISR: revalidate=3600 on all data pages, dynamic import for ProductGrid
- Event card redesign from Figma (poster + date overlay + price pill)
- UTC-safe event date formatting
- Python automation: daily product audit (vmc_product_audit.py) + new product enrichment (vmc_new_product_audit.py)

## In Progress / To Improve

### Product Audit Automation
Current: keyword-match pipeline using BeautifulSoup scraping.
Next: Replace keyword matching with LLM-based field extraction for better accuracy on materials, season, riding style classification.

### Product Detail Writer
Current: vmc_new_product_audit.py writes humanized descriptions for new submissions.
Next: Improve LLM-generated descriptions — better tone, more detailed specs, consistent format across all products.

### Discord → Notion Event Sync
Goal: Automatically monitor the Vegan Moto Club Discord events channel and create Notion entries for new events.
Approach: GitHub Action polling Discord API on a schedule, parsing event posts, writing to Notion Events DB.
Status: Deferred — design decided, not yet implemented.

### Project Folder Cleanup
- Remove stale files and outdated documentation artifacts
- Organize Scheduled audit/ outputs
- Clean up any unused dependencies

### Portfolio Case Study
- Write and publish a case study on mayaibuki.com (Webflow)
- Based on CASESTUDY.md analysis (Morton/Wen/Harrison frameworks)
- Demonstrate the "vibe engineering" methodology

## Known TODOs

From CLAUDE.md and ongoing work:
- [ ] Add donations section (Venmo / PayPal.me link)
- [ ] Add og-image.png for OpenGraph previews
- [ ] Configure ESLint
- [ ] Manual color contrast check (muted-foreground near WCAG AA threshold)
- [ ] Discord → Notion event sync (GitHub Action)
- [ ] Product audit LLM upgrade (keyword → LLM extraction)
- [ ] Product detail writer LLM upgrade
- [ ] Webflow portfolio case study
- [ ] Project folder cleanup

## Completed TODOs (for reference)
- [x] Favicon + app icons
- [x] Vercel Analytics
- [x] Speed Insights
- [x] Image cost optimization (AVIF, ISR, notion-image proxy)
- [x] UTC-safe event dates
- [x] Human-readable product slugs
- [x] Native suggestion forms
- [x] Design system tokenization + audit script
- [x] Event card redesign (Figma spec)
