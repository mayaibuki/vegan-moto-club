# Footer

| Key | Value |
|-----|-------|
| **Category** | Navigation |
| **Status** | Stable |
| **File** | `components/Footer.tsx` |
| **Rendering** | Server component |

## Overview

Site-wide footer with brand info, navigation links, and social links.

## Anatomy

```
[footer]                           — border-t, bg-secondary/10, mt-12
  └─ [container]                   — max-w-7xl, px-6 py-10
       ├─ [3-column grid]          — md:grid-cols-3, gap-10, mb-10
       │    ├─ [Brand]             — Logo (sm), name, tagline
       │    ├─ [Nav]               — Products, Events, Blog, About
       │    └─ [Connect]           — Discord, Instagram (external)
       └─ [Copyright bar]          — border-t, pt-8, text-center
```

## Tokens Used

| Property | Token / Class |
|----------|---------------|
| Top border | `border-t border-border` |
| Background | `bg-secondary/10` |
| Top margin | `mt-12` |
| Padding | `px-6 py-10` |
| Grid gap | `gap-10` |
| Section heading | `font-bold mb-4 text-base` |
| Link list | `space-y-3 text-sm` |
| Link hover | `hover:text-primary transition-colors` |
| Copyright | `text-sm text-muted-foreground` |
| Divider | `border-t border-border pt-8` |
| Max width | `max-w-7xl` |

## Cross-References

- [Logo](./logo.md) — Rendered at sm size
- [Navbar](./navbar.md) — Top navigation counterpart
