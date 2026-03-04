# Typography Foundation

## Overview

Vegan Moto Club uses **DM Sans** as the sole typeface, loaded via `next/font/google` for optimal performance (no render-blocking CSS). The font is assigned to the `--font-dm-sans` CSS variable and consumed through Tailwind's `font-sans` utility.

---

## Font Family

| Role     | Family   | CSS Variable       | Tailwind Class | Fallback Stack                         |
| -------- | -------- | ------------------ | -------------- | -------------------------------------- |
| Primary  | DM Sans  | `--font-dm-sans`   | `font-sans`    | `system-ui, -apple-system, sans-serif` |

### Loading Configuration

```tsx
// app/layout.tsx
const dmSans = DM_Sans({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-dm-sans",
})
```

The `display: "swap"` setting shows fallback text immediately, swapping in DM Sans once loaded. The font variable is applied to the `<html>` element and referenced in `tailwind.config.ts`:

```ts
fontFamily: {
  sans: ['var(--font-dm-sans)', 'system-ui', '-apple-system', 'sans-serif'],
}
```

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

### Heading Hierarchy

Maintain a strict heading hierarchy for both visual design and accessibility. Every page should have exactly one `<h1>`, and headings should not skip levels.

```html
<!-- Page title -->
<h1 class="text-4xl font-bold tracking-tight leading-tight">
  Vegan Motorcycle Gear
</h1>

<!-- Section heading -->
<h2 class="text-3xl font-bold tracking-tight leading-tight">
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
<h1 class="text-6xl font-bold tracking-tight leading-none">
  Ride Compassionate
</h1>
```

### Body Text

```html
<!-- Default paragraph -->
<p class="text-base font-normal leading-normal">
  All products are verified cruelty-free...
</p>

<!-- Lead paragraph -->
<p class="text-lg font-normal leading-relaxed">
  A curated database of vegan motorcycle gear...
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
<!-- Hero heading: scales up at larger screens -->
<h1 class="text-4xl md:text-6xl font-bold tracking-tight">
  Ride Compassionate
</h1>

<!-- Body text: slightly larger on desktop -->
<p class="text-base md:text-lg leading-normal md:leading-relaxed">
  ...
</p>
```

---

## Rules

1. **One typeface.** DM Sans is the only font. Do not introduce additional font families.
2. **Use the scale.** Only use sizes defined in the size scale table. Do not use arbitrary sizes like `text-[17px]`.
3. **Pair weight with purpose.** Bold (700) is for emphasis and headings. Normal (400) is for body text. Medium (500) is for labels and navigation.
4. **Heading hierarchy matters.** Never skip heading levels. Use CSS classes for visual styling while keeping semantic HTML correct.
5. **Line height matches context.** Headings use tight (1.25). Body text uses normal (1.5). Long-form content uses relaxed (1.625).
