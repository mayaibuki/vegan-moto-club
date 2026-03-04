# ProductGrid

| Key        | Value                                  |
|------------|----------------------------------------|
| File       | `components/ProductGrid.tsx`           |
| Type       | Client component (`"use client"`)      |
| Imports    | Input, Button, Badge, Select, Checkbox, RadioGroup, Label, ProductCard |
| Data       | `Product[]` from server component      |

## Overview

The main product listing interface. Combines a sidebar filter panel (search, category, gender, riding style, brand) with a responsive product grid and pagination. The only client component responsible for filtering and pagination logic — all data arrives server-side and is filtered in-browser via `useMemo`.

## Anatomy

```
<div>                                   ← root wrapper
  <div>                                 ← flex container (col on mobile, row on lg)
    <aside>                             ← sidebar filters (sticky, collapsible on mobile)
      <div role="search">              ← search input with icon
      <fieldset>                        ← category radio group
      <fieldset>                        ← gender checkboxes
      <fieldset>                        ← riding style checkboxes
      <fieldset>                        ← brand radio group (scrollable)
      <Button>                          ← clear all filters (conditional)
    </aside>
    <section>                           ← main content area
      <div>                             ← results count + mobile filter toggle
      <div>                             ← active filter badges (conditional)
      <div>                             ← product grid (2/3/4 columns responsive)
        <ProductCard /> ...
      </div>
      <nav>                             ← pagination controls
        <Select>                        ← rows per page (25/50/100)
        <Button> Previous </Button>
        <Button> Next </Button>
      </nav>
    </section>
  </div>
</div>
```

## Tokens Used

| Element              | Token / Class                | Purpose               |
|----------------------|------------------------------|-----------------------|
| Sidebar bg (mobile)  | `bg-background`              | Base background       |
| Filter labels        | `text-foreground`            | Primary text          |
| Filter option labels | `text-sm font-medium`        | Form labels           |
| Muted text           | `text-muted-foreground`      | Counts, descriptions  |
| Dividers             | `border-border`              | Section separators    |
| Sidebar border       | `border-border` (mobile)     | Panel outline         |
| Empty state bg       | `bg-muted/30`                | Subtle background     |
| Grid gaps            | `gap-6`                      | Card spacing          |
| Sidebar gap          | `gap-8`                      | Section spacing       |
| Pagination border    | `border-border`              | Top divider           |
| Filter badge remove  | `hover:text-foreground`      | Interactive feedback  |

## Props

| Prop       | Type        | Required | Description                        |
|------------|-------------|----------|------------------------------------|
| `products` | `Product[]` | Yes      | Full product array from server     |

## State Management

| State                  | Type             | Purpose                           |
|------------------------|------------------|-----------------------------------|
| `search`               | `string`         | Text search query                 |
| `selectedBrand`        | `string \| null` | Active brand filter               |
| `selectedCategory`     | `string \| null` | Active category filter            |
| `selectedGenders`      | `string[]`       | Active gender filters (multi)     |
| `selectedRidingStyles` | `string[]`       | Active riding style filters       |
| `showFilters`          | `boolean`        | Mobile sidebar visibility         |
| `currentPage`          | `number`         | Current pagination page           |
| `rowsPerPage`          | `number`         | Items per page (25/50/100)        |

## Responsive Behavior

| Breakpoint | Behavior                                       |
|------------|-------------------------------------------------|
| < lg       | Filters hidden (toggle button visible), 2-col grid |
| md         | 3-column product grid                          |
| lg+        | Sidebar visible (w-64, sticky), 4-column grid  |

## Accessibility

- Sidebar has `aria-label="Product filters"` and `id` for `aria-controls`
- Mobile toggle has `aria-expanded` and `aria-controls`
- Search input has `role="search"`, associated label, `aria-describedby`
- Filter groups use `<fieldset>` and `<legend>`
- Results count uses `aria-live="polite"` and `aria-atomic="true"`
- Active filters region has `role="region"` and `aria-label`
- Remove-filter buttons have descriptive `aria-label`
- Pagination nav has `aria-label="Product pagination"`
- Page buttons have `aria-label` for screen readers

## Code Example

```tsx
import { ProductGrid } from "@/components/ProductGrid"
import { getProducts } from "@/lib/notion"

const products = await getProducts()
<ProductGrid products={products} />
```

## Cross-References

- **ProductCard**: `specs/components/product-card.md` — rendered for each product
- **Input**: `specs/components/input.md` — search field
- **Button**: `specs/components/button.md` — filter toggle, pagination, clear
- **Badge**: `specs/components/badge.md` — active filter pills
- **Select**: `specs/components/select.md` — rows per page
- **Checkbox**: `specs/components/checkbox.md` — multi-select filters
- **RadioGroup**: `specs/components/radio-group.md` — single-select filters
- **Tokens**: `specs/tokens/token-reference.md`
