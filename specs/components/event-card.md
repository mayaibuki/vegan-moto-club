# EventCard

| Key     | Value                                        |
|---------|----------------------------------------------|
| File    | `components/EventCard.tsx`                   |
| Type    | Server component                             |
| Imports | Card, Button, Image, ArrowRight, MapPin      |
| Data    | `Event` from `lib/notion.ts`                 |

## Overview

Displays a single event as a card with a poster image, an overlaid date block, an overlaid price pill, title, location, description, and a "Learn More" CTA. Used inside `app/events/page.tsx` for both the Upcoming and Past grids. Matches Figma nodes `149:164` (single-day) and `149:185` (multi-day).

## Variants

| Variant       | When                                           | Date overlay                                            |
|---------------|------------------------------------------------|---------------------------------------------------------|
| Single-day    | `startDate === endDate`                        | One 48×48 block (`Mar 30`)                              |
| Multi-day     | `startDate !== endDate`                        | Two blocks with `ArrowRight` separator (`Mar 30 → Apr 1`) |

## Anatomy

```
<article>                                  ← semantic wrapper (muted via opacity-60 for past events)
  <Card p-4 gap-4>                         ← rounded-2xl shell, padded
    <div aspect-square rounded-xl>         ← poster container
      <Image fill object-cover />          ← Next.js poster
      <div absolute inset-0 p-2>           ← overlay wrapper, pointer-events-none
        <div flex gap-2>                   ← date overlay (top)
          <DateBlock />                    ← 48×48 foreground block: month + day
          [ArrowRight + DateBlock]         ← multi-day only
        </div>
        <div>                              ← price pill (bottom-left)
      </div>
    </div>
    <h3>                                   ← event name (xl, semibold, line-clamp-2)
    <p>                                    ← location with MapPin icon (muted)
    <p>                                    ← description (line-clamp-5, flex-1)
    <Button>                               ← Learn More CTA (full-width, rounded-full)
  </Card>
</article>
```

## Tokens Used

| Element            | Token / Class                     | Purpose                          |
|--------------------|-----------------------------------|----------------------------------|
| Card shell         | `bg-card`, `border-border/50`, `rounded-2xl`, `shadow-sm`, `hover:shadow-md` | Standard card |
| Poster background  | `bg-muted`                        | Placeholder while loading        |
| Poster radius      | `rounded-xl`                      | Inner radius, tighter than card  |
| DateBlock          | `bg-foreground`, `text-background`| High-contrast, auto-inverts in dark |
| DateBlock month    | `text-sm font-semibold`           | Abbreviation label               |
| DateBlock day      | `text-2xl font-semibold`          | Primary number                   |
| Arrow              | `text-foreground`, `size-6`       | Multi-day separator              |
| Price pill         | `bg-card`, `border-border`, `rounded-full`, `text-foreground`, `text-xs font-semibold` | Overlay chip |
| Heading            | `text-xl font-semibold tracking-tight text-foreground` | Event name |
| Location           | `text-sm font-medium text-muted-foreground` + `MapPin size-4` | Muted with icon |
| Description        | `text-base text-foreground line-clamp-5 flex-1` | Fills remaining height |
| CTA                | `bg-primary text-primary-foreground rounded-full h-10` | Full-width button |

No hex or arbitrary values — all classes resolve to semantic tokens defined in `app/tokens.css` + `app/globals.css`.

## Props

| Prop    | Type     | Required | Default | Description                                  |
|---------|----------|----------|---------|----------------------------------------------|
| `event` | `Event`  | Yes      | —       | Full event object from Notion API            |
| `muted` | `boolean`| No       | `false` | Renders the card at 60% opacity (past events)|

## States

| State       | Behavior                                             |
|-------------|------------------------------------------------------|
| Default     | `shadow-sm`, full opacity                            |
| Hover       | `shadow-md` (from Card base)                         |
| Muted       | `opacity-60` on the outer `<article>`                |
| No poster   | Centered `No poster` placeholder inside `bg-muted`   |
| Single-day  | Single `DateBlock` overlay                           |
| Multi-day   | Two `DateBlock`s with `ArrowRight` between           |

## Accessibility

- `<article>` wraps each card for semantic grouping.
- Image `alt` includes the event name (`"{name} event poster"`).
- `DateBlock`s are `aria-hidden="true"` (visual abbreviation); a `sr-only` span provides a natural sentence: `"On {date}"` or `"From {start} to {end}"`.
- `ArrowRight` and `MapPin` icons are `aria-hidden="true"`.
- CTA has `aria-label="Learn more about {name} (opens in new tab)"` and an `sr-only` hint for the new-tab behavior.

## Code Example

```tsx
import { EventCard } from "@/components/EventCard"

<EventCard event={event} />
<EventCard event={pastEvent} muted />
```

## Responsive Behavior

- Card uses `h-full` so all cards in a row have matching heights.
- Poster is `aspect-square`, so heights align across the grid regardless of content length.
- Description uses `flex-1`, pinning the CTA to the bottom of the card.
- Overlays use `p-2` padding and `size-12` blocks — legible at 375px mobile width through 1280px desktop.

## Cross-References

- **Card**: `specs/components/card.md` — provides the outer shell
- **Button**: `specs/components/button.md` — "Learn More" CTA
- **Tokens**: `specs/tokens/token-reference.md`
- **Color**: `specs/foundations/color.md`
