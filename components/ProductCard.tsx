import { memo } from "react"
import Link from "next/link"
import { Card, CardContent } from "./ui/card"
import { Badge } from "./ui/badge"
import { ProductCardImage } from "./ProductCardImage"
import { Product } from "@/lib/notion"
import { formatPrice } from "@/lib/utils"

const seasonEmojis: Record<string, string> = {
  Summer: "☀️",
  "Mid season": "🌦",
  Winter: "❄️",
}

interface ProductCardProps {
  product: Product
}

export const ProductCard = memo(function ProductCard({ product }: ProductCardProps) {
  return (
    <article className="h-full">
      <Link
        href={`/products/${product.slug}`}
        aria-label={`View ${product.name} by ${product.brand} - ${formatPrice(product.price)}`}
        className="block h-full"
      >
        <Card className="h-full hover:shadow-lg transition-shadow duration-300 cursor-pointer overflow-hidden group">
          {/* Image Section */}
          <div className="relative aspect-square w-full bg-card overflow-hidden border-b border-border/30 flex items-center justify-center">
            {product.photos.length > 0 ? (
              <ProductCardImage
                src={product.photos[0]}
                alt={`${product.name} by ${product.brand} - ${product.category || "motorcycle gear"}`}
              />
            ) : (
              <div className="absolute inset-0 flex items-center justify-center text-muted-foreground" aria-hidden="true">
                No Image
              </div>
            )}
            {/* Staff Pick Badge - Positioned on image */}
            {product.staffFavorite && (
              <div className="absolute top-3 left-3">
                <Badge variant="default">Staff Pick</Badge>
              </div>
            )}
          </div>

          <CardContent className="p-5 space-y-3">
            {/* Brand - Small and muted above product name */}
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
              {product.brand}
            </p>

            {/* Product Name */}
            <h3 className="font-semibold text-base leading-tight line-clamp-2">
              {product.name}
            </h3>

            {/* Price - More prominent */}
            <p className="text-xl font-bold text-foreground tabular-nums">
              {formatPrice(product.price)}
            </p>

            {/* Badges - Grouped and cleaner */}
            <div className="flex flex-wrap gap-1.5 pt-1" aria-label="Product attributes">
              {product.levelOfProtection && (
                <Badge
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
                <Badge key={s} variant="outline">
                  <span aria-hidden="true">{seasonEmojis[s] || ""}</span> {s}
                </Badge>
              ))}
              {product.gender && (
                <Badge variant="outline">
                  {product.gender}
                </Badge>
              )}
            </div>

          </CardContent>
        </Card>
      </Link>
    </article>
  )
})
