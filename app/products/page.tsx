import type { Metadata } from "next"
import { Suspense } from "react"
import dynamic from "next/dynamic"
import { getProducts } from "@/lib/notion"

const ProductGrid = dynamic(() => import("@/components/ProductGrid").then(m => m.ProductGrid), { ssr: false })

export const revalidate = 3600

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

      <Suspense fallback={<div className="text-muted-foreground">Loading products...</div>}>
        <ProductGrid products={products} />
      </Suspense>
    </div>
  )
}
