/**
 * Renders a JSON-LD block. `<` is escaped so content that comes from Notion
 * (product descriptions, event text) can never close the script tag early.
 */
export function JsonLd({ data }: { data: object }) {
  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(data).replace(/</g, "\\u003c") }}
    />
  )
}
