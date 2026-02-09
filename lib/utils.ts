import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"
import type { Product } from "./notion"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatPrice(price: number): string {
  return price % 1 === 0 ? `$${price}` : `$${price.toFixed(2)}`
}

export function formatDate(dateString: string): string {
  if (!dateString) return ""
  const date = new Date(dateString)
  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  })
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

export function filterProducts(
  products: Product[],
  filters: {
    brand?: string
    category?: string
    genders?: string[]
    ridingStyles?: string[]
    search?: string
  }
): Product[] {
  return products.filter((product) => {
    if (filters.search) {
      const searchLower = filters.search.toLowerCase()
      if (
        !product.name.toLowerCase().includes(searchLower) &&
        !product.brand.toLowerCase().includes(searchLower)
      ) {
        return false
      }
    }
    if (filters.brand && product.brand !== filters.brand) {
      return false
    }
    if (filters.category && product.category !== filters.category) {
      return false
    }
    if (filters.genders && filters.genders.length > 0) {
      // Check if product's gender matches any of the selected genders
      if (!filters.genders.some(g => product.gender.includes(g))) {
        return false
      }
    }
    if (filters.ridingStyles && filters.ridingStyles.length > 0) {
      // Check if product's ridingStyle matches any of the selected styles
      if (!filters.ridingStyles.some(s => product.ridingStyle.includes(s))) {
        return false
      }
    }
    return true
  })
}

export function getUniqueBrands(products: Product[]): string[] {
  const brands = new Set(products.map((p) => p.brand).filter(Boolean))
  return Array.from(brands).sort()
}
