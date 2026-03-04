# Checkbox

| Key | Value |
|-----|-------|
| **Category** | Forms |
| **Status** | Stable |
| **File** | `components/ui/checkbox.tsx` |

## Overview

Toggle control for multi-select options. Built on Radix Checkbox.

**Use when:** Multiple selections (gender filter, riding styles).
**Don't use when:** Single selection from a group (use RadioGroup), on/off toggle (use Switch).

## Anatomy

```
[Checkbox]
  └─ [Indicator]
       └─ [Check icon]  — h-3.5 w-3.5, stroke-[3]
```

## Tokens Used

| Property | Token / Class |
|----------|---------------|
| Size | `h-5 w-5` (20px) |
| Radius | `rounded-md` (6px) |
| Border | `border-2 border-input` |
| Background | `bg-background` |
| Checked bg | `bg-primary` |
| Checked border | `border-primary` |
| Checked text | `text-primary-foreground` |
| Focus ring | `ring-2 ring-ring ring-offset-2` |
| Transition | `transition-colors` |
| Disabled opacity | `opacity-50` |

## States

| State | Appearance |
|-------|------------|
| **Unchecked** | `border-input bg-background` |
| **Checked** | `bg-primary border-primary text-primary-foreground` + check icon |
| **Focus** | `ring-2 ring-ring ring-offset-2` |
| **Disabled** | `cursor-not-allowed opacity-50` |

## Code Example

```tsx
import { Checkbox } from "@/components/ui/checkbox"
import { Label } from "@/components/ui/label"

<div className="flex items-center space-x-3">
  <Checkbox id="gender-women" />
  <Label htmlFor="gender-women">Women</Label>
</div>
```

## Cross-References

- [RadioGroup](./radio-group.md) — Single-select alternative
- [Label](./label.md) — Always pair with a label
