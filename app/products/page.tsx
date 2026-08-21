import type { Metadata } from "next"
import Link from "next/link"
import { getProducts } from "@/lib/notion"
import { ProductGrid } from "@/components/ProductGrid"
import { PromoBanner } from "@/components/PromoBanner"
import { Card, CardContent } from "@/components/ui/card"
import { CATEGORY_PAGES } from "@/lib/constants"

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
      <PromoBanner />
      <div className="space-y-4">
        <div className="space-y-2">
          <h1 className="text-3xl md:text-4xl font-bold">Vegan Motorcycle Gear</h1>
          <p className="text-lg text-muted-foreground">
            Browse our curated database of ethical and cruelty-free motorcycle gear
          </p>
        </div>
        <nav aria-label="Gear category guides">
          <ul className="flex flex-wrap gap-2">
            {CATEGORY_PAGES.map((page) => (
              <li key={page.slug}>
                <Link
                  href={`/${page.slug}`}
                  className="inline-block rounded-full border border-border px-3 py-1 text-sm text-muted-foreground hover:bg-muted hover:text-foreground"
                >
                  {page.category}
                </Link>
              </li>
            ))}
          </ul>
        </nav>
      </div>

      {products.length === 0 ? (
        // Distinct from the zero-results filter state: an empty catalog here
        // means the data source is unavailable, not that the rider over-filtered.
        <Card>
          <CardContent className="py-16 text-center space-y-2">
            <p className="text-lg font-semibold">
              We&apos;re having trouble loading the catalog right now.
            </p>
            <p className="text-muted-foreground">
              Please check back in a few minutes.
            </p>
          </CardContent>
        </Card>
      ) : (
        <ProductGrid products={products} />
      )}
    </div>
  )
}
