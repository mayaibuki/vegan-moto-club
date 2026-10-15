# Card

| Key | Value |
|-----|-------|
| **Category** | Layout / Container |
| **Status** | Stable |
| **File** | `components/ui/card.tsx` |

## Overview

Container component for grouping related content. Provides visual boundary and elevation.

**Use when:** Product cards, event cards, form containers, content sections.
**Don't use when:** Simple text blocks, inline elements.

## Anatomy

```
[Card]                      — rounded-2xl, border, shadow-sm
  ├─ [CardHeader]           — p-7, space-y-2
  │    ├─ [CardTitle]       — text-2xl, font-semibold
  │    └─ [CardDescription] — text-sm, text-muted-foreground
  ├─ [CardContent]          — p-7, pt-0
  └─ [CardFooter]           — p-7, pt-0
```

## Tokens Used

| Property | Token / Class |
|----------|---------------|
| Background | `bg-card` → `hsl(var(--card))` |
| Text | `text-card-foreground` |
| Border | `border-border` |
| Radius | `rounded-2xl` (16px) |
| Shadow | `shadow-sm`; hover `shadow-md` only with `interactive` |
| Transition | `transition-[box-shadow,border-color] duration-200` (only with `interactive`) |
| Hover border | `hover:border-foreground/25` (only with `interactive`) |
| Padding | `p-7` (28px) for header/content/footer |

## Props / API

All sub-components accept standard HTML `div` props plus `className`. `Card` also takes `interactive?: boolean` (default `false`): set it only when the whole card is a link or button (ProductCard). Static cards (events, empty states, forms) do not react to hover.

| Sub-component | Default classes |
|---------------|-----------------|
| `Card` | `rounded-2xl border border-border bg-card text-card-foreground shadow-sm` |
| `CardHeader` | `flex flex-col space-y-2 p-7` |
| `CardTitle` | `text-2xl font-semibold leading-none` (not a heading recipe; no tracking) |
| `CardDescription` | `text-sm text-muted-foreground` |
| `CardContent` | `p-7 pt-0` |
| `CardFooter` | `flex items-center p-7 pt-0` |

## States

| State | Appearance |
|-------|------------|
| **Default** | `shadow-sm`, `border-border` |
| **Hover** | `interactive` cards only: `shadow-md` and `border-foreground/25`. Static cards have no hover |

## Code Example

```tsx
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"

<Card>
  <CardHeader>
    <CardTitle>Suggest a Product</CardTitle>
    <CardDescription>Share a link and we'll check it out.</CardDescription>
  </CardHeader>
  <CardContent>
    {/* Form content */}
  </CardContent>
</Card>
```

## Cross-References

- [ProductCard](./product-card.md) — Specialized card for products
- [EventCard](./event-card.md) — Specialized card for events
- [Badge](./badge.md) — Often used inside cards
- [Button](./button.md) — CTA buttons in card footer

## Motion

`interactive` cards lift on hover: `hover:-translate-y-0.5` with the `shadow-sm` to `shadow-md` step, `transition-[transform,box-shadow,border-color] duration-200`. Instant under reduced motion. See [motion](../foundations/motion.md#implemented-motion).
