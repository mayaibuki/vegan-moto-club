import { getProducts } from "@/lib/notion"
import { ProductGrid } from "@/components/ProductGrid"

export default async function ProductsPage() {
  const products = await getProducts()

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-4xl font-heading font-bold mb-2">Vegan Motorcycle Gear</h1>
        <p className="text-muted-foreground">
          Browse our curated database of ethical and cruelty-free motorcycle gear
        </p>
      </div>

      <ProductGrid products={products} />
    </div>
  )
}
