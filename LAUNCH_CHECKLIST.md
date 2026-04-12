# Vegan Moto Club — Maintenance Checklist

Recurring tasks to keep the live site healthy.

## Weekly

- [ ] Review Vercel Speed Insights dashboard for performance regressions
- [ ] Check Vercel deployment logs for build warnings or image optimization issues
- [ ] Review pending product suggestions in Notion (submitted via /api/suggest)
- [ ] Review pending event suggestions in Notion (submitted via /api/suggest-event)
- [ ] Check `Scheduled audit/` for recent daily audit reports — review flagged items

## Monthly

- [ ] Run `node scripts/token-audit.js` — must exit 0
- [ ] Run a broken-link scan across the site (check product URLs still resolve)
- [ ] Run a broken-image scan (check Notion image proxy is serving correctly)
- [ ] Review Vercel Analytics for traffic patterns and top pages
- [ ] Check Notion databases for stale or duplicate entries
- [ ] Verify dark mode renders correctly on all pages (spot check)

## Quarterly

- [ ] Update npm dependencies (`npm outdated`, then `npm update`)
- [ ] Check for Next.js major version updates and breaking changes
- [ ] Review color contrast compliance (muted-foreground on backgrounds — near WCAG AA threshold)
- [ ] Audit Notion database schema — prune unused select options
- [ ] Review and update SEO metadata if site content has changed significantly
- [ ] Test all forms (product suggestion, event suggestion) end-to-end

## After Major Changes

- [ ] Run `npm run build` locally before pushing
- [ ] Run `node scripts/token-audit.js`
- [ ] Verify all pages render correctly (home, products, product detail, events, blog, about)
- [ ] Check mobile responsiveness
- [ ] Verify JSON-LD structured data is valid (use Google's Rich Results Test)
- [ ] Check that sitemap.xml includes new routes if any were added

## Automation Health

- [ ] Verify `vmc_product_audit.py` is running daily and producing reports
- [ ] Verify `vmc_new_product_audit.py` is running daily and enriching new submissions
- [ ] Review audit HTML reports for false positives or missed fields
- [ ] Check that automation respects schema constraints (no new select options created)
