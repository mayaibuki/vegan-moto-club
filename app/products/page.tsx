import { getProducts } from "@/lib/notion"
import { ProductGrid } from "@/components/ProductGrid"

export default async function ProductsPage() {
  const products = await getProducts()

  return (
    <div className="space-y-10">
      <div className="space-y-2">
        <h1 className="text-3xl md:text-4xl font-bold">Vegan Motorcycle Gear</h1>
        <p className="text-lg text-muted-foreground">
          Browse our curated database of ethical and cruelty-free motorcycle gear
        </p>
      </div>

      <ProductGrid products={products} />
    </div>
  )
}
