import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"

// Match UUID pattern (Notion page IDs)
const UUID_REGEX = /^[0-9a-f]{8}-?[0-9a-f]{4}-?[0-9a-f]{4}-?[0-9a-f]{4}-?[0-9a-f]{12}$/i

export function middleware(request: NextRequest) {
  const pathname = request.nextUrl.pathname

  // Check if this is a product page with a UUID-style ID
  const match = pathname.match(/^\/products\/(.+)$/)
  if (match) {
    const param = match[1]
    if (UUID_REGEX.test(param)) {
      // Redirect UUID URLs to /products page (they'll need to find the slug URL)
      // We can't look up the slug in middleware (no Notion access), so redirect to products listing
      const url = request.nextUrl.clone()
      url.pathname = "/products"
      return NextResponse.redirect(url, 301)
    }
  }

  return NextResponse.next()
}

export const config = {
  matcher: "/products/:path*",
}
