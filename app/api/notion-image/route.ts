import { notion } from "@/lib/notion"
import { NextRequest, NextResponse } from "next/server"
import sharp from "sharp"

export const runtime = "nodejs"

const ALLOWED_WIDTHS = new Set([256, 600, 1200])

export async function GET(request: NextRequest) {
  const { searchParams } = request.nextUrl
  const pageId = searchParams.get("pageId")
  const prop = searchParams.get("prop")
  const idx = parseInt(searchParams.get("idx") ?? "0", 10)
  const wParam = searchParams.get("w")
  const width = wParam && ALLOWED_WIDTHS.has(parseInt(wParam, 10)) ? parseInt(wParam, 10) : null

  if (!pageId || !prop) {
    return new NextResponse("Missing params", { status: 400 })
  }

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

  const upstreamBytes = Buffer.from(await upstream.arrayBuffer())

  // When ?w= is supplied (and matches an allowed width), resize and re-encode
  // as WebP server-side. The downstream <Image> uses unoptimized so Vercel's
  // image optimizer is bypassed entirely — zero transformations consumed.
  // Result is cached for 31 days, keyed on the full URL incl. width.
  if (width) {
    const resized = await sharp(upstreamBytes)
      .rotate()
      .resize({ width, withoutEnlargement: true })
      .webp({ quality: 80 })
      .toBuffer()

    return new NextResponse(new Uint8Array(resized), {
      headers: {
        "Content-Type": "image/webp",
        "Cache-Control": "public, max-age=2678400, stale-while-revalidate=86400",
      },
    })
  }

  const contentType = upstream.headers.get("content-type") ?? "image/jpeg"
  return new NextResponse(new Uint8Array(upstreamBytes), {
    headers: {
      "Content-Type": contentType,
      "Cache-Control": "public, max-age=2678400, stale-while-revalidate=86400",
    },
  })
}
