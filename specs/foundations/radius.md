# Border Radius Foundation

## Overview

Vegan Moto Club uses a consistent border radius scale to create a soft, approachable visual style. The system is built around a central `--radius` variable (set to `0.75rem` / 12px) that shadcn/ui components use with `calc()` derivatives.

The token architecture provides both a primitive scale in `tokens.css` and the shadcn/ui `calc`-based system in `tailwind.config.ts`.

---

## Primitive Scale

| Token              | Value     | Size (px) | Tailwind Class   | Typical Use                          |
| ------------------ | --------- | --------- | ---------------- | ------------------------------------ |
| `--ds-radius-none` | `0`       | 0         | `rounded-none`   | No rounding (e.g., dividers)         |
| `--ds-radius-sm`   | `0.25rem` | 4px       | `rounded-sm`     | Badges, tags, small chips            |
| `--ds-radius-md`   | `0.375rem`| 6px       | `rounded-md`     | Inputs, small buttons, inline code   |
| `--ds-radius-base` | `0.5rem`  | 8px       | `rounded`        | Default element rounding             |
| `--ds-radius-lg`   | `0.75rem` | 12px      | `rounded-lg`     | Cards, dialogs, large buttons        |
| `--ds-radius-xl`   | `1rem`    | 16px      | `rounded-xl`     | Feature cards, hero sections         |
| `--ds-radius-2xl`  | `1.5rem`  | 24px      | `rounded-2xl`    | Marketing blocks, large panels       |
| `--ds-radius-full` | `9999px`  | pill      | `rounded-full`   | Avatars, pills, circular elements    |

---

## Semantic Aliases

| Alias           | Primitive           | Value     | Usage                             |
| --------------- | ------------------- | --------- | --------------------------------- |
| `--radius-sm`   | `--ds-radius-sm`    | 4px       | Badges, tags                      |
| `--radius-md`   | `--ds-radius-md`    | 6px       | Inputs, small interactive elements|
| `--radius-base` | `--ds-radius-base`  | 8px       | Default rounding                  |
| `--radius-lg`   | `--ds-radius-lg`    | 12px      | Cards, modals                     |
| `--radius-xl`   | `--ds-radius-xl`    | 16px      | Feature cards                     |
| `--radius-2xl`  | `--ds-radius-2xl`   | 24px      | Large promotional blocks          |
| `--radius-pill` | `--ds-radius-full`  | 9999px    | Pill shapes, avatars              |

---

## The shadcn/ui `--radius` Variable

shadcn/ui components use a single `--radius` CSS variable as the base, with `calc()` derivatives for smaller variants. This is defined in `globals.css`:

```css
:root {
  --radius: 0.75rem; /* 12px */
}
```

The `tailwind.config.ts` extends the border radius scale using this variable:

```ts
borderRadius: {
  lg: "var(--radius)",               // 12px (0.75rem)
  md: "calc(var(--radius) - 2px)",   // 10px (0.625rem)
  sm: "calc(var(--radius) - 4px)",   //  8px (0.5rem)
}
```

| Tailwind Class | Expression                     | Computed Value | Used By                          |
| -------------- | ------------------------------ | -------------- | -------------------------------- |
| `rounded-lg`   | `var(--radius)`                | 12px           | Cards, dialogs, large containers |
| `rounded-md`   | `calc(var(--radius) - 2px)`    | 10px           | Buttons, dropdowns, inputs       |
| `rounded-sm`   | `calc(var(--radius) - 4px)`    | 8px            | Badges, small interactive pieces |

Note: The shadcn `rounded-sm` (8px via calc) differs from the primitive `--ds-radius-sm` (4px). The shadcn scale is relatively larger because the base `--radius` is set to 12px. Both systems coexist; shadcn components use the calc-based scale, while custom components may reference the primitive tokens directly.

---

## Component Mapping

| Component            | Recommended Radius   | Tailwind Class   |
| -------------------- | -------------------- | ---------------- |
| Badge                | 4px                  | `rounded-sm` (primitive) or `rounded-full` for pills |
| Input / Select       | 10px (shadcn md)     | `rounded-md`     |
| Button (default)     | 10px (shadcn md)     | `rounded-md`     |
| Card                 | 12px (shadcn lg)     | `rounded-lg`     |
| Dialog / Sheet       | 12px (shadcn lg)     | `rounded-lg`     |
| Dropdown / Popover   | 10px (shadcn md)     | `rounded-md`     |
| Avatar               | pill                 | `rounded-full`   |
| Feature Card         | 16px                 | `rounded-xl`     |
| Image thumbnails     | 12px                 | `rounded-lg`     |
| Tooltip              | 10px                 | `rounded-md`     |

---

## Usage Examples

```html
<!-- Standard card -->
<div class="rounded-lg border bg-card p-6">
  Card content
</div>

<!-- Input field -->
<input class="rounded-md border border-input px-3 py-2" />

<!-- Pill badge -->
<span class="rounded-full bg-primary px-2.5 py-0.5 text-xs">
  Vegan
</span>

<!-- Feature section -->
<div class="rounded-xl bg-muted p-8">
  Featured content
</div>
```

---

## Rules

1. **Use the scale.** Never use arbitrary radius values like `rounded-[7px]`. Choose the nearest scale step.
2. **Match hierarchy.** Larger containers use larger radii. A card (`rounded-lg`) should have a visually larger radius than its inner badge (`rounded-sm` or `rounded-full`).
3. **Nested rounding.** When nesting rounded elements, the inner element should have a smaller radius than the outer. A card at `rounded-lg` (12px) with `p-4` (16px) padding should have inner elements at `rounded-md` (10px) or smaller.
4. **Consistency within component families.** All buttons use the same radius. All cards use the same radius. Do not vary radius for visual interest within a component type.
