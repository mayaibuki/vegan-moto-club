# Logo

| Key        | Value                          |
|------------|--------------------------------|
| File       | `components/Logo.tsx`          |
| Type       | Server component               |
| Imports    | Image (next/image), Link       |
| Asset      | `/images/logo.png`             |

## Overview

Renders the Vegan Moto Club logo at one of three predefined sizes. Optionally wraps itself in a `<Link>` for navigation (defaults to home). Used in the Navbar (sm) and Footer (lg).

## Anatomy

```
<Link href={href}>              ← optional wrapper (omitted if href is falsy)
  <div>                          ← flex container (row for sm, column otherwise)
    <Image />                    ← Next.js optimized image with priority loading
  </div>
</Link>
```

## Tokens Used

| Element    | Token / Class | Value           | Purpose            |
|------------|---------------|-----------------|--------------------|
| Small      | `h-8 w-auto`  | 32 × 32 px      | Navbar logo        |
| Medium     | `h-10 w-auto` | 40 × 40 px      | Default            |
| Large      | `h-16 w-auto` | 64 × 64 px      | Footer / hero logo |
| Container  | `gap-2`       | 0.5rem           | Icon-text spacing  |
| Layout sm  | `flex-row`    | (default flex)   | Inline layout      |
| Layout md/lg | `flex-col`  | Stacked          | Vertical layout    |

## Props

| Prop   | Type                    | Required | Default | Description         |
|--------|-------------------------|----------|---------|---------------------|
| `size` | `"sm" \| "md" \| "lg"` | No       | `"md"`  | Predefined size     |
| `href` | `string`                | No       | `"/"`   | Link destination    |

## Size Map

| Size | CSS Class  | Image Width | Image Height | Layout    |
|------|------------|-------------|--------------|-----------|
| sm   | `h-8`     | 32px        | 32px         | Row       |
| md   | `h-10`    | 40px        | 40px         | Column    |
| lg   | `h-16`    | 64px        | 64px         | Column    |

## Accessibility

- Image has `alt="Vegan Moto Club"` — serves as the site identity
- `priority` attribute on Image ensures above-fold loading
- When wrapped in Link, the link text is derived from the image alt

## Code Example

```tsx
import { Logo } from "@/components/Logo"

<Logo size="sm" />              {/* Navbar */}
<Logo size="lg" href="/" />     {/* Footer */}
<Logo size="md" href={false} /> {/* Static, no link */}
```

## Cross-References

- **Navbar**: `specs/components/navbar.md` — uses Logo sm
- **Footer**: `specs/components/footer.md` — uses Logo lg
- **Spacing**: `specs/foundations/spacing.md` — size scale alignment
- **Tokens**: `specs/tokens/token-reference.md` — `--component-logo-*`
