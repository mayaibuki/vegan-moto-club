"use client"

import type { Product } from "@/lib/notion"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "./ui/select"

export const SORT_OPTIONS = [
  { value: "updated", label: "Recently updated" },
  { value: "price-asc", label: "Price: Low to High" },
  { value: "price-desc", label: "Price: High to Low" },
  { value: "name", label: "Name: A to Z" },
] as const

export type SortValue = (typeof SORT_OPTIONS)[number]["value"]

/** Sorts in place and returns the same array. */
export function sortProducts(products: Product[], sortBy: SortValue): Product[] {
  switch (sortBy) {
    case "price-asc":
      return products.sort((a, b) => a.price - b.price)
    case "price-desc":
      return products.sort((a, b) => b.price - a.price)
    case "name":
      return products.sort((a, b) => a.name.localeCompare(b.name))
    default:
      return products.sort((a, b) => new Date(b.lastEditedTime).getTime() - new Date(a.lastEditedTime).getTime())
  }
}

interface SortSelectProps {
  value: SortValue
  onChange: (value: SortValue) => void
  id?: string
}

/** "Sort by" label plus a 44px select. Shared by /products and the category pages. */
export function SortSelect({ value, onChange, id = "sort-products" }: SortSelectProps) {
  return (
    <div className="flex items-center gap-2">
      <label htmlFor={id} className="text-sm text-muted-foreground whitespace-nowrap">Sort by</label>
      <Select value={value} onValueChange={(v) => onChange(v as SortValue)}>
        <SelectTrigger id={id} className="w-44">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          {SORT_OPTIONS.map((option) => (
            <SelectItem key={option.value} value={option.value}>
              {option.label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  )
}
