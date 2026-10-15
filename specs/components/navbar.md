# Navbar

| Key | Value |
|-----|-------|
| **Category** | Navigation |
| **Status** | Stable |
| **File** | `components/Navbar.tsx` |
| **Rendering** | Client component (`"use client"`) |

## Overview

Sticky top navigation with logo, desktop nav links, theme toggle, and mobile menu.

**Use when:** Always present — rendered in root layout.

## Anatomy

```
[header]                          — sticky top-0, z-50, border-b
  ├─ [nav]                        — `.page-container` (max-w-7xl, px-4 sm:px-6), py-4
  │    ├─ [Logo]                  — size="md"
  │    ├─ [Desktop nav]           — hidden md:flex, gap-8
  │    │    ├─ [Link] × 4         — text-lg font-medium
  │    │    └─ [ThemeToggle]      — Button ghost, icon, rounded-full
  │    └─ [Mobile controls]       — flex md:hidden
  │         ├─ [ThemeToggle]
  │         └─ [MenuToggle]       — Button ghost, icon
  └─ [Mobile menu]                — md:hidden, conditional
       └─ [ul]                    — `.page-container`, py-4, space-y-1
            └─ [Link] × 4        — py-3, text-base font-medium
```

## Tokens Used

| Property | Token / Class |
|----------|---------------|
| Position | `sticky top-0` |
| Z-index | `z-50` (z-sticky) |
| Border | `border-b border-border/50` |
| Background | `bg-card/80 backdrop-blur-sm` |
| Max width | `max-w-7xl` |
| Padding | `.page-container py-4` (16px gutter on mobile, 24px from `sm`), aligned with `<main>` |
| Link gap | `gap-8` |
| Link style | `text-lg font-medium` |
| Link hover | `hover:underline decoration-primary decoration-2 underline-offset-8` (text stays foreground) |
| Current page | `aria-current="page"` with `aria-[current=page]:underline` (same lime underline) |
| Focus | `.focus-ring` |
| Transition | `transition-colors` |
| Icon size | `h-5 w-5` |
| Mobile bg | `bg-card` |
| Mobile border | `border-t border-border/50` |

## Behavior

- **Theme toggle:** Adds/removes `.dark` on `<html>`, persists to localStorage
- **Mobile menu:** Toggle shows/hides nav list; first link auto-focused on open; focus returns to toggle on close. When closed the menu is `inert` and `aria-hidden` (and `invisible` after the close transition) so Tab and screen readers skip it. Escape closes it and returns focus to the toggle. It is a labelled `<nav aria-label="Mobile navigation">`
- **Hydration safe:** Theme button only renders after `mounted` state

## Cross-References

- [Logo](./logo.md) — Rendered inside navbar
- [Button](./button.md) — Ghost buttons for theme/menu toggles
- [Footer](./footer.md) — Paired navigation element
