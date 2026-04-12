import { notion } from "@/lib/notion"
import { NextRequest, NextResponse } from "next/server"
import { isRateLimited, isValidUrl, getClientIp, rateLimitResponse } from "@/lib/api-utils"

export async function POST(request: NextRequest) {
  try {
    const ip = getClientIp(request)
    if (isRateLimited(ip)) return rateLimitResponse()

    const body = await request.json()
    const { description, url, website } = body

    // Honeypot check
    if (website) {
      return NextResponse.json({ success: true })
    }

    if (!description || typeof description !== "string" || !description.trim()) {
      return NextResponse.json(
        { error: "Please provide an event description." },
        { status: 400 }
      )
    }

    if (description.trim().length > 2000) {
      return NextResponse.json(
        { error: "Description must be 2000 characters or fewer." },
        { status: 400 }
      )
    }

    if (!url || typeof url !== "string" || !url.trim()) {
      return NextResponse.json(
        { error: "Please provide an event URL." },
        { status: 400 }
      )
    }

    if (!isValidUrl(url.trim())) {
      return NextResponse.json(
        { error: "Please provide a valid URL (e.g. https://example.com)." },
        { status: 400 }
      )
    }

    const parsedUrl = new URL(url.trim())
    const title = `User Suggestion - ${parsedUrl.hostname}`

    await notion.pages.create({
      parent: {
        database_id: process.env.NOTION_EVENTS_DB_ID!,
      },
      properties: {
        "Name of event": {
          title: [{ text: { content: title } }],
        },
        Description: {
          rich_text: [{ text: { content: description.trim() } }],
        },
        URL: {
          url: url.trim(),
        },
      },
    })

    return NextResponse.json({ success: true })
  } catch (error) {
    console.error("[API] Failed to submit event suggestion:", error)
    return NextResponse.json(
      { error: "Something went wrong. Please try again." },
      { status: 500 }
    )
  }
}
