import { Client } from "@notionhq/client"
import { NextRequest, NextResponse } from "next/server"

const notion = new Client({
  auth: process.env.NOTION_API_KEY,
})

// In-memory rate limiting
const rateLimit = new Map<string, { count: number; resetTime: number }>()
const RATE_LIMIT_MAX = 5
const RATE_LIMIT_WINDOW = 60 * 60 * 1000 // 1 hour in ms

function isRateLimited(ip: string): boolean {
  const now = Date.now()
  const entry = rateLimit.get(ip)

  if (!entry || now > entry.resetTime) {
    rateLimit.set(ip, { count: 1, resetTime: now + RATE_LIMIT_WINDOW })
    return false
  }

  if (entry.count >= RATE_LIMIT_MAX) {
    return true
  }

  entry.count++
  return false
}

function isValidUrl(str: string): boolean {
  try {
    const url = new URL(str)
    return url.protocol === "http:" || url.protocol === "https:"
  } catch {
    return false
  }
}

export async function POST(request: NextRequest) {
  try {
    // Rate limiting
    const ip =
      request.headers.get("x-forwarded-for")?.split(",")[0]?.trim() ||
      request.headers.get("x-real-ip") ||
      "unknown"

    if (isRateLimited(ip)) {
      return NextResponse.json(
        { error: "Too many submissions. Please try again later." },
        { status: 429 }
      )
    }

    const body = await request.json()
    const { description, url, website } = body

    // Server-side honeypot check — bots fill this hidden field
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
