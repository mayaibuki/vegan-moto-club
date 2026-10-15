# Design audit, October 2026

Record of the October 2026 design audit of the Vegan Moto Club site: what was found, which of the 35 backlog items the owner approved or dropped, and which exploration options were picked. Item definitions (rationale, change, acceptance) were produced as experiment patches and are not repeated here.

## Summary

Three problems matter most. First, light mode has no surface hierarchy: page and cards are both white, the card edge is a half-opacity hairline (1.07:1), and form borders sit at 1.15:1, so cards, inputs and image tiles blur together on phones. Second, several contrast and keyboard failures already ship: lime hover text and the focus ring at about 2.2:1, dark-mode error text at 1.87:1, past events dimmed below AA, and hidden mobile-menu links that still take Tab focus. Third, mobile layouts are heavy where search traffic lands: product cards about 470px tall with wrapping badges, the store CTA several screens below the price on product pages, and /products overflowing at 320px.

What works: axe found no critical violations; landmarks, skip link, fieldset filters, aria-live counts and alt text are solid; dark mode is clean; body and muted text pass AA; the hero h1 already balances well; owner-liked sizes can stay because the type fixes are about consistency.

Sequencing: phase 3 a11y fixes have no dependencies and can ship right away. Phase 1 (tinted page, bg-card swaps, input borders, image wells, dark elevation) is one change set and unblocks badge and shader work. Phase 2 unifies heading, price and label recipes in DM Sans, so a later typeface swap changes one place. Exploration decides the tint value, the second typeface and italic use, lime distribution, the motion set and shader placement. Phase 4 applies only if a shader ships.

## Items

35 items: 26 approved, 4 dropped, 5 exploration items (VMC-31 to VMC-35).

| ID | Title | Phase | Impact | Effort | Decision | Owner note |
| --- | --- | --- | --- | --- | --- | --- |
| VMC-01 | Make the closed mobile menu unreachable by keyboard and screen readers | 3-motion-polish-a11y | high | S | approved |  |
| VMC-02 | Split lime into fill vs text: darker lime for focus ring, icons and inline text; underline for nav hover | 3-motion-polish-a11y | high | S | approved |  |
| VMC-03 | Separate status text tokens from status fills, and announce form results | 3-motion-polish-a11y | high | S | approved |  |
| VMC-04 | Stop dimming past-event text with opacity-60 | 3-motion-polish-a11y | high | S | approved |  |
| VMC-05 | Align header and footer gutters with page content on mobile | 3-motion-polish-a11y | high | S | approved |  |
| VMC-06 | Tint the light-mode page so white cards separate from it | 1-surfaces | high | S | approved |  |
| VMC-07 | Move controls and chrome from bg-background to bg-card, and drop alpha resting surfaces | 1-surfaces | high | S | approved |  |
| VMC-08 | Give form controls a 3:1 border with a dedicated --input token | 1-surfaces | high | S | approved | I like the darker border, but the background of the text input should be lighter or white, otherwise, when the background of the text input is grey, it looks like the text input is disabled. |
| VMC-09 | Add one focus, hover and press layer for links and cards | 3-motion-polish-a11y | high | S | approved |  |
| VMC-10 | Fix /products reflow at 320px and the cramped sort row | 3-motion-polish-a11y | medium | S | dropped |  |
| VMC-11 | Product detail: name, brand and price read as one title block | 2-typography | high | S | approved |  |
| VMC-12 | Cut mobile product card height from about 470px to under 340px | 3-motion-polish-a11y | high | M | approved |  |
| VMC-13 | Put the store CTA right under the price on mobile, with a sticky bar after it scrolls away | 3-motion-polish-a11y | high | M | approved | Apply the changes to the "View on Store" button but leave the main photo as is. |
| VMC-14 | Bring touch targets to 44px on filters, footer, breadcrumbs, pills and chips | 3-motion-polish-a11y | high | M | approved |  |
| VMC-15 | Give product images one explicit well that works in both modes | 1-surfaces | high | M | dropped |  |
| VMC-16 | Use three heading recipes everywhere, keeping current sizes and weights | 2-typography | high | M | approved |  |
| VMC-17 | Raise dark-mode elevation and use solid card borders | 1-surfaces | medium | S | approved |  |
| VMC-18 | Respect reduced motion and move focus on pagination | 3-motion-polish-a11y | medium | S | approved |  |
| VMC-19 | Clear the remaining axe findings and screen-reader gaps | 3-motion-polish-a11y | medium | S | approved |  |
| VMC-20 | Card and event titles: balanced wrapping, aligned prices, quieter event title | 2-typography | medium | S | dropped |  |
| VMC-21 | Give protection levels their own tonal scale, separate from Staff Pick and CTAs | 1-surfaces | medium | S | approved |  |
| VMC-22 | Hero on mobile: less padding, aligned checklist, CTA in the first viewport, rounded image | 3-motion-polish-a11y | medium | S | approved | I like the changes in spacing and order of elements, but I do not like the rounded bordered card for the hero. Implement these changes without the visible border card. |
| VMC-23 | Long-form and category intro copy: a real lead paragraph and a readable measure | 2-typography | medium | S | approved |  |
| VMC-24 | Event cards: shorter on mobile, no fake hover, concentric radii | 3-motion-polish-a11y | medium | S | approved |  |
| VMC-25 | Category landing pages: category switcher and sort above the grid | 3-motion-polish-a11y | medium | M | approved |  |
| VMC-26 | Filters as a bottom sheet with a 'Show N products' button below lg | 3-motion-polish-a11y | high | L | approved |  |
| VMC-27 | Promo banner: no layout shift, compact on mobile, animated dismiss | 3-motion-polish-a11y | medium | M | approved | Keep the copy of the CTA on mobile as "View Virus Power Suits". |
| VMC-28 | Make tokens.css the single source, sync the specs, and teach the audit the new rules | 1-surfaces | medium | M | approved |  |
| VMC-29 | Unify control strokes, radii, heights and hover fills | 3-motion-polish-a11y | low | M | approved |  |
| VMC-30 | Shader guardrails: tokens, reduced motion, fallback, no text directly on the dither | 4-shader | medium | M | dropped |  |
| VMC-31 | Explore: second typeface and italic usage pattern | explore | medium | M | exploration: typeface pending | Wants to see explorations with Redaction and Michelangelus before choosing. |
| VMC-32 | Explore: confirm the light-mode page tint value | explore | medium | S | exploration pick |  |
| VMC-33 | Explore: where lime appears beyond buttons | explore | medium | S | exploration pick |  |
| VMC-34 | Explore: the motion set | explore | low | S | exploration pick |  |
| VMC-35 | Explore: shader placement and the mobile hero | explore | medium | M | exploration pick |  |

## Exploration picks

- **VMC-32, light page tint:** S2, neutral 98% (`0 0% 98%`), which is the existing `--ds-stone-50` primitive. Cards and popovers stay white. No new primitive.
- **VMC-33, where lime appears:** fills only (items VMC-02 and VMC-21).
- **VMC-34, motion set:** M1 (card lift) and M4 (UI transitions). No M2, no M3.
- **VMC-35, shader:** B0, no shader. VMC-30 (shader guardrails) is dropped.
- **VMC-31, second typeface and italic usage:** pending. The owner wants to see explorations with Redaction and Michelangelus before choosing.

## Pull request plan

1. `feat/light-surfaces`: VMC-06, VMC-07, VMC-08, VMC-17, VMC-21, VMC-28
2. `feat/contrast-a11y`: VMC-01, VMC-02, VMC-03, VMC-04, VMC-05, VMC-09, VMC-18, VMC-19
3. `feat/type-hierarchy`: VMC-11, VMC-16, VMC-23
4. `feat/mobile-layout`: VMC-12, VMC-13, VMC-14, VMC-22, VMC-24, VMC-25, VMC-26, VMC-27, VMC-29
5. `feat/motion`: M1, M4
6. `feat/serif-accents`: VMC-31

Items marked approved in the table above ship through these pull requests. Motion items M1 and M4 are the picks from VMC-34.
