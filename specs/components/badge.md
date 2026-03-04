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
| Padding | `px-3 py-1` |
| Font | `text-xs`, `font-semibold` |
| Transition | `transition-colors` |
| Focus | `ring-2 ring-ring ring-offset-2` |

## Props / API

| Prop | Type | Default |
|------|------|---------|
| `variant` | `"default" \| "secondary" \| "outline" \| "accent" \| "destructive"` | `"default"` |

## Variants

| Variant | Background | Text | Hover |
|---------|------------|------|-------|
| `default` | `bg-primary` | `text-primary-foreground` | `bg-primary/80` |
| `secondary` | `bg-secondary` | `text-secondary-foreground` | `bg-secondary/80` |
| `outline` | transparent | `text-foreground` | — |
| `accent` | `bg-accent/20` | `text-accent-foreground` | `bg-accent/30` |
| `destructive` | `bg-destructive` | `text-destructive-foreground` | `bg-destructive/80` |

## States

| State | Appearance |
|-------|------------|
| **Default** | Per variant |
| **Hover** | Opacity shift (see variants) |
| **Focus** | `ring-2 ring-ring ring-offset-2` |

## Code Example

```tsx
import { Badge } from "@/components/ui/badge"

<Badge>Staff Pick</Badge>
<Badge variant="outline">☀️ Summer</Badge>
<Badge variant="destructive">Not waterproof</Badge>
<Badge variant="accent">Verified Vegan</Badge>
```

## Cross-References

- [ProductCard](./product-card.md) — Badges display product specs
- [Button](./button.md) — Interactive counterpart
