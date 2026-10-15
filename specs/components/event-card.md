# EventCard

| Key     | Value                                        |
|---------|----------------------------------------------|
| File    | `components/EventCard.tsx`                   |
| Type    | Server component                             |
| Imports | Card, Button, Image, ArrowRight, MapPin      |
| Data    | `Event` from `lib/notion.ts`                 |

## Overview

Displays a single event as a card with a poster image (4:3 on phones, square from 640px), an overlaid date block, an overlaid price pill, title, location, description, and a "Learn More" CTA. Used inside `app/events/page.tsx` for both the Upcoming and Past grids. Matches Figma nodes `149:164` (single-day) and `149:185` (multi-day).

## Variants

| Variant       | When                                           | Date overlay                                            |
|---------------|------------------------------------------------|---------------------------------------------------------|
| Single-day    | `startDate === endDate`                        | One 48×48 block (`Mar 30`)                              |
| Multi-day     | `startDate !== endDate`                        | Two blocks with `ArrowRight` separator (`Mar 30 → Apr 1`) |

## Anatomy

```
<article>                                  ← semantic wrapper
  <Card p-4 gap-4>                         ← rounded-2xl shell, padded
    <div aspect-4/3 sm:aspect-square rounded-xl> ← poster container (only when event.poster)
      <Image fill object-cover />          ← Next.js poster
      <div ring-1 ring-inset ring-foreground/10 rounded-xl> ← hairline outline
      <div absolute inset-0 p-2>           ← overlay wrapper, pointer-events-none
        <div flex gap-2>                   ← date overlay (top)
          <DateBlock />                    ← 48×48 rounded-md foreground block: month + day
          [ArrowRight + DateBlock]         ← multi-day only
        </div>
        <div>                              ← price pill (bottom-left)
      </div>
    </div>
    <h3>                                   ← event name (xl, semibold, line-clamp-2)
    <p>                                    ← location with MapPin icon (muted)
    <p>                                    ← description (line-clamp-5, flex-1)
    <Button>                               ← Learn More CTA (full-width, default 44px)
  </Card>
</article>
```

## Tokens Used

| Element            | Token / Class                     | Purpose                          |
|--------------------|-----------------------------------|----------------------------------|
| Card shell         | `bg-card`, `border-border`, `rounded-2xl`, `shadow-sm`; no hover (only the CTA is clickable) | Standard card |
| Poster background  | `bg-muted`                        | Placeholder while loading        |
| Poster radius      | `rounded-xl`                      | Inner radius, tighter than card  |
| Poster aspect      | `aspect-4/3 sm:aspect-square` (`aspect-4/3` is registered in `tailwind.config.ts`) | Shorter cards on phones |
| Poster outline     | `ring-1 ring-inset ring-foreground/10` overlay, `rounded-xl` | Edge for light posters |
| DateBlock          | `bg-foreground`, `text-background`, `rounded-md`, `shadow-sm` | High-contrast, auto-inverts in dark; radius steps down from the poster |
| DateBlock month    | `text-sm font-semibold`           | Abbreviation label               |
| DateBlock day      | `text-2xl font-semibold`          | Primary number                   |
| Arrow              | `text-foreground`, `size-6`       | Multi-day separator              |
| Price pill         | `bg-card`, `border-border`, `rounded-full`, `text-foreground`, `text-xs font-semibold` | Overlay chip |
| Heading            | `text-xl font-semibold text-foreground` (no tracking; only the `.h-*` heading recipes track tight) | Event name |
| Location           | `text-sm font-medium text-muted-foreground` + `MapPin size-4` | Muted with icon |
| Description        | `text-base text-foreground line-clamp-5 flex-1` | Fills remaining height |
| CTA                | `bg-primary text-primary-foreground rounded-full`, default `h-11` | Full-width button, 44px tap target |

No hex or arbitrary values — all classes resolve to semantic tokens defined in `app/tokens.css` + `app/globals.css`.

## Props

| Prop    | Type     | Required | Default | Description                                  |
|---------|----------|----------|---------|----------------------------------------------|
| `event` | `Event`  | Yes      | —       | Full event object from Notion API            |
| `muted` | `boolean`| No       | `false` | Past event: greyscale, dimmed poster plus a "Past" pill (text stays full contrast) |

## States

| State       | Behavior                                             |
|-------------|------------------------------------------------------|
| Default     | `shadow-sm`, full opacity                            |
| Hover       | None (the card is not a link; only the CTA reacts)   |
| Muted       | `opacity-60 grayscale` on the poster image only; `Past` pill (`bg-card text-muted-foreground text-xs font-semibold rounded-full`) beside the date block |
| No poster   | No poster block: date blocks and price pill sit in one compact row at the top of the card |
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
- Poster is `aspect-4/3` below 640px (about 80px shorter per card on phones) and `aspect-square` from `sm`, so heights align across the grid regardless of content length.
- Description uses `flex-1`, pinning the CTA to the bottom of the card.
- Overlays use `p-2` padding and `size-12` blocks — legible at 375px mobile width through 1280px desktop.

## Cross-References

- **Card**: `specs/components/card.md` — provides the outer shell
- **Button**: `specs/components/button.md` — "Learn More" CTA
- **Tokens**: `specs/tokens/token-reference.md`
- **Color**: `specs/foundations/color.md`

## Motion

The card lifts on hover (`hover:-translate-y-0.5`, `shadow-sm` to `shadow-md`, `transition-[transform,box-shadow] duration-200`). The card itself is not a link, so there is no press scale; its button keeps its own feedback. Instant under `prefers-reduced-motion`. See [motion](../foundations/motion.md#implemented-motion).
