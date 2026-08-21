import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"
import type { Product } from "./notion"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Append a width hint to a Notion proxy URL so the proxy returns a resized
 * WebP. Non-proxy URLs (external images) are returned unchanged. Used together
 * with `unoptimized` on <Image> to bypass Vercel's image optimizer.
 */
export function notionImageUrl(src: string, width: 256 | 600 | 1200): string {
  if (!src.startsWith("/api/notion-image")) return src
  const sep = src.includes("?") ? "&" : "?"
  return `${src}${sep}w=${width}`
}

export function formatPrice(price: number): string {
  return price % 1 === 0 ? `$${price}` : `$${price.toFixed(2)}`
}

/**
 * The first 10 chars of a Notion date string are the wall-clock date in the
 * event's own timezone, for both date-only and datetime-with-offset values.
 * Formatting that part avoids UTC-conversion day shifts (a 5pm PDT end time
 * is already midnight UTC the next day).
 */
function localDatePart(dateString: string): string {
  return dateString.slice(0, 10)
}

export function formatDate(dateString: string): string {
  if (!dateString) return ""
  const date = new Date(localDatePart(dateString))
  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    timeZone: "UTC",
  })
}

export function isSameEventDay(start: string, end: string): boolean {
  if (!start) return true
  if (!end || end === start) return true
  return localDatePart(start) === localDatePart(end)
}

export function formatEventMonth(dateString: string): string {
  if (!dateString) return ""
  return new Date(localDatePart(dateString)).toLocaleDateString("en-US", { month: "short", timeZone: "UTC" })
}

export function formatEventDay(dateString: string): string {
  if (!dateString) return ""
  return String(new Date(localDatePart(dateString)).getUTCDate())
}

export function formatRelativeDate(dateString: string): string {
  if (!dateString) return ""
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffSecs = Math.floor(diffMs / 1000)
  const diffMins = Math.floor(diffSecs / 60)
  const diffHours = Math.floor(diffMins / 60)
  const diffDays = Math.floor(diffHours / 24)

  if (diffDays === 0) return "Today"
  if (diffDays === 1) return "Yesterday"
  if (diffDays < 7) return `${diffDays} days ago`
  if (diffDays < 14) return "1 week ago"
  if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`
  if (diffDays < 60) return "1 month ago"
  return `${Math.floor(diffDays / 30)} months ago`
}

export interface ProductFilters {
  brand?: string
  category?: string
  genders?: string[]
  ridingStyles?: string[]
  protectionLevels?: string[]
  seasons?: string[]
  waterproofLevels?: string[]
  priceMin?: number
  priceMax?: number
  search?: string
}

/** Terms riders type that the catalog spells differently. */
const SEARCH_SYNONYMS: Record<string, string[]> = {
  trousers: ["pants"],
  pants: ["trousers"],
  adv: ["adventure"],
  mc: ["motorcycle"],
  waterproof: ["water resistant"],
}

export function splitCategories(category: string): string[] {
  return category.split(",").map((c) => c.trim()).filter(Boolean)
}

export function filterProducts(products: Product[], filters: ProductFilters): Product[] {
  return products.filter((product) => {
    if (filters.search) {
      const haystack = [
        product.name,
        product.brand,
        product.description,
        product.category,
        product.materials.join(" "),
        product.season.join(" "),
        product.waterproofLevel,
        product.ridingStyle.join(" "),
      ]
        .join(" ")
        .toLowerCase()
      // Every word the rider typed must match somewhere (directly or via synonym)
      const terms = filters.search.toLowerCase().split(/\s+/).filter(Boolean)
      const allTermsMatch = terms.every((term) =>
        [term, ...(SEARCH_SYNONYMS[term] || [])].some((t) => haystack.includes(t))
      )
      if (!allTermsMatch) return false
    }
    if (filters.brand && product.brand !== filters.brand) {
      return false
    }
    if (filters.category) {
      // category is a joined multi-select string ("Jackets, Protection") —
      // match individual values so multi-category products stay findable
      if (
        product.category !== filters.category &&
        !splitCategories(product.category).includes(filters.category)
      ) {
        return false
      }
    }
    if (filters.genders && filters.genders.length > 0) {
      if (!filters.genders.some(g => product.gender.includes(g))) {
        return false
      }
    }
    if (filters.ridingStyles && filters.ridingStyles.length > 0) {
      if (!filters.ridingStyles.some(s => product.ridingStyle.includes(s))) {
        return false
      }
    }
    if (filters.protectionLevels && filters.protectionLevels.length > 0) {
      if (!filters.protectionLevels.includes(product.levelOfProtection)) {
        return false
      }
    }
    if (filters.seasons && filters.seasons.length > 0) {
      if (!filters.seasons.some(s => product.season.includes(s))) {
        return false
      }
    }
    if (filters.waterproofLevels && filters.waterproofLevels.length > 0) {
      if (!filters.waterproofLevels.includes(product.waterproofLevel)) {
        return false
      }
    }
    if (filters.priceMin !== undefined && product.price < filters.priceMin) {
      return false
    }
    if (filters.priceMax !== undefined && product.price > filters.priceMax) {
      return false
    }
    return true
  })
}

/** Sorted unique non-empty values of a product field (string or string[]). */
export function getUniqueValues(
  products: Product[],
  get: (product: Product) => string | string[]
): string[] {
  const values = new Set<string>()
  for (const product of products) {
    const value = get(product)
    for (const v of Array.isArray(value) ? value : [value]) {
      if (v) values.add(v)
    }
  }
  return Array.from(values).sort()
}

export function generateSlug(name: string): string {
  return name
    .toLowerCase()
    .trim()
    .replace(/[^\w\s-]/g, "")
    .replace(/\s+/g, "-")
    .replace(/-+/g, "-")
    .replace(/^-+|-+$/g, "")
}

export function getUniqueBrands(products: Product[]): string[] {
  const brands = new Set(products.map((p) => p.brand).filter(Boolean))
  return Array.from(brands).sort()
}
