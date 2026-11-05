# FaqShowcase

| Key | Value |
|-----|-------|
| **Category** | Content |
| **Status** | Stable |
| **File** | `components/FaqShowcase.tsx` |
| **Rendering** | Client component (`"use client"`) |

## Overview

Progressive-disclosure FAQ for the home page: one question open at a time. From `lg` up, a square photo sits beside the list and crossfades to the open question's image, and the list auto-advances every `--duration-dwell` (10s) while it is on screen. Below `lg` it is a single column, each open panel shows its own photo under the answer, and nothing advances on its own.

Fed by the same Notion rows as `FaqSection` (Blog database, Type = FAQ, Category = General) via `getFaqs("General")`. The photo is the row's **Featured image**; rows without one show `/images/hero.jpg`.

Every answer is in the server HTML (collapsed panels are `inert`, not removed), and the FAQPage JSON-LD is built from the same items, so search engines and AI crawlers see the same text as `FaqSection` gives them.

## Anatomy

```
[section]                         space-y-8, aria-labelledby
  ├─ <JsonLd>                     FAQPage, unless withSchema={false}
  ├─ h2.h-section                 title (Title Case, "Common Questions")
  └─ [grid]                       gap-8; lg: grid-cols-2 gap-16 items-start
       ├─ [photo column]          hidden below lg; lg: sticky top-24
       │    └─ [frame]            relative aspect-square rounded-2xl overflow-hidden bg-muted
       │         └─ <Image> ×n    fill object-cover, transition-opacity duration-300, open one opacity-100
       └─ [list]                  border-b border-border
            └─ [item] ×n
                 ├─ [track]       relative h-px bg-border; fill: bg-primary-text animate-progress (lg+, autoplay only)
                 ├─ h3 > button   focus-ring group flex min-h-11 w-full justify-between py-5 text-left
                 │    ├─ question text-lg md:text-xl font-semibold text-balance
                 │    └─ chip     h-8 w-8 rounded-full border border-border bg-card; hover bg-accent; ChevronDown rotates 180° when open
                 └─ [panel]       role=region, grid transition-[grid-template-rows] duration-300, grid-rows-open | grid-rows-closed, inert when closed
                      └─ min-h-0 overflow-hidden > space-y-4 pb-6
                           ├─ answer   text-base text-muted-foreground leading-relaxed text-pretty max-w-prose
                           └─ photo    lg:hidden, relative aspect-4/3 sm:aspect-video rounded-xl overflow-hidden bg-muted
```

## Props

| Prop | Type | Default | Notes |
|------|------|---------|-------|
| `items` | `FaqItem[]` | required | Renders nothing when empty. `image` is optional per item |
| `title` | `string` | "Common Questions" | |
| `withSchema` | `boolean` | `true` | One FAQPage block per page |
| `id` | `string` | `"faq"` | Prefix for the heading id |

## Behaviour

| Viewport | Layout | Photo | Auto-advance |
|---|---|---|---|
| < 1024 (`lg`) | One column | Inside the open panel, under the answer | Never (avoids the page jumping as tall panels swap) |
| ≥ 1024 | Photo left, list right | Crossfade in the photo column | Yes, every 10s, looping |

Auto-advance rules (see the Auto-advance pattern in `specs/foundations/motion.md`):

- The progress fill's CSS animation is the timer: `animationend` opens the next item. Pausing sets `animation-play-state: paused`.
- Runs only while at least 30% of the section is on screen (IntersectionObserver).
- Pauses while the pointer is over the section or focus is inside it.
- Stops for good on the first click or keyboard activation. The reader is in control from then on.
- Off under `prefers-reduced-motion: reduce`, and the fill is not rendered. The global reduced-motion rule shortens animations to 0.01ms, which would cycle the items instantly.
- Clicking the open question keeps it open: exactly one is always open.

## Accessibility

- WAI accordion pattern: `h3 > button[aria-expanded][aria-controls]`, panel `role="region"` labelled by its button.
- Collapsed panels are `inert`, so Tab moves from question to question and screen readers skip hidden answers.
- Photos are `alt=""`: the answer text carries the meaning.
- The whole question row is the tap target (72px tall in practice, never under 44px).
- The progress fill is `bg-primary-text` (lime-700 / lime-400), at least 3:1 on the page in both themes.

## Rules

- Home page only. Other pages keep the always-open `FaqSection`.
- Answers and photos come from Notion. Edit them there, not in code. Use documentary photos, no text overlays.
- Copy follows `docs/brand-voice.md`.
