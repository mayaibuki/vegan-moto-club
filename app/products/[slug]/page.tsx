import type { Metadata } from "next"
import { getProductBySlug, getProducts } from "@/lib/notion"
import { notFound } from "next/navigation"
import Image from "next/image"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { formatPrice, notionImageUrl, splitCategories } from "@/lib/utils"
import { SuggestProductForm } from "@/components/SuggestProductForm"
import { RelatedProducts } from "@/components/RelatedProducts"
import { Breadcrumbs } from "@/components/Breadcrumbs"
import { SITE_URL, seasonEmojis } from "@/lib/constants"

export async function generateStaticParams() {
  const products = await getProducts()
  return products.map((product) => ({
    slug: product.slug,
  }))
}

export async function generateMetadata({
  params,
}: {
  params: { slug: string }
}): Promise<Metadata> {
  const product = await getProductBySlug(params.slug)

  if (!product) {
    return {
      title: "Product Not Found",
    }
  }

  // Build a keyword-rich description that includes materials, protection level, and season
  const keyFeatures = [
    product.levelOfProtection,
    ...product.season,
    product.waterproofLevel,
    ...product.materials.slice(0, 2),
  ].filter(Boolean).join(", ")

  const description = product.description
    ? product.description.slice(0, 160)
    : `${product.name} by ${product.brand} - Vegan ${product.category} for motorcycle riders.${keyFeatures ? ` ${keyFeatures}.` : ""} Cruelty-free and ethical gear.`.slice(0, 160)

  return {
    title: `${product.name} by ${product.brand}`,
    description,
    openGraph: {
      title: `${product.name} by ${product.brand} | Vegan Moto Club`,
      description,
      url: `/products/${product.slug}`,
      images: product.photos.length > 0 ? [{ url: product.photos[0] }] : [],
      type: "website",
    },
    twitter: {
      card: "summary_large_image",
      title: `${product.name} by ${product.brand}`,
      description,
      images: product.photos.length > 0 ? [product.photos[0]] : [],
    },
    alternates: {
      canonical: `/products/${product.slug}`,
    },
  }
}

export default async function ProductDetailPage({
  params,
}: {
  params: { slug: string }
}) {
  const [product, allProducts] = await Promise.all([
    getProductBySlug(params.slug),
    getProducts(),
  ])

  if (!product) {
    notFound()
  }

  const primaryCategory = splitCategories(product.category)[0]

  const breadcrumbJsonLd = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: [
      {
        "@type": "ListItem",
        position: 1,
        name: "Home",
        item: SITE_URL,
      },
      {
        "@type": "ListItem",
        position: 2,
        name: "Products",
        item: `${SITE_URL}/products`,
      },
      {
        "@type": "ListItem",
        position: 3,
        name: product.name,
        item: `${SITE_URL}/products/${product.slug}`,
      },
    ],
  }

  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "Product",
    name: product.name,
    description: product.description || `${product.name} - Vegan ${product.category}`,
    image: product.photos,
    brand: {
      "@type": "Brand",
      name: product.brand,
    },
    offers: {
      "@type": "Offer",
      price: product.price,
      priceCurrency: "USD",
      url: product.url || `${SITE_URL}/products/${product.slug}`,
    },
    category: product.category,
    additionalProperty: [
      ...(product.levelOfProtection
        ? [{ "@type": "PropertyValue", name: "Protection Level", value: product.levelOfProtection }]
        : []),
      ...(product.veganVerified
        ? [{ "@type": "PropertyValue", name: "Vegan Verified", value: product.veganVerified }]
        : []),
      ...product.materials.map((m) => ({
        "@type": "PropertyValue",
        name: "Material",
        value: m,
      })),
    ],
  }

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbJsonLd) }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <div className="space-y-8">
      <Breadcrumbs
        items={[
          { label: "Home", href: "/" },
          { label: "Products", href: "/products" },
          // First category only: the joined multi-select string ("Jackets,
          // Protection") isn't a valid category filter value
          ...(primaryCategory
            ? [{ label: primaryCategory, href: `/products?category=${encodeURIComponent(primaryCategory)}` }]
            : []),
          { label: product.name },
        ]}
      />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <figure aria-label={`Product images for ${product.name}`}>
          {product.photos.length > 0 ? (
            <div className="space-y-4">
              <div className="relative w-full aspect-square bg-muted rounded-lg overflow-hidden">
                <Image
                  src={notionImageUrl(product.photos[0], 1200)}
                  alt={`${product.name} by ${product.brand} - ${product.category || "motorcycle gear"}`}
                  fill
                  sizes="(max-width: 768px) 100vw, 50vw"
                  className="object-cover"
                  priority
                  unoptimized={product.photos[0].startsWith("/api/notion-image")}
                />
              </div>
              {product.photos.length > 1 && (
                <div className="grid grid-cols-3 gap-2" role="group" aria-label="Additional product images">
                  {product.photos.slice(1).map((photo, idx) => (
                    <div
                      key={idx}
                      className="relative aspect-square bg-muted rounded overflow-hidden"
                    >
                      <Image
                        src={notionImageUrl(photo, 256)}
                        alt={`${product.name} - view ${idx + 2} of ${product.photos.length}`}
                        fill
                        sizes="(max-width: 768px) 33vw, 16vw"
                        className="object-cover"
                        loading="lazy"
                        unoptimized={photo.startsWith("/api/notion-image")}
                      />
                    </div>
                  ))}
                </div>
              )}
            </div>
          ) : (
            <div className="w-full h-96 bg-muted rounded-lg flex items-center justify-center" aria-hidden="true">
              <p className="text-muted-foreground">No image available</p>
            </div>
          )}
        </figure>

        <div className="space-y-6">
          <div className="space-y-1">
            <h1 className="h-page">{product.name}</h1>
            <p className="text-lg font-medium text-muted-foreground">{product.brand}</p>
            <p className="pt-2 text-2xl md:text-3xl font-bold tabular-nums" aria-label={`Price: ${formatPrice(product.price)}`}>{formatPrice(product.price)}</p>
          </div>

          {product.url && (
            <Button size="lg" asChild className="w-full">
              <a
                href={product.url}
                target="_blank"
                rel="noopener noreferrer"
                aria-label={`View ${product.name} on store website (opens in new tab)`}
              >
                View on Store<span className="sr-only"> (opens in new tab)</span>
              </a>
            </Button>
          )}

          {product.staffFavorite && <Badge><span aria-hidden="true">⭐</span> Staff Pick</Badge>}

          <dl className="md:grid md:grid-cols-[auto_1fr] md:gap-x-6 md:gap-y-3">
            <dt className="text-sm font-medium text-muted-foreground mb-2 mt-6 first:mt-0 md:mt-0">Category</dt>
            <dd className="text-base font-semibold">{product.category}</dd>
            <dt className="text-sm font-medium text-muted-foreground mb-2 mt-6 first:mt-0 md:mt-0">Gender</dt>
            <dd className="text-base font-semibold">{product.gender}</dd>
            <dt className="text-sm font-medium text-muted-foreground mb-2 mt-6 first:mt-0 md:mt-0">Specs</dt>
            <dd>
            <ul className="flex flex-wrap gap-2 list-none" role="list" aria-label="Product specifications">
              {product.levelOfProtection && (
                <li><Badge
                  variant={
                    product.levelOfProtection === "Most protective" ||
                    product.levelOfProtection === "Highly protective"
                      ? "positive"
                      : product.levelOfProtection === "Moderately protective"
                      ? "outline"
                      : product.levelOfProtection === "Slightly protective"
                      ? "secondary"
                      : "negative"
                  }
                >
                  {product.levelOfProtection}
                </Badge></li>
              )}
              {product.season.map((s) => (
                <li key={s}><Badge variant="outline">
                  <span aria-hidden="true">{seasonEmojis[s] || ""}</span> {s}
                </Badge></li>
              ))}
              {product.waterproofLevel && (
                <li><Badge
                  variant={
                    product.waterproofLevel === "Water resistant" ||
                    product.waterproofLevel === "Not waterproof"
                      ? "destructive"
                      : "outline"
                  }
                >
                  {product.waterproofLevel}
                </Badge></li>
              )}
              {product.veganVerified && (
                <li><Link
                  href="/verification"
                  aria-label={`${product.veganVerified}, learn how we verify vegan gear`}
                  className="focus-ring rounded-full"
                >
                  <Badge
                    variant={
                      // Notion value is lowercase "us" — matching "Us" made
                      // our own strongest tier render as a red warning badge
                      product.veganVerified === "Verified Vegan by us" ||
                      product.veganVerified === "Confirmed Vegan by maker"
                        ? "default"
                        : product.veganVerified === "Verified Vegan by AI"
                        ? "outline"
                        : "destructive"
                    }
                  >
                    <span aria-hidden="true">✓</span> {product.veganVerified}
                  </Badge>
                </Link></li>
              )}
            </ul>
            </dd>

          {product.ridingStyle.length > 0 && (
            <>
              <dt className="text-sm font-medium text-muted-foreground mb-2 mt-6 first:mt-0 md:mt-0">Riding Styles</dt>
              <dd>
              <ul className="flex flex-wrap gap-2 list-none" aria-label="Suitable riding styles">
                {product.ridingStyle.map((style) => (
                  <li key={style}>
                    <Badge variant="outline">
                      {style}
                    </Badge>
                  </li>
                ))}
              </ul>
              </dd>
            </>
          )}

          {product.materials.length > 0 && (
            <>
              <dt className="text-sm font-medium text-muted-foreground mb-2 mt-6 first:mt-0 md:mt-0">Materials</dt>
              <dd>
              <ul className="flex flex-wrap gap-2 list-none" aria-label="Product materials">
                {product.materials.map((material) => (
                  <li key={material}>
                    <Badge variant="outline" className="text-xs">
                      {material}
                    </Badge>
                  </li>
                ))}
              </ul>
              </dd>
            </>
          )}
          </dl>
        </div>
      </div>

      {product.description && (
        <div className="max-w-2xl mx-auto">
          <h2 className="h-section mb-4">Description</h2>
          <p className="text-muted-foreground whitespace-pre-wrap">
            {product.description}
          </p>
        </div>
      )}

      <RelatedProducts currentProduct={product} allProducts={allProducts} />

      <SuggestProductForm id="product" />
    </div>
    </>
  )
}
