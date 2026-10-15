# Badge

| Key | Value |
|-----|-------|
| **Category** | Data Display |
| **Status** | Stable |
| **File** | `components/ui/badge.tsx` |

## Overview

Compact label for categorization, status, or metadata.

**Use when:** Protection levels, seasons, materials, product categories, filter counts.
**Don't use when:** Actions (use Button), long text, navigation.

## Anatomy

```
[Badge]
  └─ content (text, optional emoji prefix)
```

## Tokens Used

| Property | Token / Class |
|----------|---------------|
| Radius | `rounded-full` (pill) |
| Padding | `px-3 py-1` (`size="default"`), `px-2 py-0.5` (`size="sm"`) |
| Font | `text-xs`, `font-semibold` |
| Transition | `transition-colors` |
| Focus | `ring-2 ring-ring ring-offset-2` |

## Props / API

| Prop | Type | Default |
|------|------|---------|
| `variant` | `"default" \| "secondary" \| "outline" \| "accent" \| "destructive" \| "positive" \| "negative"` | `"default"` |
| `size` | `"default" \| "sm"` | `"default"` |

### Sizes

| Size | Padding | Use |
|------|---------|-----|
| `default` | `px-3 py-1` | Detail pages, filters, overlays |
| `sm` | `px-2 py-0.5` | Dense rows. Product cards use `size="sm"` plus `sm:px-3 sm:py-1`, so the compact padding applies below 640px only |

Text stays `text-xs` in both sizes; never drop below it (no `text-[11px]`).

## Variants

| Variant | Background | Text | Hover |
|---------|------------|------|-------|
| `default` | `bg-primary` | `text-primary-foreground` | — |
| `secondary` | `bg-secondary` | `text-secondary-foreground` | — |
| `outline` | transparent, `border-border` | `text-foreground` | — |
| `accent` | `bg-primary/15` | `text-primary-text` | — |
| `destructive` | `bg-destructive` | `text-destructive-foreground` | — |
| `positive` | `bg-primary/15`, `border-primary/30` | `text-primary-text` | — |
| `negative` | `bg-destructive/10`, `border-destructive/30` | `text-destructive-text` | — |

### Protection scale (product card and detail)

Staff Pick is the only solid lime pill (`default`). Most and Highly protective use `positive`, Moderately protective uses `outline`, Slightly protective uses `secondary`, Not protective uses `negative`.

Below 640px the product card shows a short label (Most, High, Moderate, Slight) with `whitespace-nowrap` so the pill never wraps; the full label renders from `sm` up and always in an `sr-only` span.

### Vegan verification and waterproof

Same quiet scale, never solid red or lime. Verified Vegan by us / Confirmed Vegan by maker use `positive`, Verified Vegan by AI uses `outline`, Waiting for confirmation uses `secondary`. Waterproof uses `positive`, Water resistant `outline`, Not waterproof `secondary`. Verification badges carry no icon or emoji. Helpers: `veganVerifiedVariant`, `waterproofVariant` in `lib/utils.ts`. Base class includes `leading-4` so emoji badges (seasons) match the height of text-only badges.

## States

| State | Appearance |
|-------|------------|
| **Default** | Per variant |
| **Hover / focus** | None. Badges are static labels; wrap them in a link (with `.focus-ring`) when they need to be interactive |
| **Focus** | `ring-2 ring-ring ring-offset-2` |

## Code Example

```tsx
import { Badge } from "@/components/ui/badge"

<Badge>Staff Pick</Badge>
<Badge variant="outline">☀️ Summer</Badge>
<Badge variant="secondary">Not waterproof</Badge>
<Badge variant="positive">Verified Vegan by us</Badge>
```

## Cross-References

- [ProductCard](./product-card.md) — Badges display product specs
- [Button](./button.md) — Interactive counterpart
