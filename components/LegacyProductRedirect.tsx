"use client"

import { useEffect } from "react"

// Old product links used the Notion page id (/products/<uuid>). The static host
// cannot look those up, so the 404 page sends them to the catalog instead.
const UUID_PATH = /^\/products\/[0-9a-f]{8}-?[0-9a-f]{4}-?[0-9a-f]{4}-?[0-9a-f]{4}-?[0-9a-f]{12}\/?$/i

export function LegacyProductRedirect() {
  useEffect(() => {
    if (UUID_PATH.test(window.location.pathname)) window.location.replace("/products")
  }, [])
  return null
}
