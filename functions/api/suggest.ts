// POST /api/suggest: a visitor suggests a product URL. Stored as a
// "User Suggestion - <host>" row in the products database, which the site hides.
import { createNotionPage, isRateLimited, isValidUrl, json, rateLimitResponse, type PagesContext } from "../../lib/cloudflare/shared"

export async function onRequestPost({ request, env }: PagesContext): Promise<Response> {
  try {
    if (isRateLimited(request)) return rateLimitResponse()
    const { url, website } = (await request.json()) as { url?: unknown; website?: unknown }

    // Honeypot: bots fill the hidden field; pretend it worked.
    if (website) return json({ success: true })

    if (!url || typeof url !== "string" || !url.trim()) {
      return json({ error: "Please provide a product URL." }, 400)
    }
    if (!isValidUrl(url.trim())) {
      return json({ error: "Please provide a valid URL (e.g. https://example.com)." }, 400)
    }

    await createNotionPage(env, env.NOTION_PRODUCTS_DB_ID, {
      "Name of product": { title: [{ text: { content: `User Suggestion - ${new URL(url.trim()).hostname}` } }] },
      URL: { url: url.trim() },
    })
    return json({ success: true })
  } catch (error) {
    console.error("[api/suggest] failed:", error)
    return json({ error: "Something went wrong. Please try again." }, 500)
  }
}
