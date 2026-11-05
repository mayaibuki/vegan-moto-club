# Agent instructions: Vegan Moto Club

Read this before changing anything under `app/` or `components/`. Project overview, commands and architecture are in `CLAUDE.md`.

## Design system

The design system lives in this repo. Code is the source of truth:

- `app/tokens.css`: every token (Layer 1 primitives `--ds-*`, Layer 2 semantic `--color-*` etc., light and `.dark`)
- `app/globals.css`: shadcn/ui bridge variables (`--background`, `--foreground`, ...)
- `tailwind.config.ts`: the Tailwind classes that map to those tokens
- `specs/foundations/` (color, spacing, typography, radius, elevation, motion), `specs/tokens/token-reference.md`, `specs/components/` (one file per component)
- `components/ui/` and `components/`: the components themselves

A browsable mirror is published at https://claude.ai/artifact/PfoXuHvSnGkzeNV6hwSRT7. It is a read-only view for people. Never treat it as the source and never copy values from it into code.

### Rules

1. **Read the specs before writing UI code.** Open the relevant file in `specs/components/` and `specs/foundations/` first.
2. **Reuse before you build.** Before creating a component, check whether one of these already does the job, and extend it with a variant or prop instead of adding a new one:
   - Primitives (`components/ui/`): `Badge`, `Button`, `Card`, `Checkbox`, `Input`, `Label`, `RadioGroup`, `Select`, `Textarea`
   - Site components (`components/`): `Breadcrumbs`, `CategoryProductList`, `EventCard`, `FaqSection`, `Footer`, `Logo`, `Navbar`, `PastEventsList`, `ProductCard`, `ProductCardImage`, `ProductGrid`, `PromoBanner`, `RelatedProducts`, `SortSelect`, `Spinner`, `StickyBuyBar`, `SuggestEventForm`, `SuggestProductForm`
3. **A genuinely new component needs a spec first.** Write `specs/components/<name>.md` in the same format as the existing specs, built only from existing tokens, and say in the PR why no existing component fits.
4. **Use only tokens.** No hardcoded colours (`text-red-600`, `bg-white`, `#hex`), no arbitrary values (`h-[30px]`, `z-[100]`). Prefer the semantic Tailwind classes (`bg-card`, `text-muted-foreground`, `text-destructive`, `text-success`) over raw `var()`.
5. **Don't invent new tokens or values.** If a design needs a value the tokens don't have, stop and ask instead of adding one.
6. **When a spec and the code disagree, stop and ask.** Don't silently pick one.
7. **Keep the brand rules.** Lime is a fill: lime as text, icons or links uses `primary-text`, and text on a lime fill is always stone-950. Muted text is stone-600 (stone-500 fails AA). Dark mode is `.dark` on `<html>`. Copy follows `docs/brand-voice.md`.
8. **Run the audit before committing.** `node scripts/token-audit.js` must exit 0. If you changed `specs/foundations/color.md`, run `node scripts/spec-hex.js` and commit the result. CI runs both on every pull request.
9. **When you change tokens or components, update the matching spec in the same PR**, and tell the owner the design system mirror needs a re-sync.
