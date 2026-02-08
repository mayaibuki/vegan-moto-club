import type { Metadata } from "next"
import { getProducts } from "@/lib/notion"
import { ProductGrid } from "@/components/ProductGrid"

export const metadata: Metadata = {
  title: "Vegan Motorcycle Gear",
  description:
    "Browse our curated database of ethical and cruelty-free motorcycle gear. Find vegan jackets, gloves, boots, and protective wear for every riding style.",
  openGraph: {
    title: "Vegan Motorcycle Gear | Vegan Moto Club",
    description:
      "Browse our curated database of ethical and cruelty-free motorcycle gear. Find vegan jackets, gloves, boots, and protective wear for every riding style.",
    url: "/products",
  },
  alternates: {
    canonical: "/products",
  },
}

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
