import { getProduct, getProducts } from "@/lib/notion"
import { notFound } from "next/navigation"
import Image from "next/image"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { formatPrice } from "@/lib/utils"

export async function generateStaticParams() {
  const products = await getProducts()
  return products.map((product) => ({
    id: product.id,
  }))
}

export default async function ProductDetailPage({
  params,
}: {
  params: { id: string }
}) {
  const product = await getProduct(params.id)

  if (!product) {
    notFound()
  }

  const seasonEmojis: Record<string, string> = {
    Summer: "☀️",
    "Mid season": "🌦",
    Winter: "❄️",
  }

  return (
    <div className="space-y-8">
      {/* Back Button */}
      <Button variant="ghost" asChild className="mb-4">
        <Link href="/products">← Back to Products</Link>
      </Button>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Images */}
        <div>
          {product.photos.length > 0 ? (
            <div className="space-y-4">
              <div className="relative w-full h-96 bg-muted rounded-lg overflow-hidden">
                <Image
                  src={product.photos[0]}
                  alt={product.name}
                  fill
                  className="object-cover"
                  priority
                  onError={(e) => {
                    e.currentTarget.style.display = "none"
                  }}
                />
              </div>
              {product.photos.length > 1 && (
                <div className="grid grid-cols-3 gap-2">
                  {product.photos.slice(1).map((photo, idx) => (
                    <div
                      key={idx}
                      className="relative h-24 bg-muted rounded overflow-hidden"
                    >
                      <Image
                        src={photo}
                        alt={`${product.name} ${idx + 2}`}
                        fill
                        className="object-cover"
                        onError={(e) => {
                          e.currentTarget.style.display = "none"
                        }}
                      />
                    </div>
                  ))}
                </div>
              )}
            </div>
          ) : (
            <div className="w-full h-96 bg-muted rounded-lg flex items-center justify-center">
              <p className="text-muted-foreground">No image available</p>
            </div>
          )}
        </div>

        {/* Details */}
        <div className="space-y-6">
          {/* Title and Brand */}
          <div>
            <div className="flex items-start justify-between gap-2 mb-2">
              <h1 className="text-3xl font-bold">{product.name}</h1>
              {product.staffFavorite && <Badge>⭐ Staff Pick</Badge>}
            </div>
            <p className="text-lg text-muted-foreground">{product.brand}</p>
          </div>

          {/* Price */}
          <div>
            <p className="text-sm text-muted-foreground mb-1">Price</p>
            <p className="text-3xl font-bold">{formatPrice(product.price)}</p>
          </div>

          {/* Category and Gender */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-muted-foreground mb-1">Category</p>
              <p className="font-semibold">{product.category}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground mb-1">Gender</p>
              <p className="font-semibold">{product.gender}</p>
            </div>
          </div>

          {/* Badges */}
          <div>
            <p className="text-sm text-muted-foreground mb-2">Specs</p>
            <div className="flex flex-wrap gap-2">
              {product.levelOfProtection && (
                <Badge>{product.levelOfProtection}</Badge>
              )}
              {product.season.map((s) => (
                <Badge key={s} variant="secondary">
                  {seasonEmojis[s] || ""} {s}
                </Badge>
              ))}
              {product.waterproofLevel && (
                <Badge variant="outline">{product.waterproofLevel}</Badge>
              )}
              {product.veganVerified && (
                <Badge variant="outline" className="bg-green-50 text-green-900 dark:bg-green-900 dark:text-green-50">
                  ✓ {product.veganVerified}
                </Badge>
              )}
            </div>
          </div>

          {/* Riding Styles */}
          {product.ridingStyle.length > 0 && (
            <div>
              <p className="text-sm text-muted-foreground mb-2">Riding Styles</p>
              <div className="flex flex-wrap gap-2">
                {product.ridingStyle.map((style) => (
                  <Badge key={style} variant="secondary">
                    {style}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {/* Materials */}
          {product.materials.length > 0 && (
            <div>
              <p className="text-sm text-muted-foreground mb-2">Materials</p>
              <div className="flex flex-wrap gap-2">
                {product.materials.map((material) => (
                  <Badge key={material} variant="outline" className="text-xs">
                    {material}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {/* CTA Button */}
          {product.url && (
            <Button size="lg" asChild className="w-full">
              <a href={product.url} target="_blank" rel="noopener noreferrer">
                View on Store
              </a>
            </Button>
          )}
        </div>
      </div>

      {/* Description */}
      {product.description && (
        <Card>
          <CardContent className="pt-6">
            <h2 className="text-xl font-bold mb-4">Description</h2>
            <p className="text-muted-foreground whitespace-pre-wrap">
              {product.description}
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
