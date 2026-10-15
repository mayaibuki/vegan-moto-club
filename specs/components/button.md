# Button

| Key | Value |
|-----|-------|
| **Category** | Primitives / Actions |
| **Status** | Stable |
| **File** | `components/ui/button.tsx` |

## Overview

Primary interactive element for user actions. Uses Radix `Slot` for `asChild` composition.

**Use when:** Triggering actions, navigation CTAs, form submission.
**Don't use when:** Inline text navigation (use Link), toggling state (use Checkbox/Switch).

## Anatomy

```
[Button]
  └─ content (text, icon, or both)
```

## Tokens Used

| Property | Token / Class |
|----------|---------------|
| Background (default) | `bg-primary` |
| Text (default) | `text-primary-foreground` |
| Background (outline) | `bg-card`, hover: `bg-muted` (text stays `text-foreground`) |
| Border (outline) | 1px `border border-border` (same weight as inputs and selects) |
| Background (ghost) | hover: `bg-muted` (stone fill, not lime) |
| Shadow | `shadow-sm`, hover: `shadow-md` |
| Radius | `rounded-full` (pill shape) |
| Ring | `ring-ring`, `ring-offset-background` |
| Font | `text-sm`, `font-medium` |
| Transition | `transition-[background-color,border-color,color,box-shadow,transform]`, `duration-200` |
| Link press | `active:scale-100` (text links do not shrink) |
| Disabled opacity | `opacity-50` |

## Props / API

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `variant` | `"default" \| "destructive" \| "outline" \| "secondary" \| "ghost" \| "link"` | `"default"` | Visual style |
| `size` | `"default" \| "xs" \| "sm" \| "lg" \| "icon"` | `"default"` | Size preset |
| `asChild` | `boolean` | `false` | Render as child element (e.g., `<Link>`) |

## Sizes

| Size | Height | Padding | Font |
|------|--------|---------|------|
| `xs` | `h-8` (32px), `max-sm:h-11` (44px below 640px) | `px-3` | `text-xs` |
| `sm` | `h-10` (40px) | `px-5` | `text-sm` |
| `default` | `h-11` (44px) | `px-6 py-2.5` | `text-sm` |
| `lg` | `h-12` (48px) | `px-8` | `text-base` |
| `icon` | `h-11 w-11` | — | — |

Touch targets: anything tapped on mobile is at least 44px tall. `xs` grows to 44px below 640px; pagination buttons use `default` (44px), not `sm`.

## States

| State | Appearance |
|-------|------------|
| **Default** | `bg-primary text-primary-foreground shadow-sm` |
| **Hover** | `bg-primary/90 shadow-md` |
| **Focus** | `ring-2 ring-ring ring-offset-2` |
| **Disabled** | `opacity-50 pointer-events-none` |
| **Active/Pressed** | `active:scale-[0.96]` on top of the hover appearance |

## Code Example

```tsx
import { Button } from "@/components/ui/button"

<Button>Default Action</Button>
<Button variant="outline" size="lg">Browse Products</Button>
<Button variant="ghost" size="icon"><Sun className="h-5 w-5" /></Button>
<Button asChild><Link href="/products">View All</Link></Button>
```

## Cross-References

- [Badge](./badge.md) — Non-interactive variant of pill-shaped element
- [Input](./input.md) — Often paired in forms
- [Card](./card.md) — CTA buttons inside cards
