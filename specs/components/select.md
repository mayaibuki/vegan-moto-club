# Select

| Key | Value |
|-----|-------|
| **Category** | Forms |
| **Status** | Stable |
| **File** | `components/ui/select.tsx` |

## Overview

Dropdown for choosing a single value from a list. Built on Radix Select.

**Use when:** Rows per page, sort order, compact single-select.
**Don't use when:** Multiple selections, visible option list (use RadioGroup).

## Anatomy

```
[Select]
  ├─ [SelectTrigger]        — h-10, rounded-full, border
  │    ├─ [SelectValue]     — placeholder text
  │    └─ [ChevronDown]     — h-4 w-4, opacity-50
  └─ [SelectContent]        — rounded-xl, border, shadow-md
       ├─ [SelectLabel]     — py-1.5 pl-8 pr-2, font-semibold
       ├─ [SelectItem]      — rounded-lg, py-2 pl-8 pr-2
       │    └─ [ItemIndicator] — absolute left-2, h-3.5 w-3.5
       └─ [ScrollButtons]   — py-1, cursor-default
```

## Tokens Used

| Property | Token / Class |
|----------|---------------|
| Trigger height | `h-10` (40px) |
| Trigger radius | `rounded-full` |
| Trigger border | `border border-input` |
| Trigger bg | `bg-background` |
| Content radius | `rounded-xl` |
| Content shadow | `shadow-md` |
| Content bg | `bg-popover` |
| Content text | `text-popover-foreground` |
| Content z-index | `z-50` |
| Item radius | `rounded-lg` |
| Item focus | `bg-accent` |
| Animation | `animate-in fade-in-0 zoom-in-95 slide-in-from-top-2` |

## Code Example

```tsx
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

<Select value="25" onValueChange={setRows}>
  <SelectTrigger className="w-20 h-9">
    <SelectValue />
  </SelectTrigger>
  <SelectContent>
    <SelectItem value="25">25</SelectItem>
    <SelectItem value="50">50</SelectItem>
    <SelectItem value="100">100</SelectItem>
  </SelectContent>
</Select>
```

## Cross-References

- [RadioGroup](./radio-group.md) — Visible single-select alternative
- [Input](./input.md) — Text entry counterpart
