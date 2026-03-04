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
  ├─ [nav]                        — max-w-7xl, px-6 py-4
  │    ├─ [Logo]                  — size="md"
  │    ├─ [Desktop nav]           — hidden md:flex, gap-8
  │    │    ├─ [Link] × 4         — text-lg font-medium
  │    │    └─ [ThemeToggle]      — Button ghost, icon, rounded-full
  │    └─ [Mobile controls]       — flex md:hidden
  │         ├─ [ThemeToggle]
  │         └─ [MenuToggle]       — Button ghost, icon
  └─ [Mobile menu]                — md:hidden, conditional
       └─ [ul]                    — px-6 py-4, space-y-1
            └─ [Link] × 4        — py-3, text-base font-medium
```

## Tokens Used

| Property | Token / Class |
|----------|---------------|
| Position | `sticky top-0` |
| Z-index | `z-50` (z-sticky) |
| Border | `border-b border-border/50` |
| Background | `bg-muted/80 backdrop-blur-sm` |
| Max width | `max-w-7xl` |
| Padding | `px-6 py-4` |
| Link gap | `gap-8` |
| Link style | `text-lg font-medium` |
| Link hover | `hover:text-primary` |
| Transition | `transition-colors` |
| Icon size | `h-5 w-5` |
| Mobile bg | `bg-background` |
| Mobile border | `border-t border-border/50` |

## Behavior

- **Theme toggle:** Adds/removes `.dark` on `<html>`, persists to localStorage
- **Mobile menu:** Toggle shows/hides nav list; first link auto-focused on open; focus returns to toggle on close
- **Hydration safe:** Theme button only renders after `mounted` state

## Cross-References

- [Logo](./logo.md) — Rendered inside navbar
- [Button](./button.md) — Ghost buttons for theme/menu toggles
- [Footer](./footer.md) — Paired navigation element
