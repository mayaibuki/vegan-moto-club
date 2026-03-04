# Token Reference

> Master map of every CSS variable in the Vegan Moto Club design system.

## How Tokens Work

This design system uses a **3-layer token architecture**:

| Layer | Prefix | Purpose | Who references it |
|-------|--------|---------|-------------------|
| **1 — Primitives** | `--ds-*` | Raw values (palette, scale, constants) | Layer 2 only |
| **2 — Semantic aliases** | `--color-*`, `--space-*`, `--font-*`, etc. | Contextual meaning with fallbacks | Components (Layer 3) |
| **3 — Components** | Tailwind classes / `var()` | Actual UI elements | End users |

**Rule:** Components must NEVER reference Layer 1 primitives or raw values — only Layer 2 aliases (via Tailwind utility classes or `var(--token)`).

### shadcn/ui Bridge

The project also maintains the **shadcn/ui variable convention** (`--background`, `--foreground`, `--primary`, etc.) in `globals.css`. Tailwind resolves these via `hsl(var(--token))` in `tailwind.config.ts`. These are the primary interface for Tailwind classes.

---

## Color Tokens

### Primitives (Layer 1)

| Token | HSL Value | Usage |
|-------|-----------|-------|
| `--ds-stone-50` | `0 0% 98%` | Lightest neutral, text-inverse |
| `--ds-stone-100` | `12 6.5% 97.5%` | Muted/secondary backgrounds (light) |
| `--ds-stone-200` | `12 6.3% 93.8%` | Borders, inputs (light) |
| `--ds-stone-300` | `12 5.4% 84%` | Chart accents |
| `--ds-stone-400` | `12 4.9% 64%` | Muted text (dark mode) |
| `--ds-stone-500` | `12 6.5% 51.5%` | Muted text (light mode) |
| `--ds-stone-800` | `12 6.3% 18.8%` | Dark backgrounds, borders (dark) |
| `--ds-stone-900` | `12 8.7% 11.8%` | Foreground text (light) |
| `--ds-stone-950` | `12 8.3% 7.2%` | Darkest, bg in dark mode |
| `--ds-white` | `0 0% 100%` | Pure white |
| `--ds-lime-200` | `79.9 84.6% 80.2%` | Chart accent |
| `--ds-lime-300` | `79.7 77.9% 69.7%` | Chart accent |
| `--ds-lime-400` | `79.1 64.5% 57.5%` | Accent (light), primary (dark) |
| `--ds-lime-500` | `77.9 54.4% 47.4%` | Primary (light), accent (dark) |
| `--ds-lime-600` | `77.2 61.3% 38.5%` | Chart accent (dark) |
| `--ds-green-600` | `142 71% 45%` | Success (light) |
| `--ds-green-400` | `142 69% 58%` | Success (dark) |
| `--ds-red-light` | `0 84.2% 60.2%` | Destructive (light) |
| `--ds-red-dark` | `0 62.8% 30.6%` | Destructive (dark) |

### Semantic Aliases (Layer 2)

| Token | Light | Dark | Tailwind | When to use |
|-------|-------|------|----------|-------------|
| `--color-bg` | white | stone-950 | `bg-background` | Page background |
| `--color-bg-subtle` | stone-100 | stone-800 | `bg-muted` | Subtle section bg |
| `--color-bg-muted` | stone-100 | stone-800 | `bg-muted` | Muted backgrounds |
| `--color-bg-inverse` | stone-950 | white | — | Inverted sections |
| `--color-text` | stone-900 | stone-50 | `text-foreground` | Primary text |
| `--color-text-muted` | stone-500 | stone-400 | `text-muted-foreground` | Secondary text |
| `--color-text-inverse` | stone-50 | stone-900 | — | Text on inverse bg |
| `--color-text-on-primary` | stone-950 | stone-950 | `text-primary-foreground` | Text on primary bg |
| `--color-primary` | lime-500 | lime-400 | `bg-primary`, `text-primary` | Brand/CTA |
| `--color-primary-hover` | lime-400 | lime-500 | `hover:bg-primary/90` | Primary hover |
| `--color-accent` | lime-400 | lime-500 | `bg-accent` | Accent highlight |
| `--color-border` | stone-200 | stone-800 | `border-border` | Default borders |
| `--color-border-muted` | stone-200 | stone-800 | `border-border/50` | Subtle borders |
| `--color-input` | stone-200 | stone-800 | `border-input` | Input borders |
| `--color-ring` | lime-500 | lime-400 | `ring-ring` | Focus rings |
| `--color-card-bg` | white | stone-900 | `bg-card` | Card backgrounds |
| `--color-card-text` | stone-900 | stone-50 | `text-card-foreground` | Card text |
| `--color-destructive` | red-light | red-dark | `text-destructive`, `bg-destructive` | Errors, danger |
| `--color-destructive-text` | stone-50 | stone-50 | `text-destructive-foreground` | Text on destructive bg |
| `--color-success` | green-600 | green-400 | `text-success`, `bg-success` | Success states |
| `--color-success-text` | green-600 | green-400 | `text-success` | Success text |

### shadcn/ui Bridge Variables (globals.css)

| CSS Variable | Light | Dark | Tailwind Class |
|---|---|---|---|
| `--background` | `0 0% 100%` | `12 8.3% 7.2%` | `bg-background` |
| `--foreground` | `12 8.7% 11.8%` | `0 0% 98%` | `text-foreground` |
| `--card` | `0 0% 100%` | `12 8.7% 11.8%` | `bg-card` |
| `--card-foreground` | `12 8.7% 11.8%` | `0 0% 98%` | `text-card-foreground` |
| `--popover` | `0 0% 100%` | `12 8.7% 11.8%` | `bg-popover` |
| `--popover-foreground` | `12 8.7% 11.8%` | `0 0% 98%` | `text-popover-foreground` |
| `--primary` | `77.9 54.4% 47.4%` | `79.1 64.5% 57.5%` | `bg-primary`, `text-primary` |
| `--primary-foreground` | `12 8.3% 7.2%` | `12 8.3% 7.2%` | `text-primary-foreground` |
| `--secondary` | `12 6.5% 97.5%` | `12 6.3% 18.8%` | `bg-secondary` |
| `--secondary-foreground` | `12 8.7% 11.8%` | `0 0% 98%` | `text-secondary-foreground` |
| `--accent` | `79.1 64.5% 57.5%` | `77.9 54.4% 47.4%` | `bg-accent` |
| `--accent-foreground` | `12 8.3% 7.2%` | `12 8.3% 7.2%` | `text-accent-foreground` |
| `--muted` | `12 6.5% 97.5%` | `12 6.3% 18.8%` | `bg-muted` |
| `--muted-foreground` | `12 6.5% 51.5%` | `12 4.9% 64%` | `text-muted-foreground` |
| `--destructive` | `0 84.2% 60.2%` | `0 62.8% 30.6%` | `bg-destructive`, `text-destructive` |
| `--destructive-foreground` | `0 0% 98%` | `0 0% 98%` | `text-destructive-foreground` |
| `--success` | `142 71% 45%` | `142 69% 58%` | `bg-success`, `text-success` |
| `--success-foreground` | `0 0% 100%` | `0 0% 100%` | `text-success-foreground` |
| `--border` | `12 6.3% 93.8%` | `12 6.3% 18.8%` | `border-border` |
| `--input` | `12 6.3% 93.8%` | `12 6.3% 18.8%` | `border-input` |
| `--ring` | `77.9 54.4% 47.4%` | `79.1 64.5% 57.5%` | `ring-ring` |
| `--radius` | `0.75rem` | — | `rounded-lg`, `rounded-md`, `rounded-sm` |

---

## Spacing Tokens

### Primitives

| Token | Value | px | Tailwind | Use case |
|-------|-------|-----|----------|----------|
| `--ds-space-0` | `0rem` | 0 | `p-0`, `m-0` | Reset |
| `--ds-space-0-5` | `0.125rem` | 2 | `p-0.5` | Hairline |
| `--ds-space-1` | `0.25rem` | 4 | `p-1`, `gap-1` | Tight inner |
| `--ds-space-1-5` | `0.375rem` | 6 | `p-1.5`, `gap-1.5` | Badge gaps |
| `--ds-space-2` | `0.5rem` | 8 | `p-2`, `gap-2` | Compact |
| `--ds-space-2-5` | `0.625rem` | 10 | `p-2.5` | Input padding-y |
| `--ds-space-3` | `0.75rem` | 12 | `p-3`, `gap-3` | Small gap |
| `--ds-space-4` | `1rem` | 16 | `p-4`, `gap-4` | Default |
| `--ds-space-5` | `1.25rem` | 20 | `p-5`, `gap-5` | Card content |
| `--ds-space-6` | `1.5rem` | 24 | `p-6`, `gap-6` | Grid gaps |
| `--ds-space-7` | `1.75rem` | 28 | `p-7` | Card sections |
| `--ds-space-8` | `2rem` | 32 | `p-8`, `gap-8` | Section |
| `--ds-space-10` | `2.5rem` | 40 | `p-10`, `gap-10` | Large section |
| `--ds-space-12` | `3rem` | 48 | `mt-12` | Footer margin |
| `--ds-space-16` | `4rem` | 64 | `py-16` | Hero padding |
| `--ds-space-20` | `5rem` | 80 | `p-20` | XL spacing |
| `--ds-space-24` | `6rem` | 96 | `py-24` | Hero (desktop) |

### Semantic Aliases

| Token | Resolves to | px | When to use |
|-------|-------------|-----|-------------|
| `--space-xs` | `--ds-space-1` | 4 | Tight inner spacing |
| `--space-sm` | `--ds-space-2` | 8 | Compact spacing |
| `--space-md` | `--ds-space-4` | 16 | Default component spacing |
| `--space-lg` | `--ds-space-6` | 24 | Generous group spacing |
| `--space-xl` | `--ds-space-8` | 32 | Section spacing |
| `--space-2xl` | `--ds-space-10` | 40 | Large section gaps |
| `--space-3xl` | `--ds-space-16` | 64 | Page-level sections |
| `--space-4xl` | `--ds-space-24` | 96 | Hero sections |

---

## Typography Tokens

### Font Size

| Token | Value | px | Tailwind | Usage |
|-------|-------|-----|----------|-------|
| `--font-size-caption` | `0.75rem` | 12 | `text-xs` | Labels, captions, badges |
| `--font-size-body-sm` | `0.875rem` | 14 | `text-sm` | Secondary body, form labels |
| `--font-size-body` | `1rem` | 16 | `text-base` | Default body text |
| `--font-size-body-lg` | `1.125rem` | 18 | `text-lg` | Large body, nav links |
| `--font-size-h4` | `1.25rem` | 20 | `text-xl` | Card titles, subsections |
| `--font-size-h3` | `1.5rem` | 24 | `text-2xl` | Section headings |
| `--font-size-h2` | `1.875rem` | 30 | `text-3xl` | Page headings |
| `--font-size-h1` | `2.25rem` | 36 | `text-4xl` | Large page headings |
| `--font-size-display` | `3.75rem` | 60 | `text-6xl` | Hero headings |

### Font Weight

| Token | Value | Tailwind | Usage |
|-------|-------|----------|-------|
| `--font-weight-normal` | `400` | `font-normal` | Body text |
| `--font-weight-medium` | `500` | `font-medium` | Nav links, labels, buttons |
| `--font-weight-semibold` | `600` | `font-semibold` | Card titles, section heads |
| `--font-weight-bold` | `700` | `font-bold` | Page headings, prices |

### Line Height

| Token | Value | Tailwind | Usage |
|-------|-------|----------|-------|
| `--line-height-tight` | `1.25` | `leading-tight` | Headings |
| `--line-height-normal` | `1.5` | `leading-normal` | Body text |
| `--line-height-relaxed` | `1.625` | `leading-relaxed` | Long-form content |

### Tracking

| Token | Value | Tailwind | Usage |
|-------|-------|----------|-------|
| `--ds-tracking-tight` | `-0.025em` | `tracking-tight` | Large headings |
| `--ds-tracking-normal` | `0em` | `tracking-normal` | Default |
| `--ds-tracking-wide` | `0.025em` | `tracking-wide` | Uppercase labels |

### Font Family

| Token | Value |
|-------|-------|
| `--font-family` | DM Sans, system-ui, -apple-system, sans-serif |

---

## Border Radius Tokens

### Primitives

| Token | Value | px | Tailwind |
|-------|-------|-----|----------|
| `--ds-radius-none` | `0` | 0 | `rounded-none` |
| `--ds-radius-sm` | `0.25rem` | 4 | `rounded` |
| `--ds-radius-md` | `0.375rem` | 6 | `rounded-md` |
| `--ds-radius-base` | `0.5rem` | 8 | — |
| `--ds-radius-lg` | `0.75rem` | 12 | `rounded-xl` |
| `--ds-radius-xl` | `1rem` | 16 | `rounded-2xl` |
| `--ds-radius-2xl` | `1.5rem` | 24 | `rounded-3xl` |
| `--ds-radius-full` | `9999px` | pill | `rounded-full` |

### Semantic Aliases

| Token | Use |
|-------|-----|
| `--radius-sm` | Subtle rounding (thumbnails) |
| `--radius-md` | Checkboxes, small elements |
| `--radius-base` | Default rounded elements |
| `--radius-lg` | Inputs, select items |
| `--radius-xl` | Cards |
| `--radius-2xl` | Large cards, hero sections |
| `--radius-pill` | Buttons, badges, pills |

### shadcn/ui `--radius` (0.75rem)

| Tailwind Class | Computed | Usage |
|---|---|---|
| `rounded-lg` | `var(--radius)` = 12px | Cards (shadcn) |
| `rounded-md` | `calc(var(--radius) - 2px)` = 10px | Medium elements |
| `rounded-sm` | `calc(var(--radius) - 4px)` = 8px | Small elements |

---

## Elevation Tokens

### Shadow

| Token | Value | Tailwind | Usage |
|-------|-------|----------|-------|
| `--shadow-none` | `0 0 #0000` | `shadow-none` | Reset |
| `--shadow-card` | `0 1px 2px rgb(0 0 0/0.05)` | `shadow-sm` | Default card |
| `--shadow-card-hover` | `0 4px 6px -1px rgb(0 0 0/0.1)...` | `shadow-md` | Card hover |
| `--shadow-dropdown` | same as md | `shadow-md` | Dropdown menus |
| `--shadow-elevated` | `0 10px 15px -3px rgb(0 0 0/0.1)...` | `shadow-lg` | Prominent hover |

### Z-Index

| Token | Value | Tailwind | Usage |
|-------|-------|----------|-------|
| `--z-base` | `0` | `z-0` | Default stacking |
| `--z-raised` | `10` | `z-10` | Floating elements |
| `--z-sticky` | `50` | `z-50` | Navbar, skip link, dropdowns |
| `--z-overlay` | `100` | — | Modal overlays |

---

## Motion Tokens

### Duration

| Token | Value | Tailwind | Usage |
|-------|-------|----------|-------|
| `--duration-fast` | `150ms` | `duration-150` | Micro-interactions |
| `--duration-normal` | `200ms` | `duration-200` | Color/shadow transitions |
| `--duration-slow` | `300ms` | `duration-300` | Layout, transform transitions |

### Easing

| Token | Value | Usage |
|-------|-------|-------|
| `--ease` | `cubic-bezier(0.4, 0, 0.2, 1)` | Default easing for all transitions |

---

## Component Sizing Tokens

### Icons

| Token | Value | Tailwind | Usage |
|-------|-------|----------|-------|
| `--size-icon-sm` | `0.75rem` (12px) | `h-3 w-3` | Dismiss/close icons |
| `--size-icon` | `1rem` (16px) | `h-4 w-4` | Inline icons, search, spinner |
| `--size-icon-md` | `1.25rem` (20px) | `h-5 w-5` | Nav icons, theme toggle |
| `--size-icon-lg` | `1.5rem` (24px) | `h-6 w-6` | Large standalone icons |

### Logo

| Token | Value | Context |
|-------|-------|---------|
| `--size-logo-sm` | `30px` | Footer |
| `--size-logo-md` | `40px` | Navbar |
| `--size-logo-lg` | `60px` | Hero/about |

### Controls

| Token | Value | Tailwind | Usage |
|-------|-------|----------|-------|
| `--size-control-sm` | `2.25rem` (36px) | `h-9` | Small selects |
| `--size-control` | `2.5rem` (40px) | `h-10` | Small buttons |
| `--size-control-md` | `2.75rem` (44px) | `h-11` | Default buttons/inputs |
| `--size-control-lg` | `3rem` (48px) | `h-12` | Large buttons |

### Max Widths

| Token | Value | Tailwind | Usage |
|-------|-------|----------|-------|
| `--max-width-content` | `80rem` (1280px) | `max-w-7xl` | Main content area |
| `--max-width-prose` | `48rem` (768px) | `max-w-3xl` | Blog posts, about |
| `--max-width-form` | `42rem` (672px) | `max-w-2xl` | Forms |

---

## Opacity Tokens

| Token | Value | Tailwind | Usage |
|-------|-------|----------|-------|
| `--ds-opacity-disabled` | `0.5` | `opacity-50` | Disabled controls |
| `--ds-opacity-muted` | `0.7` | `opacity-70` | Disabled labels |
| `--ds-opacity-hover` | `0.8` | `/80` suffix | Hover on filled badges |
| `--ds-opacity-soft` | `0.9` | `/90` suffix | Hover on primary button |
