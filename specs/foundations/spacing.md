# Spacing Foundation

## Overview

Vegan Moto Club uses a **4px base unit** spacing system. All spacing values are multiples of 4px (0.25rem), ensuring consistent visual rhythm across the interface.

Spacing tokens live in `app/tokens.css` as CSS custom properties in two layers:

1. **Primitive tokens** (`--ds-space-*`) -- the raw scale values.
2. **Semantic aliases** (`--space-*`) -- meaningful names for use in components.

Components should reference semantic aliases or Tailwind utility classes. Never use arbitrary pixel values.

---

## Primitive Scale

| Token            | rem       | px   | Tailwind Class | Typical Use Case                        |
| ---------------- | --------- | ---- | -------------- | --------------------------------------- |
| `--ds-space-0`   | `0rem`    | 0    | `p-0`, `m-0`   | Reset spacing                           |
| `--ds-space-0-5` | `0.125rem`| 2    | `p-0.5`        | Hairline gaps, border offsets           |
| `--ds-space-1`   | `0.25rem` | 4    | `p-1`, `gap-1` | Tight inner padding, icon-to-text gap   |
| `--ds-space-1-5` | `0.375rem`| 6    | `p-1.5`        | Badge padding, compact elements         |
| `--ds-space-2`   | `0.5rem`  | 8    | `p-2`, `gap-2` | Compact padding, small component gaps   |
| `--ds-space-2-5` | `0.625rem`| 10   | `p-2.5`        | Button vertical padding                 |
| `--ds-space-3`   | `0.75rem` | 12   | `p-3`, `gap-3` | Input padding, card internal spacing    |
| `--ds-space-4`   | `1rem`    | 16   | `p-4`, `gap-4` | Default component padding               |
| `--ds-space-5`   | `1.25rem` | 20   | `p-5`, `gap-5` | Generous component padding              |
| `--ds-space-6`   | `1.5rem`  | 24   | `p-6`, `gap-6` | Card padding, group spacing             |
| `--ds-space-7`   | `1.75rem` | 28   | `p-7`          | Extended card padding                   |
| `--ds-space-8`   | `2rem`    | 32   | `p-8`, `gap-8` | Section internal spacing                |
| `--ds-space-10`  | `2.5rem`  | 40   | `p-10`         | Large section padding                   |
| `--ds-space-12`  | `3rem`    | 48   | `p-12`         | Section dividers                        |
| `--ds-space-16`  | `4rem`    | 64   | `p-16`         | Page-level section spacing              |
| `--ds-space-20`  | `5rem`    | 80   | `p-20`         | Large page sections                     |
| `--ds-space-24`  | `6rem`    | 96   | `p-24`         | Hero section spacing                    |

---

## Semantic Spacing Aliases

These named tokens map to the primitive scale and carry intent. Components should prefer these over raw scale values.

| Alias        | Primitive      | Value     | Tailwind Equiv | Usage                                     |
| ------------ | -------------- | --------- | -------------- | ----------------------------------------- |
| `--space-xs` | `--ds-space-1` | 4px       | `gap-1`, `p-1` | Tight inner spacing, icon gaps            |
| `--space-sm` | `--ds-space-2` | 8px       | `gap-2`, `p-2` | Compact spacing, small component padding  |
| `--space-md` | `--ds-space-4` | 16px      | `gap-4`, `p-4` | Default component spacing                 |
| `--space-lg` | `--ds-space-6` | 24px      | `gap-6`, `p-6` | Generous spacing, card padding            |
| `--space-xl` | `--ds-space-8` | 32px      | `gap-8`, `p-8` | Section internal spacing                  |
| `--space-2xl`| `--ds-space-10`| 40px      | `gap-10`, `p-10` | Large section padding                   |
| `--space-3xl`| `--ds-space-16`| 64px      | `gap-16`, `p-16` | Page-level section spacing              |
| `--space-4xl`| `--ds-space-24`| 96px      | `gap-24`, `p-24` | Hero sections, major vertical rhythm    |

---

## Usage Patterns

### Inner Component Padding

Use `--space-xs` through `--space-sm` (4px-8px) for padding inside compact components.

```html
<!-- Badge -->
<span class="px-2 py-0.5">Badge</span>

<!-- Small button -->
<button class="px-3 py-1.5">Button SM</button>
```

### Component Gaps

Use `--space-sm` through `--space-md` (8px-16px) for spacing between elements within a component.

```html
<!-- Icon + label inside a button -->
<button class="flex items-center gap-2">
  <Icon />
  <span>Label</span>
</button>

<!-- Form field stack -->
<div class="flex flex-col gap-4">
  <Input />
  <Input />
</div>
```

### Group / Card Spacing

Use `--space-md` through `--space-lg` (16px-24px) for spacing between related groups or inside cards.

```html
<!-- Card padding -->
<div class="p-6">
  <h3>Title</h3>
  <p class="mt-2">Description</p>
</div>

<!-- Stacked cards -->
<div class="flex flex-col gap-6">
  <Card />
  <Card />
</div>
```

### Section Spacing

Use `--space-xl` through `--space-3xl` (32px-64px) for spacing between major page sections.

```html
<!-- Section separator -->
<section class="py-16">
  <h2>Products</h2>
  <div class="mt-8">
    <ProductGrid />
  </div>
</section>
```

### Page / Hero Spacing

Use `--space-3xl` through `--space-4xl` (64px-96px) for top-level page spacing and hero sections.

```html
<!-- Hero section -->
<section class="py-24">
  <h1>Vegan Moto Club</h1>
</section>
```

---

## Spacing in the Globals

The `globals.css` file also defines three legacy spacing custom properties:

```css
--spacing-sm: 0.75rem;   /* 12px */
--spacing-md: 1.25rem;   /* 20px */
--spacing-lg: 2rem;       /* 32px */
```

These are from the original theme setup. Prefer the `--space-*` semantic tokens from `tokens.css` for new work.

---

## Consistency Rules

1. **Always use scale values.** Never use arbitrary pixel values like `p-[13px]` or `gap-[7px]`. If a value is not in the scale, choose the nearest scale step.
2. **Use Tailwind utilities** (`p-4`, `gap-6`, `mt-8`) for all spacing. These map directly to the 4px base unit system.
3. **Prefer semantic aliases** (`--space-md`, `--space-lg`) when referencing spacing in CSS custom properties or component documentation.
4. **Maintain vertical rhythm.** Stack spacing should use consistent increments. Do not mix `gap-3` and `gap-5` between adjacent siblings at the same hierarchy level.
5. **Responsive spacing.** Use Tailwind responsive prefixes to adjust spacing at breakpoints (e.g., `py-8 md:py-16 lg:py-24`), always stepping through the scale.
