# Guide page

| Key | Value |
|-----|-------|
| **Category** | Content |
| **Status** | Stable |
| **Files** | `app/guides/[slug]/page.tsx`, `app/guides/page.tsx`, data in `lib/guides.ts` |
| **Rendering** | Static (generateStaticParams, dynamicParams false) |

## Overview

Long-form explainer for one rider question (for example "Is Cordura vegan?"). Content is typed data in `lib/guides.ts`, not MDX: title, description (also the lead and the meta description), dated sections of plain paragraphs, FAQ items, related category slugs and sources. The page emits Article and BreadcrumbList JSON-LD; the FAQ block emits FAQPage through `FaqSection`.

## Anatomy

```
[article]                      — max-w-3xl space-y-10
  ├─ Breadcrumbs               — Home > Guides > title
  ├─ [header]                  — h1 `.h-page`, p `.lead`, updated date (text-sm text-muted-foreground)
  ├─ [section] x N             — h2 `.h-section`, body paragraphs (`text-base text-muted-foreground leading-relaxed max-w-prose text-pretty`)
  ├─ [Related gear]            — h2 `.h-section`, pill links (same classes as the category switcher)
  ├─ FaqSection                — "Common questions"
  └─ [Sources]                 — h2 `text-lg font-semibold`, external links with (opens in new tab)
```

The index at `/guides` lists guides as Cards in a 2-column grid with an ItemList block.

## Rules

- Answer in the first sentence of `description`.
- Copy follows `docs/brand-voice.md`: digits, standards as printed (EN 17092-3 class AA), no dashes, no safety promises. "A rating is a test result, not a guarantee."
- Bump `dateModified` when copy changes; the sitemap reads it.
- 500 to 900 words per guide. Cite the standard or maker in `sources`.
