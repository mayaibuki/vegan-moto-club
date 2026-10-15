# Typography Foundation

## Overview

Vegan Moto Club uses two typefaces:

- **DM Sans** for body copy and all UI (cards, h3s, buttons, prices, labels, `.lead`). Loaded with `next/font/google`.
- **Redaction** for display headings only: every element carrying `.h-hero`, `.h-page` or `.h-section` (page h1s and section h2s). Loaded with `next/font/local` from `webfonts/`. As the visitor scrolls, these headings degrade from the clean cut to progressively pixelated cuts (see Scroll Degradation).

Both are configured in `app/fonts.ts`; all font variables are applied on `<html>` in `app/layout.tsx`.

---

## Font Family

| Role    | Family                 | CSS Variable           | Token                                         | Tailwind Class | Fallback Stack                         |
| ------- | ---------------------- | ---------------------- | --------------------------------------------- | -------------- | -------------------------------------- |
| Body/UI | DM Sans                | `--font-dm-sans`       | `--ds-font-sans` / `--font-family`            | `font-sans`    | `system-ui, -apple-system, sans-serif` |
| Display | Redaction (clean)      | `--font-redaction`     | `--ds-font-serif` / `--font-family-display`   | `font-serif`   | `Georgia, serif`                       |
| Display | Redaction 10 / 20 / 35 | `--font-redaction-10`, `--font-redaction-20`, `--font-redaction-35` | (used only by the `data-degrade` rules) | none | `Georgia, serif` |

Each Redaction face loads weights 400 and 700 with `display: "swap"` and `adjustFontFallback: "Times New Roman"`. Headings use 700. Italics are not loaded for the degraded cuts; the clean Italic file stays in `webfonts/` but is unused. Cuts above 35 (`_50`, `_70`, `_100`) were removed.

### Scroll Degradation

`components/DegradeOnScroll.tsx` (mounted once in the root layout) sets `data-degrade` on each heading from the position of its top edge in the viewport:

| Heading top (fraction of viewport height from the top) | `data-degrade` | Face            |
| ------------------------------------------------------ | -------------- | --------------- |
| 0.40 and below the fold (lower 60%)                    | none (0)       | Redaction       |
| 0.267 to 0.40                                          | `10`           | Redaction_10    |
| 0.133 to 0.267                                         | `20`           | Redaction_20    |
| above 0.133 (including off the top)                    | `35`           | Redaction_35    |

- It reverses as headings move back down. Levels above 35 are not used.
- Nothing degrades before the first scroll, so headings above the fold paint clean.
- Under `prefers-reduced-motion: reduce` it does nothing and headings stay clean.
- The cuts share metrics: line heights are identical and single-line widths differ by at most ~2.7px at 30px (6px on the 60px hero), so swapping does not change line breaks or layout.
- `font-synthesis: none` is set on the heading recipes.

### Italics

Not used. No italic accents in headings or `.lead`.

---

## Size Scale

| Name       | Size (rem) | Size (px) | Tailwind Class | CSS Token             | Typical Use                     |
| ---------- | ---------- | --------- | -------------- | --------------------- | ------------------------------- |
| Caption    | 0.75rem    | 12px      | `text-xs`      | `--font-size-caption` | Timestamps, fine print, labels  |
| Body SM    | 0.875rem   | 14px      | `text-sm`      | `--font-size-body-sm` | Secondary text, table cells     |
| Body       | 1rem       | 16px      | `text-base`    | `--font-size-body`    | Default paragraph text          |
| Body LG    | 1.125rem   | 18px      | `text-lg`      | `--font-size-body-lg` | Lead paragraphs, emphasis       |
| H4         | 1.25rem    | 20px      | `text-xl`      | `--font-size-h4`      | Card titles, subsection heads   |
| H3         | 1.5rem     | 24px      | `text-2xl`     | `--font-size-h3`      | Section subheadings             |
| H2         | 1.875rem   | 30px      | `text-3xl`     | `--font-size-h2`      | Page section titles             |
| H1         | 2.25rem    | 36px      | `text-4xl`     | `--font-size-h1`      | Page titles                     |
| Display    | 3.75rem    | 60px      | `text-6xl`     | `--font-size-display` | Hero headlines                  |

---

## Weight Scale

| Name      | Value | Tailwind Class   | CSS Token                 | Typical Use                        |
| --------- | ----- | ---------------- | ------------------------- | ---------------------------------- |
| Normal    | 400   | `font-normal`    | `--font-weight-normal`    | Body text, descriptions            |
| Medium    | 500   | `font-medium`    | `--font-weight-medium`    | Labels, nav links, subtle emphasis |
| Semibold  | 600   | `font-semibold`  | `--font-weight-semibold`  | Card titles, subheadings           |
| Bold      | 700   | `font-bold`      | `--font-weight-bold`      | Page titles, hero text, CTAs       |

---

## Line Height Scale

| Name     | Value  | Tailwind Class    | CSS Token                  | Typical Use                             |
| -------- | ------ | ----------------- | -------------------------- | --------------------------------------- |
| None     | 1      | `leading-none`    | `--ds-leading-none`        | Single-line badges, icon labels         |
| Tight    | 1.25   | `leading-tight`   | `--line-height-tight`      | Headings, display text                  |
| Snug     | 1.375  | `leading-snug`    | `--ds-leading-snug`        | Compact multi-line text                 |
| Normal   | 1.5    | `leading-normal`  | `--line-height-normal`     | Default body text, paragraphs           |
| Relaxed  | 1.625  | `leading-relaxed` | `--line-height-relaxed`    | Long-form reading, blog content         |

---

## Tracking (Letter Spacing)

| Name    | Value       | Tailwind Class     | CSS Token              | Typical Use                    |
| ------- | ----------- | ------------------ | ---------------------- | ------------------------------ |
| Tight   | -0.025em    | `tracking-tight`   | `--ds-tracking-tight`  | Large headings, display text   |
| Normal  | 0em         | `tracking-normal`  | `--ds-tracking-normal` | Body text (default)            |
| Wide    | 0.025em     | `tracking-wide`    | `--ds-tracking-wide`   | Uppercase labels, small caps   |

---

## Usage Patterns

### Heading Recipes

Three `@layer components` classes in `app/globals.css` set every page h1 and section h2. Do not restyle those headings inline; pick the recipe that matches the heading's role.

| Class        | Sizes                  | Weight | Tracking / wrap                | Used on                                                                                                                 |
| ------------ | ---------------------- | ------ | ------------------------------ | ----------------------------------------------------------------------------------------------------------------------- |
| `.h-hero`    | `text-4xl md:text-6xl` | 700    | `tracking-tight text-balance`  | Home hero h1                                                                                                            |
| `.h-page`    | `text-3xl md:text-4xl` | 700    | `tracking-tight text-balance`  | Every other page h1: products, category pages, product detail, events, about, verification, 404, error                  |
| `.h-section` | `text-2xl md:text-3xl` | 700    | `tracking-tight text-balance`  | Section h2s: home (Staff Picks, Upcoming Events), events, about, verification, product Description, Related Products, Past Events |

Rules:

- **Sizes and weights are unchanged from before the recipes.** What changed is that one role now maps to one style (for example, every h2 section heading is 24px on mobile and 30px from `md`, weight 700).
- **The recipes set the display family.** `.h-hero`, `.h-page` and `.h-section` include `font-serif` (Redaction) and `font-synthesis: none`. Do not use `font-serif` anywhere else.
- **Not covered by the recipes:** `CardTitle` (the Suggest forms' h2) stays `text-2xl font-semibold leading-none` without tracking; footer column headings stay `text-base font-bold`; h3s (product card names, event card titles, verification tier headings) are untouched and use `text-lg font-semibold` or their component's own style. The visually hidden "Products" h2s stay `sr-only`.
- **Past Events** adds `text-muted-foreground` on top of `.h-section` to stay secondary to Upcoming Events.
- Weights in use: 400 body, 500 labels/nav/buttons, 600 card titles, 700 headings and prices.

### Product Detail Title Block

On `/products/[slug]` the name, brand and price read as one block, followed directly by the store button:

| Element | Classes                                           | Computed (mobile / md+) |
| ------- | ------------------------------------------------- | ----------------------- |
| Name    | `.h-page` (h1)                                    | 30px / 36px, 700        |
| Brand   | `text-lg font-medium text-muted-foreground`       | 18px, 500               |
| Price   | `text-2xl md:text-3xl font-bold tabular-nums`     | 24px / 30px, 700        |

The block uses `space-y-1`, with `pt-2` on the price. The price is always one size step below the name. Spec labels below it (`dt`) are `text-sm font-medium text-muted-foreground mb-2`; values are `text-base font-semibold`. From `md` the spec list is a two-column `dl` (`grid-cols-[auto_1fr]`).

### Lead Paragraph

A page that opens with an intro paragraph under its h1 uses the `.lead` class (`text-lg md:text-xl text-foreground leading-relaxed text-pretty`): 18px on mobile, 20px from `md`, in the full foreground colour, so it reads as the entry point of the page.

- Applied on: about (both opening paragraphs), verification, `/products`, and the first intro paragraph of each category page.
- Paragraphs that follow a lead are body copy: `text-base text-muted-foreground leading-relaxed max-w-prose text-pretty`. `max-w-prose` caps lines at about 65 characters; the `max-w-3xl` page container stays for headings and cards.
- On category pages the lead also gets `max-w-prose`.
- Result counts ("N products in this category", "Showing 1-24 of N products") use `text-sm font-medium text-foreground` so both pages match.

### Heading Hierarchy

Maintain a strict heading hierarchy for both visual design and accessibility. Every page should have exactly one `<h1>`, and headings should not skip levels.

```html
<!-- Page title (.h-page: text-3xl md:text-4xl font-bold tracking-tight text-balance) -->
<h1 class="h-page">
  Vegan Motorcycle Gear
</h1>

<!-- Section heading (.h-section: text-2xl md:text-3xl font-bold tracking-tight text-balance) -->
<h2 class="h-section">
  Jackets
</h2>

<!-- Subsection heading -->
<h3 class="text-2xl font-semibold leading-tight">
  Summer Collection
</h3>

<!-- Card / item title -->
<h4 class="text-xl font-semibold leading-tight">
  RevIt Eclipse H2O
</h4>
```

### Display / Hero Text

```html
<h1 class="h-hero">
  Ride Compassionate
</h1>
```

### Body Text

```html
<!-- Default paragraph -->
<p class="text-base font-normal leading-normal">
  All products are verified cruelty-free...
</p>

<!-- Lead paragraph (the .lead class) -->
<p class="lead">
  A curated database of vegan motorcycle gear...
</p>

<!-- Body paragraph that follows a lead -->
<p class="text-base text-muted-foreground leading-relaxed max-w-prose text-pretty">
  Every product carries a verification badge...
</p>

<!-- Secondary / helper text -->
<p class="text-sm text-muted-foreground leading-normal">
  Last updated 3 days ago
</p>
```

### Captions and Labels

```html
<!-- Fine print -->
<span class="text-xs text-muted-foreground leading-normal">
  Prices may vary by retailer
</span>

<!-- Form label -->
<label class="text-sm font-medium leading-none">
  Email Address
</label>

<!-- Uppercase label -->
<span class="text-xs font-medium tracking-wide uppercase">
  New Arrival
</span>
```

---

## Responsive Typography

Use Tailwind responsive prefixes to scale typography at breakpoints:

```html
<!-- Hero heading (.h-hero): scales up at larger screens -->
<h1 class="text-4xl md:text-6xl font-bold tracking-tight text-balance">
  Ride Compassionate
</h1>

<!-- Body text: slightly larger on desktop -->
<p class="text-base md:text-lg leading-normal md:leading-relaxed">
  ...
</p>
```

---

## Rules

1. **Two typefaces.** Redaction only through the three heading recipes; DM Sans for everything else. Do not introduce other families.
2. **Use the scale.** Only use sizes defined in the size scale table. Do not use arbitrary sizes like `text-[17px]`.
3. **Pair weight with purpose.** Bold (700) is for emphasis and headings. Normal (400) is for body text. Medium (500) is for labels and navigation.
4. **Heading hierarchy matters.** Never skip heading levels. Use the recipe classes for visual styling while keeping semantic HTML correct.
6. **Three heading recipes, one lead.** Page h1s use `.h-page` (home hero: `.h-hero`), section h2s use `.h-section`, and the intro under an h1 uses `.lead`. No inline heading sizes.
5. **Line height matches context.** Headings use tight (1.25). Body text uses normal (1.5). Long-form content uses relaxed (1.625).
