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
| `--ds-stone-50`    | `0 0% 98%`          | `#fafafa`      | Page background (light), light foreground, inverse |
| `--ds-stone-100`   | `12 6.5% 97.5%`     | `#f9f8f8`      | Muted backgrounds (light) |
| `--ds-stone-200`   | `12 6.3% 93.8%`     | `#f0efee`      | Borders, secondary bg (light) |
| `--ds-stone-300`   | `12 5.4% 84%`       | `#d8d5d4`      | Chart fill, subtle UI     |
| `--ds-stone-400`   | `12 4.9% 64%`       | `#a8a19f`      | Muted text (dark mode)    |
| `--ds-stone-500`   | `12 6.5% 51.5%`     | `#8b7f7b`      | Form control border (`--input`), chart fill, not for text |
| `--ds-stone-600`   | `12 6.5% 44%`       | `#776c69`      | Muted text (light mode)   |
| `--ds-stone-700`   | `12 5% 24%`         | `#403b3a`      | Border (dark)             |
| `--ds-stone-800`   | `12 6.3% 18.8%`     | `#332e2d`      | Muted/secondary bg (dark) |
| `--ds-stone-850`   | `12 6.5% 17%`       | `#2e2a29`      | Popover bg (dark)         |
| `--ds-stone-875`   | `12 7.5% 14%`       | `#262221`      | Card bg (dark)            |
| `--ds-stone-900`   | `12 8.7% 11.8%`     | `#211d1b`      | Text (light)              |
| `--ds-stone-950`   | `12 8.3% 7.2%`      | `#141111`      | Background (dark mode)    |
| `--ds-white`       | `0 0% 100%`         | `#ffffff`      | Background (light mode)   |

### Lime (Brand / Accent)

| Token              | HSL Value            | Hex (approx.) | Usage Context              |
| ------------------ | -------------------- | -------------- | -------------------------- |
| `--ds-lime-200`    | `79.9 84.6% 80.2%`  | `#dbf7a2`      | Chart fill, soft accent    |
| `--ds-lime-300`    | `79.7 77.9% 69.7%`  | `#c6ee76`      | Chart secondary            |
| `--ds-lime-400`    | `79.1 64.5% 57.5%`  | `#acd94d`      | Accent (light), Primary (dark) |
| `--ds-lime-500`    | `77.9 54.4% 47.4%`  | `#93bb37`      | Primary (light), Accent (dark) |
| `--ds-lime-600`    | `77.2 61.3% 38.5%`  | `#7c9e26`      | Chart dark variant         |
| `--ds-lime-700`    | `77 67% 28%`        | `#5c7718`      | Text on tinted lime (light) |

### Status Colors

| Token              | HSL Value            | Hex (approx.) | Usage Context           |
| ------------------ | -------------------- | -------------- | ----------------------- |
| `--ds-red-light`   | `0 84.2% 60.2%`     | `#ef4444`      | Destructive (light)     |
| `--ds-red-dark`    | `0 62.8% 30.6%`     | `#7f1d1d`      | Destructive (dark)      |
| `--ds-red-400`     | `0 91% 71%`         | `#f87272`      | Text on tinted red (dark) |
| `--ds-red-600`     | `0 72% 45%`         | `#c52020`      | Text on tinted red (light) |
| `--ds-green-600`   | `142 71% 45%`       | `#21c45d`      | Success (light)         |
| `--ds-green-400`   | `142 69% 58%`       | `#4ade80`      | Success (dark)          |

---

## Semantic Role Mapping

These are the tokens consumed by shadcn/ui components via `globals.css` and the Tailwind config. `globals.css` holds no raw HSL values: every bridge variable (`--background`, `--card`, ...) is `var(--color-*)` pointing at a semantic alias in `tokens.css`, which is the single source for both modes. The values below are what those aliases resolve to.

| Role                     | CSS Variable              | Light Mode Value      | Dark Mode Value       |
| ------------------------ | ------------------------- | --------------------- | --------------------- |
| **Background**           | `--background`            | Stone-50 `0 0% 98%` | Stone-950 `12 8.3% 7.2%` |
| **Foreground**           | `--foreground`            | Stone-900 `12 8.7% 11.8%` | Stone-50 `0 0% 98%` |
| **Muted BG**             | `--muted`                 | Stone-100 `12 6.5% 97.5%` | Stone-800 `12 6.3% 18.8%` |
| **Muted Text**           | `--muted-foreground`      | Stone-600 `12 6.5% 44%` | Stone-400 `12 4.9% 64%` |
| **Primary**              | `--primary`               | Lime-500 `77.9 54.4% 47.4%` | Lime-400 `79.1 64.5% 57.5%` |
| **Primary Foreground**   | `--primary-foreground`    | Stone-950 `12 8.3% 7.2%` | Stone-950 `12 8.3% 7.2%` |
| **Secondary BG**         | `--secondary`             | Stone-200 `12 6.3% 93.8%` | Stone-800 `12 6.3% 18.8%` |
| **Secondary Foreground** | `--secondary-foreground`  | Stone-900 `12 8.7% 11.8%` | Stone-50 `0 0% 98%` |
| **Accent**               | `--accent`                | Lime-400 `79.1 64.5% 57.5%` | Lime-500 `77.9 54.4% 47.4%` |
| **Accent Foreground**    | `--accent-foreground`     | Stone-950 `12 8.3% 7.2%` | Stone-950 `12 8.3% 7.2%` |
| **Destructive**          | `--destructive`           | Red `0 84.2% 60.2%`  | Red (dark) `0 62.8% 30.6%` |
| **Destructive FG**       | `--destructive-foreground`| `0 0% 98%`           | `0 0% 98%`           |
| **Border**               | `--border`                | Stone-200 `12 6.3% 93.8%` | Stone-700 `12 5% 24%` |
| **Input**                | `--input`                 | Stone-500 `12 6.5% 51.5%` | Stone-500 `12 6.5% 51.5%` |
| **Ring**                 | `--ring`                  | Lime-500 `77.9 54.4% 47.4%` | Lime-400 `79.1 64.5% 57.5%` |
| **Card BG**              | `--card`                  | White `0 0% 100%`    | Stone-875 `12 7.5% 14%` |
| **Card Foreground**      | `--card-foreground`       | Stone-900 `12 8.7% 11.8%` | Stone-50 `0 0% 98%` |
| **Popover BG**           | `--popover`               | White `0 0% 100%`    | Stone-850 `12 6.5% 17%` |
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
| **Popover BG / Text** | `--color-popover-bg`, `--color-popover-text` | White / Stone-900 | Stone-850 / Stone-50 |
| **Secondary BG / Text** | `--color-secondary`, `--color-secondary-text` | Stone-200 / Stone-900 | Stone-800 / Stone-50 |
| **Success Foreground** | `--color-success-foreground` | White          | White              |
| **Destructive Text**  | `--color-destructive-text` | Stone-50 (text on destructive fill) | Stone-50 |
| **Primary Text**      | `--color-primary-text`   | Lime-700 (text on tinted lime) | Lime-400 |
| **Negative Text**     | `--color-negative-text`  | Red-600 (text on tinted red)   | Red-400  |

---

## Tailwind Class Mapping

| Tailwind Class       | Resolves To                  | Light Appearance | Dark Appearance |
| -------------------- | ---------------------------- | ---------------- | --------------- |
| `bg-background`      | `hsl(var(--background))`     | Off-white (Stone-50) | Near-black  |
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

### `muted-foreground`

The `--muted-foreground` token is Stone-600 in light mode and Stone-400 in dark mode, both chosen to clear WCAG AA for normal-sized text.

- Light mode: Stone-600 is approximately 4.87:1 on the Stone-50 page, 5.08:1 on White cards and 4.65:1 on Stone-100. Passes AA.
- Dark mode: Stone-400 (`#a8a19f`) on Stone-950 (`#141111`) is approximately 5.7:1. Passes AA.

Stone-500 (`#8b7f7b`) is only about 3.9:1 on white, so do not use it for text. It is reserved for the `--input` form control border (3:1 non-text contrast).

### Focus Indicators

- All interactive elements use `ring-ring` (Lime-500/400) as the focus indicator color.
- Focus rings provide sufficient contrast against both light and dark backgrounds.
