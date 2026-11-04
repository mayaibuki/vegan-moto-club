# FaqSection

| Key | Value |
|-----|-------|
| **Category** | Content |
| **Status** | Stable |
| **File** | `components/FaqSection.tsx` |
| **Rendering** | Server component |

## Overview

An always-open list of questions and answers fed by FAQ rows in the Notion Blog database (`getFaqs(category)` in `lib/notion.ts`). The text stays visible so search engines and AI crawlers can quote it, and the FAQPage JSON-LD is generated from the same items so the two cannot drift. No accordion: nothing to open, no JavaScript, no motion.

Used on the home page (Category "General"), `/verification` ("Verification"), each category landing page (the gear category name) and grouped on `/blog`.

## Anatomy

```
[section]                      — space-y-6 max-w-3xl, aria-labelledby
  ├─ <JsonLd>                  — FAQPage, unless withSchema={false}
  ├─ [heading]                 — h2 `.h-section` (default) or h3 `text-lg font-semibold`
  └─ <dl>                      — space-y-6
       └─ [item]               — space-y-2
            ├─ <dt>            — question as h3/h4, `text-lg font-semibold text-balance`
            └─ <dd>            — answer, `text-base text-muted-foreground leading-relaxed max-w-prose text-pretty`
```

## Props

| Prop | Type | Default | Notes |
|------|------|---------|-------|
| `items` | `FaqItem[]` | required | Renders nothing when empty |
| `title` | `string` | "Common questions" | |
| `headingLevel` | `"h2" \| "h3"` | `"h2"` | Questions use the next level down |
| `withSchema` | `boolean` | `true` | `/blog` turns it off and emits one FAQPage block for all groups |
| `id` | `string` | `"faq"` | Prefix for the heading id |

## Rules

- Answers come from Notion (Blog database, Type = FAQ, Category = page). Edit them there, not in code.
- One FAQPage block per page. Several sections on one page share a single block.
- Copy follows `docs/brand-voice.md`: no dashes, digits, standards as printed, no safety promises.
