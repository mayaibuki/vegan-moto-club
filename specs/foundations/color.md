# Color Foundation

## Overview

Vegan Moto Club uses a **Stone base palette** for neutrals and a **Lime accent palette** for brand identity. The color system supports both light and dark modes, toggled via the `.dark` class on the `<html>` element.

All colors are defined as HSL triplets (without the `hsl()` wrapper) in CSS custom properties. Tailwind consumes them via `hsl(var(--token))`, enabling opacity modifiers like `bg-primary/80`.

The token architecture has three layers:

1. **Primitive tokens** (`--ds-stone-*`, `--ds-lime-*`) -- raw palette values, never referenced by components directly.
2. **Semantic aliases** (`--color-*`) -- meaningful names that map to primitives, with light/dark variants.
3. **shadcn/ui tokens** (`--background`, `--primary`, etc.) -- consumed by Tailwind config and shadcn components.

---

## Primitive Palette

### Stone (Neutrals)

| Token              | HSL Value            | Hex (approx.) | Usage Context             |
| ------------------ | -------------------- | -------------- | ------------------------- |
| `--ds-stone-50`    | `0 0% 98%`          | `#fafafa`      | Light foreground, inverse |
| `--ds-stone-100`   | `12 6.5% 97.5%`     | `#f9f8f7`      | Muted backgrounds (light) |
| `--ds-stone-200`   | `12 6.3% 93.8%`     | `#efedeb`      | Borders, inputs (light)   |
| `--ds-stone-300`   | `12 5.4% 84%`       | `#d7d4d1`      | Chart fill, subtle UI     |
| `--ds-stone-400`   | `12 4.9% 64%`       | `#a5a09c`      | Muted text (dark mode)    |
| `--ds-stone-500`   | `12 6.5% 51.5%`     | `#8b8380`      | Muted text (light mode)   |
| `--ds-stone-800`   | `12 6.3% 18.8%`     | `#322f2d`      | Muted/secondary bg (dark) |
| `--ds-stone-900`   | `12 8.7% 11.8%`     | `#211f1d`      | Card bg (dark), text (light) |
| `--ds-stone-950`   | `12 8.3% 7.2%`      | `#141311`      | Background (dark mode)    |
| `--ds-white`       | `0 0% 100%`         | `#ffffff`      | Background (light mode)   |

### Lime (Brand / Accent)

| Token              | HSL Value            | Hex (approx.) | Usage Context              |
| ------------------ | -------------------- | -------------- | -------------------------- |
| `--ds-lime-200`    | `79.9 84.6% 80.2%`  | `#d9f99d`      | Chart fill, soft accent    |
| `--ds-lime-300`    | `79.7 77.9% 69.7%`  | `#bef264`      | Chart secondary            |
| `--ds-lime-400`    | `79.1 64.5% 57.5%`  | `#a3e635`      | Accent (light), Primary (dark) |
| `--ds-lime-500`    | `77.9 54.4% 47.4%`  | `#84cc16`      | Primary (light), Accent (dark) |
| `--ds-lime-600`    | `77.2 61.3% 38.5%`  | `#65a30d`      | Chart dark variant         |

### Status Colors

| Token              | HSL Value            | Hex (approx.) | Usage Context           |
| ------------------ | -------------------- | -------------- | ----------------------- |
| `--ds-red-light`   | `0 84.2% 60.2%`     | `#ef4444`      | Destructive (light)     |
| `--ds-red-dark`    | `0 62.8% 30.6%`     | `#7f1d1d`      | Destructive (dark)      |
| `--ds-green-600`   | `142 71% 45%`       | `#16a34a`      | Success (light)         |
| `--ds-green-400`   | `142 69% 58%`       | `#4ade80`      | Success (dark)          |

---

## Semantic Role Mapping

These are the tokens consumed by shadcn/ui components via `globals.css` and the Tailwind config.

| Role                     | CSS Variable              | Light Mode Value      | Dark Mode Value       |
| ------------------------ | ------------------------- | --------------------- | --------------------- |
| **Background**           | `--background`            | White `0 0% 100%`    | Stone-950 `12 8.3% 7.2%` |
| **Foreground**           | `--foreground`            | Stone-900 `12 8.7% 11.8%` | Stone-50 `0 0% 98%` |
| **Muted BG**             | `--muted`                 | Stone-100 `12 6.5% 97.5%` | Stone-800 `12 6.3% 18.8%` |
| **Muted Text**           | `--muted-foreground`      | Stone-500 `12 6.5% 51.5%` | Stone-400 `12 4.9% 64%` |
| **Primary**              | `--primary`               | Lime-500 `77.9 54.4% 47.4%` | Lime-400 `79.1 64.5% 57.5%` |
| **Primary Foreground**   | `--primary-foreground`    | Stone-950 `12 8.3% 7.2%` | Stone-950 `12 8.3% 7.2%` |
| **Secondary BG**         | `--secondary`             | Stone-100 `12 6.5% 97.5%` | Stone-800 `12 6.3% 18.8%` |
| **Secondary Foreground** | `--secondary-foreground`  | Stone-900 `12 8.7% 11.8%` | Stone-50 `0 0% 98%` |
| **Accent**               | `--accent`                | Lime-400 `79.1 64.5% 57.5%` | Lime-500 `77.9 54.4% 47.4%` |
| **Accent Foreground**    | `--accent-foreground`     | Stone-950 `12 8.3% 7.2%` | Stone-950 `12 8.3% 7.2%` |
| **Destructive**          | `--destructive`           | Red `0 84.2% 60.2%`  | Red (dark) `0 62.8% 30.6%` |
| **Destructive FG**       | `--destructive-foreground`| `0 0% 98%`           | `0 0% 98%`           |
| **Border**               | `--border`                | Stone-200 `12 6.3% 93.8%` | Stone-800 `12 6.3% 18.8%` |
| **Input**                | `--input`                 | Stone-200 `12 6.3% 93.8%` | Stone-800 `12 6.3% 18.8%` |
| **Ring**                 | `--ring`                  | Lime-500 `77.9 54.4% 47.4%` | Lime-400 `79.1 64.5% 57.5%` |
| **Card BG**              | `--card`                  | White `0 0% 100%`    | Stone-900 `12 8.7% 11.8%` |
| **Card Foreground**      | `--card-foreground`       | Stone-900 `12 8.7% 11.8%` | Stone-50 `0 0% 98%` |
| **Popover BG**           | `--popover`               | White `0 0% 100%`    | Stone-900 `12 8.7% 11.8%` |
| **Popover Foreground**   | `--popover-foreground`    | Stone-900 `12 8.7% 11.8%` | Stone-50 `0 0% 98%` |

### Extended Semantic Tokens (from `tokens.css`)

| Role                  | CSS Variable             | Light Mode         | Dark Mode          |
| --------------------- | ------------------------ | ------------------ | ------------------ |
| **Success**           | `--color-success`        | Green-600          | Green-400          |
| **BG Subtle**         | `--color-bg-subtle`      | Stone-100          | Stone-800          |
| **BG Inverse**        | `--color-bg-inverse`     | Stone-950          | White              |
| **Text Inverse**      | `--color-text-inverse`   | Stone-50           | Stone-900          |
| **Text on Primary**   | `--color-text-on-primary`| Stone-950          | Stone-950          |
| **Primary Hover**     | `--color-primary-hover`  | Lime-400           | Lime-500           |

---

## Tailwind Class Mapping

| Tailwind Class       | Resolves To                  | Light Appearance | Dark Appearance |
| -------------------- | ---------------------------- | ---------------- | --------------- |
| `bg-background`      | `hsl(var(--background))`     | White            | Near-black      |
| `text-foreground`    | `hsl(var(--foreground))`     | Dark stone       | Near-white      |
| `bg-primary`         | `hsl(var(--primary))`        | Lime-500 green   | Lime-400 green  |
| `text-primary`       | `hsl(var(--primary))`        | Lime-500 green   | Lime-400 green  |
| `bg-secondary`       | `hsl(var(--secondary))`      | Light stone      | Dark stone      |
| `bg-muted`           | `hsl(var(--muted))`          | Off-white stone  | Dark stone      |
| `text-muted-foreground` | `hsl(var(--muted-foreground))` | Medium stone | Light stone  |
| `bg-accent`          | `hsl(var(--accent))`         | Lime-400         | Lime-500        |
| `bg-destructive`     | `hsl(var(--destructive))`    | Bright red       | Dark red        |
| `border-border`      | `hsl(var(--border))`         | Light stone      | Dark stone      |
| `bg-card`            | `hsl(var(--card))`           | White            | Dark stone      |
| `ring-ring`          | `hsl(var(--ring))`           | Lime-500         | Lime-400        |

### Opacity Modifier Example

```html
<!-- 80% opacity primary background -->
<div class="bg-primary/80">...</div>

<!-- 50% opacity border -->
<div class="border border-border/50">...</div>
```

---

## Usage Guidelines

### When to Use Each Semantic Color

| Purpose                          | Token to Use           | Tailwind Class              |
| -------------------------------- | ---------------------- | --------------------------- |
| Page background                  | `--background`         | `bg-background`             |
| Default body text                | `--foreground`         | `text-foreground`           |
| Secondary/helper text            | `--muted-foreground`   | `text-muted-foreground`     |
| Primary CTA buttons              | `--primary`            | `bg-primary text-primary-foreground` |
| Secondary buttons                | `--secondary`          | `bg-secondary text-secondary-foreground` |
| Hover highlights, tags           | `--accent`             | `bg-accent text-accent-foreground` |
| Cards, dialogs                   | `--card`               | `bg-card text-card-foreground` |
| Popovers, dropdowns              | `--popover`            | `bg-popover text-popover-foreground` |
| Subtle backgrounds (sections)    | `--muted`              | `bg-muted`                  |
| Default borders                  | `--border`             | `border-border`             |
| Form input borders               | `--input`              | `border-input`              |
| Focus rings                      | `--ring`               | `ring-ring`                 |
| Error states, delete actions     | `--destructive`        | `bg-destructive text-destructive-foreground` |
| Success indicators               | `--color-success`      | Use `hsl(var(--color-success))` inline |

### Rules

- **Never use raw palette values** (e.g., `bg-lime-500`) in components. Always use semantic tokens.
- **Always pair background + foreground** tokens to maintain contrast (e.g., `bg-primary` with `text-primary-foreground`).
- The primary/accent colors **swap** between light and dark modes to maintain optimal contrast. Do not hardcode a single lime shade.

---

## Accessibility

### Contrast Requirements

- All text must meet **WCAG 2.1 AA** minimum contrast ratios:
  - **Normal text** (< 18px): 4.5:1 contrast ratio
  - **Large text** (>= 18px bold or >= 24px): 3:1 contrast ratio
  - **UI components and graphics**: 3:1 contrast ratio

### Known Issue: `muted-foreground`

The `--muted-foreground` token (Stone-500 in light mode, Stone-400 in dark mode) is **near the WCAG AA threshold** for normal-sized text on default backgrounds.

- Light mode: Stone-500 (`#8b8380`) on White (`#ffffff`) = approximately 3.9:1 -- **below 4.5:1 for normal text**.
- Dark mode: Stone-400 (`#a5a09c`) on Stone-950 (`#141311`) = approximately 5.7:1 -- passes AA.

**Recommendations:**

- Use `text-muted-foreground` only for **large text** (18px+ bold or 24px+) or **non-essential** secondary information.
- For smaller helper text that must be accessible, prefer `text-foreground` or a custom intermediate shade.
- This is tracked as a remaining TODO in the project audit log.

### Focus Indicators

- All interactive elements use `ring-ring` (Lime-500/400) as the focus indicator color.
- Focus rings provide sufficient contrast against both light and dark backgrounds.
