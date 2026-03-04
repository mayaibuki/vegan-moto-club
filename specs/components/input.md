# Input

| Key | Value |
|-----|-------|
| **Category** | Forms |
| **Status** | Stable |
| **File** | `components/ui/input.tsx` |

## Overview

Single-line text input for forms and search.

**Use when:** Text entry, search, URL input.
**Don't use when:** Multi-line text (use textarea), selection (use Select).

## Anatomy

```
[Input]  — single <input> element, styled
```

## Tokens Used

| Property | Token / Class |
|----------|---------------|
| Height | `h-11` (44px) |
| Radius | `rounded-xl` (12px) |
| Border | `border-2 border-input` |
| Background | `bg-background` |
| Padding | `px-4 py-2.5` |
| Font | `text-sm` |
| Focus border | `border-primary` |
| Focus ring | `ring-2 ring-ring ring-offset-2` |
| Transition | `transition-colors` |
| Disabled opacity | `opacity-50` |

## Props / API

Standard HTML `<input>` props. Forwarded ref.

## States

| State | Appearance |
|-------|------------|
| **Default** | `border-input bg-background` |
| **Focus** | `border-primary ring-2 ring-ring ring-offset-2` |
| **Disabled** | `cursor-not-allowed opacity-50` |
| **With icon** | Add `pl-9` and position icon `absolute left-3` |

## Code Example

```tsx
import { Input } from "@/components/ui/input"

<Input type="text" placeholder="Search products..." />
<Input type="url" placeholder="https://example.com" disabled />
```

## Cross-References

- [Label](./label.md) — Always pair with a label
- [Button](./button.md) — Submit buttons alongside inputs
- [Select](./select.md) — Dropdown alternative
