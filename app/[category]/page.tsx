import type { Metadata } from "next"
import Link from "next/link"
import { notFound } from "next/navigation"
import { getProducts } from "@/lib/notion"
import { splitCategories } from "@/lib/utils"
import { CATEGORY_PAGES, SITE_URL } from "@/lib/constants"
import { CategoryProductList } from "@/components/CategoryProductList"
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
          <h1 className="h-page">{page.title}</h1>
          {page.intro.map((paragraph, index) => (
            <p
              key={paragraph.slice(0, 24)}
              className={index === 0 ? "lead max-w-prose" : "text-base text-muted-foreground leading-relaxed max-w-prose text-pretty"}
            >
              {paragraph}
            </p>
          ))}
        </div>

        {/* Category switcher: scrolls sideways on phones, wraps from md */}
        <nav aria-label="Gear categories">
          <ul className="no-scrollbar flex gap-2 overflow-x-auto -mx-4 px-4 scroll-px-4 snap-x sm:-mx-6 sm:px-6 md:mx-0 md:px-0 md:flex-wrap md:overflow-visible">
            {CATEGORY_PAGES.map((cat) => (
              <li key={cat.slug} className="snap-start shrink-0">
                <Link
                  href={`/${cat.slug}`}
                  aria-current={cat.slug === page.slug ? "page" : undefined}
                  className="inline-flex h-11 items-center rounded-full border border-border bg-card px-4 text-sm transition-colors duration-150 hover:bg-muted focus-ring aria-[current=page]:border-primary aria-[current=page]:bg-primary aria-[current=page]:font-semibold aria-[current=page]:text-primary-foreground"
                >
                  {cat.title}
                </Link>
              </li>
            ))}
          </ul>
        </nav>

        <CategoryProductList products={products}>
          <Button variant="outline" asChild>
            <Link href={`/products?category=${encodeURIComponent(page.category)}`}>
              More filters
            </Link>
          </Button>
        </CategoryProductList>

        {products.length === 0 && (
          <p className="text-muted-foreground py-8">
            No products in this category right now. Check back soon, or{" "}
            <Link href="/products" className="underline hover:text-foreground">
              browse the full catalog
            </Link>
            .
          </p>
        )}
      </div>
    </>
  )
}
