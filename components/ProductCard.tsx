import Link from "next/link"
import Image from "next/image"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card"
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
      <Card className="h-full hover:shadow-lg transition-shadow cursor-pointer overflow-hidden">
        {product.photos.length > 0 && (
          <div className="relative h-48 w-full bg-muted">
            <Image
              src={product.photos[0]}
              alt={product.name}
              fill
              className="object-cover"
              onError={(e) => {
                e.currentTarget.style.display = "none"
              }}
            />
          </div>
        )}

        <CardHeader className="pb-3">
          <div className="flex items-start justify-between gap-2">
            <div className="flex-1">
              <CardTitle className="text-lg font-heading line-clamp-2">{product.name}</CardTitle>
              <CardDescription className="text-xs font-sans">{product.brand}</CardDescription>
            </div>
            {product.staffFavorite && <Badge variant="default" className="bg-accent text-accent-foreground hover:bg-accent/90">⭐ Staff Pick</Badge>}
          </div>
        </CardHeader>

        <CardContent className="space-y-3">
          <div className="flex items-baseline justify-between">
            <span className="text-2xl font-bold">{formatPrice(product.price)}</span>
          </div>

          <div className="flex flex-wrap gap-1.5">
            {product.levelOfProtection && (
              <Badge variant="secondary" className="text-xs bg-secondary text-secondary-foreground">
                {product.levelOfProtection}
              </Badge>
            )}
            {product.season.map((s) => (
              <Badge key={s} variant="outline" className="text-xs bg-accent/20 border-accent/30 text-foreground">
                {seasonEmojis[s] || ""} {s}
              </Badge>
            ))}
            {product.gender && (
              <Badge variant="outline" className="text-xs bg-muted border-border text-foreground">
                {product.gender}
              </Badge>
            )}
          </div>

          {product.category && (
            <div className="text-sm text-muted-foreground">
              {product.category}
            </div>
          )}
        </CardContent>
      </Card>
    </Link>
  )
}
