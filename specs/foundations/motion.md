# Motion / Transitions Foundation

## Overview

Vegan Moto Club uses subtle, functional motion to provide interaction feedback and smooth state changes. The system prioritizes fast, non-distracting transitions that feel responsive without being flashy.

All motion primitives are defined in `app/tokens.css` with semantic aliases for component usage.

---

## Duration Scale

| Token                 | Value  | Tailwind Class  | Usage                                       |
| --------------------- | ------ | --------------- | ------------------------------------------- |
| `--ds-duration-fast`  | 150ms  | `duration-150`  | Micro-interactions: color changes, opacity   |
| `--ds-duration-normal`| 200ms  | `duration-200`  | Standard transitions: hover states, focus    |
| `--ds-duration-slow`  | 300ms  | `duration-300`  | Layout transitions: accordion, slide, expand |

### Semantic Aliases

| Alias              | Primitive              | Value  | Usage                              |
| ------------------ | ---------------------- | ------ | ---------------------------------- |
| `--duration-fast`  | `--ds-duration-fast`   | 150ms  | Immediate feedback (color, opacity)|
| `--duration-normal`| `--ds-duration-normal` | 200ms  | Default transition duration        |
| `--duration-slow`  | `--ds-duration-slow`   | 300ms  | Spatial movement (position, size)  |

---

## Easing

| Token               | Value                           | Tailwind Class   | Description                     |
| -------------------- | ------------------------------ | ---------------- | ------------------------------- |
| `--ds-ease-default`  | `cubic-bezier(0.4, 0, 0.2, 1)` | `ease-in-out` (approx.) | Standard ease -- quick start, gentle finish |

The default easing curve `cubic-bezier(0.4, 0, 0.2, 1)` is Tailwind's built-in `ease-in-out` equivalent. It provides a natural-feeling transition that accelerates quickly and decelerates smoothly.

The semantic alias is:

```css
--ease: var(--ds-ease-default);
```

---

## Common Transition Patterns

### Color Transitions (fast / normal)

Use for hover, focus, and active state color changes. These should feel instant.

```html
<!-- Button hover color change -->
<button class="transition-colors duration-200">
  Submit
</button>

<!-- Link hover -->
<a class="transition-colors duration-150 hover:text-primary">
  View Details
</a>

<!-- Background color shift -->
<div class="transition-colors duration-200 hover:bg-muted">
  Clickable row
</div>
```

**Tailwind mapping:** `transition-colors` applies `transition-property: color, background-color, border-color, text-decoration-color, fill, stroke` with the specified duration.

### Shadow / Elevation Transitions (normal)

Use for hover lift effects on cards and interactive surfaces.

```html
<!-- Card hover lift -->
<div class="shadow-sm hover:shadow-md transition-shadow duration-200">
  Card content
</div>
```

**Tailwind mapping:** `transition-shadow` applies `transition-property: box-shadow`.

### Layout Transitions (slow)

Use for changes that involve size, position, or spatial movement. These need more time to feel natural.

```html
<!-- Accordion expand -->
<div class="transition-all duration-300">
  Expandable content
</div>

<!-- Mobile menu slide -->
<nav class="transition-transform duration-300">
  Menu items
</nav>

<!-- Width change -->
<div class="transition-all duration-300 w-64 hover:w-72">
  Expanding panel
</div>
```

**Tailwind mapping:** `transition-all` applies `transition-property: all`. Use `transition-transform` when only transform changes to avoid animating unintended properties.

### Opacity Transitions (fast)

Use for fade-in/fade-out effects on tooltips, overlays, and notifications.

```html
<!-- Tooltip appearance -->
<div class="opacity-0 group-hover:opacity-100 transition-opacity duration-150">
  Tooltip text
</div>

<!-- Overlay backdrop -->
<div class="opacity-0 data-[state=open]:opacity-100 transition-opacity duration-200">
  Backdrop
</div>
```

---

## Tailwind Transition Utilities Reference

| Utility               | Properties Transitioned                                                  | When to Use                |
| --------------------- | ------------------------------------------------------------------------ | -------------------------- |
| `transition-none`     | None                                                                     | Disable transitions        |
| `transition-colors`   | `color`, `background-color`, `border-color`, `fill`, `stroke`           | Hover/focus color changes  |
| `transition-opacity`  | `opacity`                                                                | Fade effects               |
| `transition-shadow`   | `box-shadow`                                                             | Elevation changes          |
| `transition-transform`| `transform`                                                              | Position/scale changes     |
| `transition-all`      | All properties                                                           | Multiple property changes  |

| Duration Utility | Value  | Pairing                        |
| ---------------- | ------ | ------------------------------ |
| `duration-150`   | 150ms  | `transition-colors`, `transition-opacity` |
| `duration-200`   | 200ms  | `transition-colors`, `transition-shadow`  |
| `duration-300`   | 300ms  | `transition-all`, `transition-transform`  |

---

## Opacity Tokens

The design system includes opacity primitives for disabled and muted states:

| Token                  | Value | Usage                               |
| ---------------------- | ----- | ----------------------------------- |
| `--ds-opacity-disabled`| 0.5   | Disabled buttons, inactive elements |
| `--ds-opacity-muted`   | 0.7   | De-emphasized content               |
| `--ds-opacity-hover`   | 0.8   | Hover dimming effect                |
| `--ds-opacity-soft`    | 0.9   | Subtle transparency                 |

```html
<!-- Disabled button -->
<button disabled class="opacity-50 cursor-not-allowed">
  Disabled
</button>
```

---

## Rules

1. **Always animate transitions.** Never change visual state (color, shadow, opacity) without a transition. Abrupt changes feel broken.
2. **Match duration to scope.** Color and opacity changes use fast/normal (150-200ms). Layout and position changes use slow (300ms). Mixing these durations looks inconsistent.
3. **Use specific transition properties.** Prefer `transition-colors` or `transition-shadow` over `transition-all` when possible. `transition-all` can cause unexpected animations on properties like `height` or `padding`.
4. **Respect `prefers-reduced-motion`.** Consider adding reduced motion support for users who prefer it:
   ```css
   @media (prefers-reduced-motion: reduce) {
     * {
       transition-duration: 0.01ms !important;
     }
   }
   ```
5. **No decorative animations.** Motion is purely functional -- providing feedback for user interactions. Avoid loading animations, bouncing elements, or continuous motion.
6. **One easing curve.** Use the default `cubic-bezier(0.4, 0, 0.2, 1)` for all transitions. Do not introduce custom easing curves without design review.
