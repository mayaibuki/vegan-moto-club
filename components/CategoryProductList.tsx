"use client"

import { useMemo, useState } from "react"
import type { Product } from "@/lib/notion"
import { ProductCard } from "./ProductCard"
import { SortSelect, sortProducts, type SortValue } from "./SortSelect"

interface CategoryProductListProps {
  products: Product[]
  /** Rendered next to the count (e.g. the "Filter & sort" link). */
  children?: React.ReactNode
}

/** Category landing page grid: product count, Sort by, then the cards (client-side sort). */
export function CategoryProductList({ products, children }: CategoryProductListProps) {
  const [sortBy, setSortBy] = useState<SortValue>("updated")
  const sorted = useMemo(() => sortProducts([...products], sortBy), [products, sortBy])

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex flex-wrap items-center gap-4">
          <p className="text-sm font-medium text-foreground">
            <span className="tabular-nums">{products.length}</span>{" "}
            {products.length === 1 ? "product" : "products"} in this category
          </p>
          {children}
        </div>
        {products.length > 1 && <SortSelect value={sortBy} onChange={setSortBy} />}
      </div>
      {products.length > 0 && (
        <>
          <h2 className="sr-only">Products</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 sm:gap-6">
            {sorted.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        </>
      )}
    </div>
  )
}
