import Link from "next/link"
import Image from "next/image"
import { Card, CardContent } from "./ui/card"
import { Badge } from "./ui/badge"
import { Product } from "@/lib/notion"
import { formatPrice } from "@/lib/utils"

interface ProductCardProps {
  product: Product
}

export function ProductCard({ product }: ProductCardProps) {
  const seasonEmojis: Record<string, string> = {
    Summer: "☀️",
    "Mid season": "🌦",
    Winter: "❄️",
  }

  return (
    <Link href={`/products/${product.id}`}>
      <Card className="h-full hover:shadow-lg transition-all duration-300 cursor-pointer overflow-hidden group">
        {/* Image Section */}
        <div className="relative aspect-square w-full bg-white overflow-hidden border-b border-border/30 flex items-center justify-center">
          {product.photos.length > 0 ? (
            <Image
              src={product.photos[0]}
              alt={product.name}
              fill
              className="object-contain p-4 transition-transform duration-300 group-hover:scale-105"
            />
          ) : (
            <div className="absolute inset-0 flex items-center justify-center text-muted-foreground">
              No Image
            </div>
          )}
          {/* Staff Pick Badge - Positioned on image */}
          {product.staffFavorite && (
            <div className="absolute top-3 left-3">
              <Badge variant="default">⭐ Staff Pick</Badge>
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
          <p className="text-xl font-bold text-foreground">
            {formatPrice(product.price)}
          </p>

          {/* Badges - Grouped and cleaner */}
          <div className="flex flex-wrap gap-1.5 pt-1">
            {product.levelOfProtection && (
              <Badge variant="secondary">
                {product.levelOfProtection}
              </Badge>
            )}
            {product.season.map((s) => (
              <Badge key={s} variant="accent">
                {seasonEmojis[s] || ""} {s}
              </Badge>
            ))}
            {product.gender && (
              <Badge variant="outline">
                {product.gender}
              </Badge>
            )}
          </div>

          {/* Category - Subtle text at bottom */}
          {product.category && (
            <p className="text-xs text-muted-foreground pt-1">
              {product.category}
            </p>
          )}
        </CardContent>
      </Card>
    </Link>
  )
}
