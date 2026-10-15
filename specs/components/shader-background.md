# ShaderBackground

| Key        | Value                                         |
|------------|-----------------------------------------------|
| File       | `components/ShaderBackground.tsx`             |
| Type       | Client component                              |
| Imports    | `GrainGradient` from `@paper-design/shaders-react` |
| Mounted in | `app/layout.tsx`, first child of `<body>`     |

## Overview

An animated grain gradient (Paper Shaders) fixed behind every page. Its two colours come from design tokens, so it follows light and dark mode without its own palette.

## Anatomy

```
<div aria-hidden class="pointer-events-none fixed inset-0 -z-10">   ← full-viewport layer behind content
  <GrainGradient />                                                  ← WebGL canvas, 100% × 100%
</div>
```

The layout wrapper (`min-h-screen flex flex-col`) has no background of its own so the layer shows through. Cards, popovers and inputs keep their opaque surfaces.

## Tokens Used

| Prop         | Token          | Light           | Dark             | Note                                  |
|--------------|----------------|-----------------|------------------|---------------------------------------|
| `colorBack`  | `--background` | stone-50        | stone-950        | Same as `bg-background`               |
| `colors[0]`  | `--primary`    | lime-500        | lime-400         | Same as `bg-primary` (full opacity)   |

Token values are read with `getComputedStyle` and converted to `hsla(h, s%, l%, a)` with integer components, the only HSL form the shader's colour parser accepts. A `MutationObserver` on `<html class>` re-reads them when the theme toggles. Never pass hex values.

## Shader Parameters

| Prop       | Value       |
|------------|-------------|
| `shape`    | `"corners"` |
| `softness` | 1           |
| `intensity`| 1           |
| `noise`    | 1           |
| `speed`    | 1 (0 under reduced motion) |

## Fallbacks

- **Server render / first paint:** renders nothing until mounted; the body's `bg-background` shows.
- **No WebGL2:** renders nothing; `bg-background` stays.
- **`prefers-reduced-motion: reduce`:** `speed={0}`, a static gradient. Updates live if the OS setting changes.

## Accessibility

Decorative only: `aria-hidden`, `pointer-events-none`. Text sits on the shader where the gradient is near `colorBack`; check contrast where the lime corners reach headings or body copy.
