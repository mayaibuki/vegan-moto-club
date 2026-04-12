import { notion } from "@/lib/notion"
import { NextRequest, NextResponse } from "next/server"
import { isRateLimited, isValidUrl, getClientIp, rateLimitResponse } from "@/lib/api-utils"

export async function POST(request: NextRequest) {
  try {
    const ip = getClientIp(request)
    if (isRateLimited(ip)) return rateLimitResponse()

    const body = await request.json()
    const { url, website } = body

    // Honeypot check
    if (website) {
      return NextResponse.json({ success: true })
    }

    if (!url || typeof url !== "string" || !url.trim()) {
      return NextResponse.json(
        { error: "Please provide a product URL." },
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
        database_id: process.env.NOTION_PRODUCTS_DB_ID!,
      },
      properties: {
        "Name of product": {
          title: [
            {
              text: {
                content: title,
              },
            },
          ],
        },
        URL: {
          url: url.trim(),
        },
      },
    })

    return NextResponse.json({ success: true })
  } catch (error) {
    console.error("[API] Failed to submit product suggestion:", error)
    return NextResponse.json(
      { error: "Something went wrong. Please try again." },
      { status: 500 }
    )
  }
}
