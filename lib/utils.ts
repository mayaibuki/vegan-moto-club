import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatPrice(price: number): string {
  return `$${Math.round(price)}`
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

export function filterProducts(
  products: any[],
  filters: {
    brand?: string
    category?: string
    genders?: string[]
    ridingStyles?: string[]
    search?: string
  }
): any[] {
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

export function getUniqueBrands(products: any[]): string[] {
  const brands = new Set(products.map((p) => p.brand).filter(Boolean))
  return Array.from(brands).sort()
}

export function getUniqueCategories(products: any[]): string[] {
  const categories = new Set(products.map((p) => p.category).filter(Boolean))
  return Array.from(categories).sort()
}

export function getUniqueGenders(products: any[]): string[] {
  const genders = new Set(products.map((p) => p.gender).filter(Boolean))
  return Array.from(genders).sort()
}

export function getUniqueRidingStyles(products: any[]): string[] {
  const styles = new Set<string>()
  products.forEach((p) => {
    p.ridingStyle.forEach((s: string) => styles.add(s))
  })
  return Array.from(styles).sort()
}
