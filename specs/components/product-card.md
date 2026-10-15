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
        <p>                        ← brand (xs, medium, muted, sentence case as stored)
        <h3>                       ← product name (semibold, line-clamp-2)
        <p>                        ← price (xl, bold)
        <ul>                       ← badge row (protection, season, gender)
          <li><Badge size="sm" /></li> ...
        </ul>
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
| Content padding     | `p-3 space-y-2` below 640px, `sm:p-5 sm:space-y-3` | Compact mobile card |
| Image padding       | `p-3 sm:p-4`               | Photo inset        |
| Badges              | `size="sm"` + `sm:px-3 sm:py-1` | Compact below 640px, default padding from sm up |
| Card hover          | `<Card interactive>`: `hover:shadow-md hover:border-foreground/25`, `transition-[box-shadow,border-color,transform] duration-200` (hover-capable devices only) | Elevation feedback |
| Card press          | `motion-safe:group-active:scale-[0.98]` (`group` is on the Link) | Touch/press feedback |
| Keyboard focus      | `.focus-ring rounded-2xl` on the Link | Ring follows the 16px card radius |
| Image hover         | `group-hover:scale-105`    | Zoom effect        |
| Transition          | `duration-300`             | Standard motion    |
| No-image text       | `text-muted-foreground`    | Placeholder        |
| Image divider       | `border-b border-border`   | Solid hairline     |

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
| Hover          | Card shadow to `shadow-md`, border darkens, image scales up 5% |

## Mobile (below 640px)

The two-column grid leaves about 145px of text width, so the attribute row is trimmed to stay on one line and the card stays under 340px tall at 390px:

| Badge | Below 640px | 640px and up |
|-------|-------------|--------------|
| Protection | Short label (Most, High, Moderate, Slight), `whitespace-nowrap`; full label in `sr-only` | Full label |
| Season | First season as its emoji only (name in `sr-only`), then a `+N` pill when there are more | Every season with emoji and name |
| Gender | Hidden | Shown |

## Accessibility

- `<article>` wraps each card for semantic grouping
- `<Link>` has `aria-label` with product name, brand, price, protection level and "Staff pick" when set
- Decorative emojis use `aria-hidden="true"`
- Badge row is a `<ul role="list" aria-label="Product attributes">` with one `<li>` per badge
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
