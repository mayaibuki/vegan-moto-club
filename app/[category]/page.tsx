import type { Metadata } from "next"
import Link from "next/link"
import { notFound } from "next/navigation"
import { getProducts } from "@/lib/notion"
import { splitCategories } from "@/lib/utils"
import { CATEGORY_PAGES, SITE_URL } from "@/lib/constants"
import { ProductCard } from "@/components/ProductCard"
import { Breadcrumbs } from "@/components/Breadcrumbs"
import { Button } from "@/components/ui/button"

export const revalidate = 3600
// Only the listed category slugs resolve; everything else 404s
export const dynamicParams = false

export function generateStaticParams() {
  return CATEGORY_PAGES.map((page) => ({ category: page.slug }))
}

export function generateMetadata({ params }: { params: { category: string } }): Metadata {
  const page = CATEGORY_PAGES.find((p) => p.slug === params.category)
  if (!page) return {}
  return {
    title: page.title,
    description: page.description,
    openGraph: {
      title: `${page.title} | Vegan Moto Club`,
      description: page.description,
      url: `/${page.slug}`,
    },
    alternates: {
      canonical: `/${page.slug}`,
    },
  }
}

export default async function CategoryLandingPage({
  params,
}: {
  params: { category: string }
}) {
  const page = CATEGORY_PAGES.find((p) => p.slug === params.category)
  if (!page) notFound()

  const allProducts = await getProducts()
  const products = allProducts.filter((product) =>
    splitCategories(product.category).includes(page.category)
  )
  const otherCategories = CATEGORY_PAGES.filter((p) => p.slug !== page.slug)

  const breadcrumbJsonLd = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: [
      { "@type": "ListItem", position: 1, name: "Home", item: SITE_URL },
      { "@type": "ListItem", position: 2, name: "Products", item: `${SITE_URL}/products` },
      { "@type": "ListItem", position: 3, name: page.title, item: `${SITE_URL}/${page.slug}` },
    ],
  }

  const itemListJsonLd = {
    "@context": "https://schema.org",
    "@type": "ItemList",
    name: page.title,
    numberOfItems: products.length,
    itemListElement: products.slice(0, 48).map((product, index) => ({
      "@type": "ListItem",
      position: index + 1,
      name: product.name,
      url: `${SITE_URL}/products/${product.slug}`,
    })),
  }

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbJsonLd) }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(itemListJsonLd) }}
      />
      <div className="space-y-10">
        <Breadcrumbs
          items={[
            { label: "Home", href: "/" },
            { label: "Products", href: "/products" },
            { label: page.title },
          ]}
        />

        <div className="space-y-4 max-w-3xl">
          <h1 className="text-3xl md:text-4xl font-bold">{page.title}</h1>
          {page.intro.map((paragraph) => (
            <p key={paragraph.slice(0, 24)} className="text-lg text-muted-foreground">
              {paragraph}
            </p>
          ))}
        </div>

        <div className="flex flex-wrap items-center gap-4">
          <p className="text-sm text-muted-foreground">
            <span className="font-semibold text-foreground">{products.length}</span>{" "}
            {products.length === 1 ? "product" : "products"} in this category
          </p>
          <Button variant="outline" size="sm" asChild>
            <Link href={`/products?category=${encodeURIComponent(page.category)}`}>
              Filter &amp; sort these products
            </Link>
          </Button>
        </div>

        {products.length === 0 ? (
          <p className="text-muted-foreground py-8">
            No products in this category right now. Check back soon, or{" "}
            <Link href="/products" className="underline hover:text-foreground">
              browse the full catalog
            </Link>
            .
          </p>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            {products.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        )}

        <nav aria-label="Other categories" className="border-t border-border pt-8">
          <p className="text-sm text-muted-foreground mb-3">Browse other categories:</p>
          <ul className="flex flex-wrap gap-3">
            {otherCategories.map((other) => (
              <li key={other.slug}>
                <Link
                  href={`/${other.slug}`}
                  className="inline-block rounded-full border border-border px-4 py-1.5 text-sm hover:bg-muted"
                >
                  {other.title}
                </Link>
              </li>
            ))}
          </ul>
        </nav>
      </div>
    </>
  )
}
