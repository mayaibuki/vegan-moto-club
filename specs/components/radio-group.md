# RadioGroup

| Key | Value |
|-----|-------|
| **Category** | Forms |
| **Status** | Stable |
| **File** | `components/ui/radio-group.tsx` |

## Overview

Single-select option group. Built on Radix RadioGroup.

**Use when:** Choosing one option from a set (category filter, brand filter).
**Don't use when:** Multiple selections (use Checkbox), few options (use Select).

## Anatomy

```
[RadioGroup]                — grid, gap-2
  └─ [RadioGroupItem]       — h-5 w-5, rounded-full, border-2
       └─ [Indicator]       — flex center
            └─ [dot]        — h-2.5 w-2.5, rounded-full, bg-primary
```

## Tokens Used

| Property | Token / Class |
|----------|---------------|
| Size | `h-5 w-5` (20px) |
| Radius | `rounded-full` |
| Border | `border-2 border-input` |
| Checked border | `border-primary` |
| Indicator | `h-2.5 w-2.5 rounded-full bg-primary` |
| Focus ring | `ring-2 ring-ring ring-offset-2` |
| Transition | `transition-colors` |
| Disabled opacity | `opacity-50` |

## States

| State | Appearance |
|-------|------------|
| **Unselected** | `border-input`, no indicator |
| **Selected** | `border-primary` + `bg-primary` dot |
| **Focus** | `ring-2 ring-ring ring-offset-2` |
| **Disabled** | `opacity-50` |

## Code Example

```tsx
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Label } from "@/components/ui/label"

<RadioGroup value="all" onValueChange={setValue}>
  <div className="flex items-center space-x-3">
    <RadioGroupItem value="all" id="cat-all" />
    <Label htmlFor="cat-all">All Categories</Label>
  </div>
  <div className="flex items-center space-x-3">
    <RadioGroupItem value="gloves" id="cat-gloves" />
    <Label htmlFor="cat-gloves">Gloves</Label>
  </div>
</RadioGroup>
```

## Cross-References

- [Checkbox](./checkbox.md) — Multi-select alternative
- [Select](./select.md) — Dropdown alternative for many options
