// POST /api/suggest-event: a visitor suggests an event (description + URL).
import { createNotionPage, isRateLimited, isValidUrl, json, rateLimitResponse, type PagesContext } from "../../lib/cloudflare/shared"

export async function onRequestPost({ request, env }: PagesContext): Promise<Response> {
  try {
    if (isRateLimited(request)) return rateLimitResponse()
    const { description, url, website } = (await request.json()) as {
      description?: unknown
      url?: unknown
      website?: unknown
    }

    if (website) return json({ success: true })

    if (!description || typeof description !== "string" || !description.trim()) {
      return json({ error: "Please provide an event description." }, 400)
    }
    if (description.trim().length > 2000) {
      return json({ error: "Description must be 2000 characters or fewer." }, 400)
    }
    if (!url || typeof url !== "string" || !url.trim()) {
      return json({ error: "Please provide an event URL." }, 400)
    }
    if (!isValidUrl(url.trim())) {
      return json({ error: "Please provide a valid URL (e.g. https://example.com)." }, 400)
    }

    await createNotionPage(env, env.NOTION_EVENTS_DB_ID, {
      "Name of event": { title: [{ text: { content: `User Suggestion - ${new URL(url.trim()).hostname}` } }] },
      URL: { url: url.trim() },
      Description: { rich_text: [{ text: { content: description.trim() } }] },
    })
    return json({ success: true })
  } catch (error) {
    console.error("[api/suggest-event] failed:", error)
    return json({ error: "Something went wrong. Please try again." }, 500)
  }
}
