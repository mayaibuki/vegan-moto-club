import { Product } from "@/lib/notion"
import { ProductCard } from "./ProductCard"

interface RelatedProductsProps {
  currentProduct: Product
  allProducts: Product[]
  maxItems?: number
}

/**
 * Score-based related products: prioritizes same category, then shared
 * riding styles, then same brand. Excludes current product.
 */
export function RelatedProducts({
  currentProduct,
  allProducts,
  maxItems = 4,
}: RelatedProductsProps) {
  const scored = allProducts
    .filter((p) => p.id !== currentProduct.id)
    .map((p) => {
      let score = 0
      if (p.category === currentProduct.category) score += 3
      const sharedStyles = p.ridingStyle.filter((s) =>
        currentProduct.ridingStyle.includes(s)
      )
      score += sharedStyles.length
      if (p.brand === currentProduct.brand) score += 1
      return { product: p, score }
    })
    .filter((s) => s.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, maxItems)

  if (scored.length === 0) return null

  return (
    <section aria-labelledby="related-products-heading">
      <h2
        id="related-products-heading"
        className="text-2xl font-bold tracking-tight mb-6"
      >
        Related Products
      </h2>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
        {scored.map(({ product }) => (
          <ProductCard key={product.id} product={product} />
        ))}
      </div>
    </section>
  )
}
