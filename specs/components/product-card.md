# ProductCard

| Key        | Value                              |
|------------|------------------------------------|
| File       | `components/ProductCard.tsx`       |
| Type       | Client-rendered (via `React.memo`) |
| Imports    | Card, CardContent, Badge, Image, Link |
| Data       | `Product` from `lib/notion.ts`     |

## Overview

Displays a single product as a linked card with image, brand, name, price, and attribute badges. Wrapped in `React.memo` to prevent re-renders when sibling cards change. Used exclusively inside `ProductGrid`.

## Anatomy

```
<article>                          ← semantic wrapper
  <Link>                           ← full-card link to /products/[id]
    <Card>                         ← shadcn Card shell
      <div>                        ← image container (aspect-square, bg-card)
        <Image />                  ← Next.js optimized image (fill + object-contain)
        <Badge />                  ← "Staff Pick" overlay (conditional)
      </div>
      <CardContent>
        <p>                        ← brand (xs, uppercase, muted)
        <h3>                       ← product name (semibold, line-clamp-2)
        <p>                        ← price (xl, bold)
        <div>                      ← badge row (protection, season, gender)
          <Badge /> ...
        </div>
        <p>                        ← category (xs, muted, conditional)
      </CardContent>
    </Card>
  </Link>
</article>
```

## Tokens Used

| Element             | Token / Class              | Purpose            |
|---------------------|----------------------------|--------------------|
| Image container     | `bg-card`                  | Neutral background |
| Brand text          | `text-muted-foreground`    | De-emphasized      |
| Product name        | `text-foreground` (inherit)| Primary text       |
| Price               | `text-foreground`          | High emphasis      |
| Category text       | `text-muted-foreground`    | De-emphasized      |
| Card hover          | `hover:shadow-lg`          | Elevation feedback |
| Image hover         | `group-hover:scale-105`    | Zoom effect        |
| Transition          | `duration-300`             | Standard motion    |
| No-image text       | `text-muted-foreground`    | Placeholder        |
| Border              | `border-border/30`         | Subtle divider     |

## Props

| Prop      | Type      | Required | Description                          |
|-----------|-----------|----------|--------------------------------------|
| `product` | `Product` | Yes      | Full product object from Notion API  |

## States

| State          | Behavior                                          |
|----------------|---------------------------------------------------|
| With image     | Shows product photo with object-contain + padding |
| Without image  | Shows "No Image" centered placeholder             |
| Staff favorite | Overlays ⭐ Staff Pick badge on image top-left    |
| Hover          | Card shadow increases, image scales up 5%         |

## Accessibility

- `<article>` wraps each card for semantic grouping
- `<Link>` has `aria-label` with product name, brand, and price
- Decorative emojis use `aria-hidden="true"`
- Badge row has `aria-label="Product attributes"`
- Image `alt` includes product name, brand, and category

## Code Example

```tsx
import { ProductCard } from "@/components/ProductCard"

<ProductCard product={product} />
```

## Cross-References

- **Card**: `specs/components/card.md` — provides the outer shell
- **Badge**: `specs/components/badge.md` — attribute pills
- **ProductGrid**: `specs/components/product-grid.md` — parent container
- **Tokens**: `specs/tokens/token-reference.md`
- **Color**: `specs/foundations/color.md`
