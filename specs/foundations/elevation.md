# Elevation / Shadow Foundation

## Overview

Vegan Moto Club uses a minimal elevation system built on box shadows and z-index layers. Shadows provide subtle depth cues, while z-index values establish layering for overlapping UI elements.

All primitive values are defined in `app/tokens.css` with semantic aliases for component-level usage.

---

## Shadow Scale

### Primitive Tokens

| Token            | CSS Value                                                                 | Visual Effect           |
| ---------------- | ------------------------------------------------------------------------- | ----------------------- |
| `--ds-shadow-none` | `0 0 #0000`                                                            | No shadow               |
| `--ds-shadow-sm`   | `0 1px 2px 0 rgb(0 0 0 / 0.05)`                                       | Subtle lift, barely visible |
| `--ds-shadow-md`   | `0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)`  | Moderate depth, floating |
| `--ds-shadow-lg`   | `0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)` | Strong elevation, prominent |

### Tailwind Equivalents

| Token            | Tailwind Class | Tailwind CSS Value (matches)               |
| ---------------- | -------------- | ------------------------------------------- |
| `--ds-shadow-none` | `shadow-none` | `0 0 #0000`                                |
| `--ds-shadow-sm`   | `shadow-sm`   | `0 1px 2px 0 rgb(0 0 0 / 0.05)`           |
| `--ds-shadow-md`   | `shadow-md`   | `0 4px 6px -1px rgb(0 0 0 / 0.1), ...`    |
| `--ds-shadow-lg`   | `shadow-lg`   | `0 10px 15px -3px rgb(0 0 0 / 0.1), ...`  |

---

## Semantic Shadow Mapping

These aliases carry component-level intent and are the tokens components should reference.

| Alias                | Primitive          | Tailwind Class | Usage                              |
| -------------------- | ------------------ | -------------- | ---------------------------------- |
| `--shadow-none`      | `--ds-shadow-none` | `shadow-none`  | Flat elements, no elevation        |
| `--shadow-card`      | `--ds-shadow-sm`   | `shadow-sm`    | Cards at rest                      |
| `--shadow-card-hover`| `--ds-shadow-md`   | `shadow-md`    | Cards on hover (lifted state)      |
| `--shadow-dropdown`  | `--ds-shadow-md`   | `shadow-md`    | Dropdown menus, popovers, tooltips |
| `--shadow-elevated`  | `--ds-shadow-lg`   | `shadow-lg`    | Modals, dialogs, floating panels   |

### Component Examples

```html
<!-- Card with hover lift -->
<div class="shadow-sm hover:shadow-md transition-shadow duration-200">
  Card content
</div>

<!-- Dropdown menu -->
<div class="shadow-md rounded-md border bg-popover">
  Menu items
</div>

<!-- Modal dialog -->
<div class="shadow-lg rounded-lg border bg-card">
  Dialog content
</div>
```

---

## Z-Index Layers

### Primitive Tokens

| Token            | Value | Tailwind Class | Description                           |
| ---------------- | ----- | -------------- | ------------------------------------- |
| `--ds-z-base`    | `0`   | `z-0`          | Default document flow                 |
| `--ds-z-raised`  | `10`  | `z-10`         | Raised elements above siblings        |
| `--ds-z-sticky`  | `50`  | `z-50`         | Sticky headers, fixed navigation      |
| `--ds-z-overlay` | `100` | `z-[100]`      | Overlays, modals, backdrop            |

### Semantic Aliases

| Alias          | Primitive          | Value | Usage                              |
| -------------- | ------------------ | ----- | ---------------------------------- |
| `--z-base`     | `--ds-z-base`      | 0     | Default stacking context           |
| `--z-raised`   | `--ds-z-raised`    | 10    | Tooltips, floating badges, dropdowns |
| `--z-sticky`   | `--ds-z-sticky`    | 50    | Navbar, sticky table headers       |
| `--z-overlay`  | `--ds-z-overlay`   | 100   | Modal backdrop, sheet overlay      |

### Layer Hierarchy

```
z-100  ██████████████████████████  Overlay (modals, sheets, backdrop)
z-50   ████████████████████        Sticky (navbar, fixed elements)
z-10   ████████████                Raised (dropdowns, tooltips)
z-0    ████████                    Base (default document flow)
```

---

## Usage Guidelines

### Shadows

1. **Use shadows sparingly.** The design favors flat UI with border-based separation. Shadows are for interactive lift effects and floating elements.
2. **Cards use `shadow-sm` at rest.** On hover, transition to `shadow-md` with `transition-shadow duration-200` for a subtle lift effect.
3. **Floating elements use `shadow-md`.** Dropdowns, popovers, and tooltips should feel like they float above the surface.
4. **Modals use `shadow-lg`.** Dialogs and sheets need the strongest elevation to separate them from the page.
5. **Dark mode consideration.** Shadows are less visible on dark backgrounds. The border-based design ensures elements remain visually distinct regardless of mode.

### Z-Index

1. **Use only the defined layers.** Never use arbitrary z-index values like `z-[999]` or `z-[50000]`. The four-tier system is sufficient for all UI patterns.
2. **The navbar is `z-sticky` (50).** All content scrolls behind it.
3. **Modals and sheets are `z-overlay` (100).** They stack above everything including the navbar.
4. **Dropdowns are `z-raised` (10).** They float above sibling content but below sticky elements.
5. **Create new stacking contexts carefully.** Elements with `position: relative` and a z-index create new stacking contexts. Keep the hierarchy flat where possible.

### Transition Patterns

Shadow transitions should always be animated for smooth interaction feedback:

```html
<!-- Hover lift pattern -->
<div class="shadow-sm hover:shadow-md transition-shadow duration-200">
  ...
</div>

<!-- Focus elevation -->
<button class="shadow-none focus:shadow-md transition-shadow duration-150">
  ...
</button>
```
