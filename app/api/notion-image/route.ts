import { Client } from "@notionhq/client"
import { NextRequest, NextResponse } from "next/server"

const notion = new Client({ auth: process.env.NOTION_API_KEY })

export async function GET(request: NextRequest) {
  const { searchParams } = request.nextUrl
  const pageId = searchParams.get("pageId")
  const prop = searchParams.get("prop")
  const idx = parseInt(searchParams.get("idx") ?? "0", 10)

  if (!pageId || !prop) {
    return new NextResponse("Missing params", { status: 400 })
  }

  // Fetch a fresh page to get a current (non-expired) signed URL from Notion.
  // This call is cheap — Vercel caches the resulting image for 31 days so this
  // route is only invoked once per image per cache window, not per page view.
  let imageUrl: string | null = null
  try {
    const page = await notion.pages.retrieve({ page_id: pageId }) as {
      properties: Record<string, { type: string; files?: Array<{ type: string; file?: { url: string }; external?: { url: string } }> }>
    }
    const files = page.properties[prop]?.files
    if (!files || !files[idx]) {
      return new NextResponse("File not found", { status: 404 })
    }
    const file = files[idx]
    if (file.type === "file") {
      imageUrl = file.file?.url ?? null
    } else if (file.type === "external") {
      imageUrl = file.external?.url ?? null
    }
  } catch {
    return new NextResponse("Notion API error", { status: 502 })
  }

  if (!imageUrl) {
    return new NextResponse("No image URL", { status: 404 })
  }

  const upstream = await fetch(imageUrl)
  if (!upstream.ok) {
    return new NextResponse("Upstream fetch failed", { status: upstream.status })
  }

  const contentType = upstream.headers.get("content-type") ?? "image/jpeg"
  const body = await upstream.arrayBuffer()

  return new NextResponse(body, {
    headers: {
      "Content-Type": contentType,
      // Cache for 31 days — matches minimumCacheTTL in next.config.js.
      // Vercel's image optimizer will cache the optimized result for the same
      // duration, keyed on the stable pageId+prop+idx URL.
      "Cache-Control": "public, max-age=2678400, stale-while-revalidate=86400",
    },
  })
}
