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
[footer]                           — border-t, bg-card, mt-12
  └─ [container]                   — `.page-container` (max-w-7xl, px-4 sm:px-6), py-10
       ├─ [grid]                   — grid-cols-2 md:grid-cols-3, gap-x-6 gap-y-8 md:gap-10, mb-10
       │    ├─ [Brand]             — Logo (sm), name, tagline; col-span-2 on mobile, left-aligned
       │    ├─ [Nav]               — Products, Events, About
       │    └─ [Connect]           — Discord, Instagram (external)
       └─ [Copyright bar]          — border-t, pt-8, text-center
```

## Tokens Used

| Property | Token / Class |
|----------|---------------|
| Top border | `border-t border-border` |
| Background | `bg-card` |
| Top margin | `mt-12` |
| Padding | `.page-container py-10` (aligned with `<main>`) |
| Grid | `grid-cols-2 md:grid-cols-3`; brand block `col-span-2 md:col-span-1`, so Navigation and Connect sit side by side on mobile |
| Grid gap | `gap-x-6 gap-y-8 md:gap-10` |
| Section heading | `<h2>` with `text-sm font-semibold mb-2` |
| Link list | `text-sm`, no extra spacing |
| Link tap target | `inline-flex min-h-11 items-center` (44px rows) |
| Link hover | `hover:underline decoration-primary decoration-2 underline-offset-4` (text stays foreground) |
| Link focus | `.focus-ring` |
| Copyright | `text-sm text-muted-foreground`; year from `new Date().getFullYear()` |
| Divider | `border-t border-border pt-8` |
| Max width | `max-w-7xl` |

## Cross-References

- [Logo](./logo.md) — Rendered at sm size
- [Navbar](./navbar.md) — Top navigation counterpart
