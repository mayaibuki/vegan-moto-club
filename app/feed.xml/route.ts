import { getProducts } from "@/lib/notion"
import { SITE_URL } from "@/lib/constants"

export const revalidate = 3600

function escapeXml(value: string): string {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&apos;")
}

export async function GET() {
  const products = await getProducts()

  const newest = [...products]
    .sort((a, b) => b.createdTime.localeCompare(a.createdTime))
    .slice(0, 50)

  const items = newest
    .map((product) => {
      const url = `${SITE_URL}/products/${product.slug}`
      const description = [
        product.brand && `${product.brand}.`,
        product.description,
        product.price ? `Price: $${product.price}.` : "",
      ]
        .filter(Boolean)
        .join(" ")
        .trim()

      return `    <item>
      <title>${escapeXml(product.name)}</title>
      <link>${escapeXml(url)}</link>
      <guid isPermaLink="false">${escapeXml(product.id)}</guid>
      <pubDate>${new Date(product.createdTime).toUTCString()}</pubDate>
      <description>${escapeXml(description)}</description>
    </item>`
    })
    .join("\n")

  const feed = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>Vegan Moto Club: New Gear</title>
    <link>${SITE_URL}</link>
    <atom:link href="${SITE_URL}/feed.xml" rel="self" type="application/rss+xml"/>
    <description>Newly added vegan motorcycle gear from the Vegan Moto Club database.</description>
    <language>en-us</language>
${items}
  </channel>
</rss>
`

  return new Response(feed, {
    headers: {
      "Content-Type": "application/rss+xml; charset=utf-8",
      "Cache-Control": "public, max-age=3600, s-maxage=3600",
    },
  })
}
