import type { Metadata } from "next"
import { getProductBySlug, getProducts } from "@/lib/notion"
import { notFound } from "next/navigation"
import Image from "next/image"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { formatPrice } from "@/lib/utils"
import { SuggestProductForm } from "@/components/SuggestProductForm"
import { RelatedProducts } from "@/components/RelatedProducts"
import { Breadcrumbs } from "@/components/Breadcrumbs"

const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || "https://veganmotoclub.com"

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

  const seasonEmojis: Record<string, string> = {
    Summer: "☀️",
    "Mid season": "🌦",
    Winter: "❄️",
  }

  const breadcrumbJsonLd = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: [
      {
        "@type": "ListItem",
        position: 1,
        name: "Home",
        item: siteUrl,
      },
      {
        "@type": "ListItem",
        position: 2,
        name: "Products",
        item: `${siteUrl}/products`,
      },
      {
        "@type": "ListItem",
        position: 3,
        name: product.name,
        item: `${siteUrl}/products/${product.slug}`,
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
      availability: "https://schema.org/InStock",
      url: product.url || `${siteUrl}/products/${product.slug}`,
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
      {/* Breadcrumb Navigation */}
      <Breadcrumbs
        items={[
          { label: "Home", href: "/" },
          { label: "Products", href: "/products" },
          { label: product.category, href: `/products?category=${encodeURIComponent(product.category)}` },
          { label: product.name },
        ]}
      />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Images */}
        <figure aria-label={`Product images for ${product.name}`}>
          {product.photos.length > 0 ? (
            <div className="space-y-4">
              <div className="relative w-full aspect-square bg-muted rounded-lg overflow-hidden">
                <Image
                  src={product.photos[0]}
                  alt={`${product.name} by ${product.brand} - ${product.category || "motorcycle gear"}`}
                  fill
                  sizes="(max-width: 768px) 100vw, 50vw"
                  className="object-cover"
                  priority
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
                        src={photo}
                        alt={`${product.name} - view ${idx + 2} of ${product.photos.length}`}
                        fill
                        sizes="(max-width: 768px) 33vw, 16vw"
                        className="object-cover"
                        loading="lazy"
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

        {/* Details */}
        <div className="space-y-6">
          {/* Title and Brand */}
          <div>
            <h1 className="text-3xl font-bold">{product.name}</h1>
            <p className="text-lg text-muted-foreground">{product.brand}</p>
          </div>

          {/* Staff Pick Badge */}
          {product.staffFavorite && <Badge><span aria-hidden="true">⭐</span> Staff Pick</Badge>}

          {/* Price */}
          <div>
            <p className="text-sm text-muted-foreground font-medium mb-1">Price</p>
            <p className="text-3xl font-bold" aria-label={`Price: ${formatPrice(product.price)}`}>{formatPrice(product.price)}</p>
          </div>

          {/* Category and Gender */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-muted-foreground font-medium mb-1">Category</p>
              <p className="font-semibold">{product.category}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground font-medium mb-1">Gender</p>
              <p className="font-semibold">{product.gender}</p>
            </div>
          </div>

          {/* Badges */}
          <div>
            <p className="text-sm text-muted-foreground font-medium mb-2">Specs</p>
            <div className="flex flex-wrap gap-2" role="list" aria-label="Product specifications">
              {product.levelOfProtection && (
                <Badge
                  role="listitem"
                  variant={
                    product.levelOfProtection === "Most protective" ||
                    product.levelOfProtection === "Highly protective"
                      ? "default"
                      : product.levelOfProtection === "Moderately protective" ||
                        product.levelOfProtection === "Slightly protective"
                      ? "outline"
                      : "destructive"
                  }
                >
                  {product.levelOfProtection}
                </Badge>
              )}
              {product.season.map((s) => (
                <Badge key={s} variant="outline" role="listitem">
                  <span aria-hidden="true">{seasonEmojis[s] || ""}</span> {s}
                </Badge>
              ))}
              {product.waterproofLevel && (
                <Badge
                  role="listitem"
                  variant={
                    product.waterproofLevel === "Water resistant" ||
                    product.waterproofLevel === "Not waterproof"
                      ? "destructive"
                      : "outline"
                  }
                >
                  {product.waterproofLevel}
                </Badge>
              )}
              {product.veganVerified && (
                <Badge
                  role="listitem"
                  variant={
                    product.veganVerified === "Verified Vegan by Us" ||
                    product.veganVerified === "Confirmed Vegan by maker"
                      ? "default"
                      : product.veganVerified === "Verified Vegan by AI"
                      ? "outline"
                      : "destructive"
                  }
                >
                  <span aria-hidden="true">✓</span> {product.veganVerified}
                </Badge>
              )}
            </div>
          </div>

          {/* Riding Styles */}
          {product.ridingStyle.length > 0 && (
            <div>
              <p className="text-sm text-muted-foreground font-medium mb-2">Riding Styles</p>
              <ul className="flex flex-wrap gap-2 list-none" aria-label="Suitable riding styles">
                {product.ridingStyle.map((style) => (
                  <li key={style}>
                    <Badge variant="outline">
                      {style}
                    </Badge>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Materials */}
          {product.materials.length > 0 && (
            <div>
              <p className="text-sm text-muted-foreground font-medium mb-2">Materials</p>
              <ul className="flex flex-wrap gap-2 list-none" aria-label="Product materials">
                {product.materials.map((material) => (
                  <li key={material}>
                    <Badge variant="outline" className="text-xs">
                      {material}
                    </Badge>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* CTA Button */}
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
        </div>
      </div>

      {/* Description */}
      {product.description && (
        <div className="max-w-2xl mx-auto">
          <h2 className="text-xl font-bold mb-4">Description</h2>
          <p className="text-muted-foreground whitespace-pre-wrap">
            {product.description}
          </p>
        </div>
      )}

      {/* Related Products */}
      <RelatedProducts currentProduct={product} allProducts={allProducts} />

      <SuggestProductForm id="product" />
    </div>
    </>
  )
}
