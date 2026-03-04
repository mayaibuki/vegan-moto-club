# SuggestProductForm

| Key        | Value                                    |
|------------|------------------------------------------|
| File       | `components/SuggestProductForm.tsx`      |
| Type       | Client component (`"use client"`)        |
| Imports    | Card, CardHeader, CardTitle, CardDescription, CardContent, Input, Label, Button |
| Endpoint   | `POST /api/suggest`                      |

## Overview

A URL submission form that lets visitors suggest vegan motorcycle products for review. Includes honeypot and timing-based bot protection. Wraps the form inside a Card for visual consistency. Used on the products listing page.

## Anatomy

```
<section aria-labelledby={headingId}>
  <Card>                                 ← max-w-2xl, centered
    <CardHeader>
      <CardTitle>                        ← "Suggest a Product"
      <CardDescription>                 ← helper text
    </CardHeader>
    <CardContent>
      <form>
        <div aria-hidden="true">         ← honeypot field (visually hidden)
        <div>
          <Label>                        ← "Product URL"
          <div>                          ← flex row (col on mobile)
            <Input type="url" />         ← URL input
            <Button type="submit" />     ← submit with loading spinner
          </div>
        </div>
        <p>                              ← success message (conditional)
        <p>                              ← error message (conditional)
      </form>
    </CardContent>
  </Card>
</section>
```

## Tokens Used

| Element            | Token / Class             | Purpose              |
|--------------------|---------------------------|----------------------|
| Success message    | `text-success`            | Positive feedback    |
| Error message      | `text-destructive`        | Error feedback       |
| Card description   | `text-base` (inherited)   | Helper text          |
| Spinner opacity    | `opacity-25`, `opacity-75`| Loading indicator    |
| Spinner animation  | `animate-spin`            | Rotation             |
| Form gap           | `gap-3`                   | Input-button spacing |
| Honeypot wrapper   | `opacity-0 h-0 w-0`      | Hidden from users    |

## Props

| Prop | Type     | Required | Default | Description                      |
|------|----------|----------|---------|----------------------------------|
| `id` | `string` | No       | —       | Unique suffix for element IDs    |

## States

| State        | Type         | Visual Behavior                                |
|--------------|--------------|------------------------------------------------|
| `idle`       | `FormStatus` | Default — input enabled, submit button shows "Submit" |
| `submitting` | `FormStatus` | Input disabled, button shows spinner + "Submitting..." |
| `success`    | `FormStatus` | Green success message, auto-resets after 3s    |
| `error`      | `FormStatus` | Red error message with specific reason         |

## Bot Protection

1. **Honeypot field**: Hidden input (`website`) — if filled, fakes success silently
2. **Timing check**: Rejects submissions under 2 seconds from mount (fakes success)
3. **URL validation**: Client-side `new URL()` check before API call

## Accessibility

- `<section>` with `aria-labelledby` pointing to the heading
- Label associated with input via `htmlFor`/`id` pairing
- Honeypot field has `aria-hidden="true"` and `tabIndex={-1}`
- Submit button has visible loading state text for screen readers
- Error and success messages are in the DOM flow (announced on render)

## Code Example

```tsx
import { SuggestProductForm } from "@/components/SuggestProductForm"

<SuggestProductForm />
<SuggestProductForm id="sidebar" />  {/* multiple instances */}
```

## Cross-References

- **Card**: `specs/components/card.md` — outer container
- **Input**: `specs/components/input.md` — URL field
- **Button**: `specs/components/button.md` — submit action
- **Color (success)**: `specs/foundations/color.md` — `--success` token
- **Tokens**: `specs/tokens/token-reference.md`
