import { memo } from "react"
import Link from "next/link"
import { Card, CardContent } from "./ui/card"
import { Badge } from "./ui/badge"
import { ProductCardImage } from "./ProductCardImage"
import { Product } from "@/lib/notion"
import { formatPrice } from "@/lib/utils"
import { seasonEmojis } from "@/lib/constants"

// Short protection labels for narrow mobile cards; the full text shows from sm up
// and is always available to screen readers.
const protectionShortLabels: Record<string, string> = {
  "Most protective": "Most",
  "Highly protective": "High",
  "Moderately protective": "Moderate",
  "Slightly protective": "Slight",
}

// Notion season values usually carry their emoji ("☀️ Summer"); older plain values
// ("Summer") get it from seasonEmojis. Returns the emoji and the bare name.
function splitSeason(season: string): { emoji: string; name: string } {
  const match = season.match(/^(\p{Extended_Pictographic}\uFE0F?)\s*(.+)$/u)
  if (match) return { emoji: match[1], name: match[2] }
  return { emoji: seasonEmojis[season] || "", name: season }
}

// Card badges are compact below sm and keep the default badge padding from sm up,
// so desktop cards are unchanged.
const cardBadge = "sm:px-3 sm:py-1"

interface ProductCardProps {
  product: Product
}

export const ProductCard = memo(function ProductCard({ product }: ProductCardProps) {
  return (
    <article className="h-full">
      <Link
        href={`/products/${product.slug}`}
        aria-label={`${product.name} by ${product.brand}, ${formatPrice(product.price)}${product.levelOfProtection ? `, ${product.levelOfProtection}` : ""}${product.staffFavorite ? ", Staff pick" : ""}`}
        className="group block h-full focus-ring rounded-2xl"
      >
        <Card className="h-full hover:shadow-lg transition-[box-shadow,transform] duration-200 cursor-pointer overflow-hidden motion-safe:group-active:scale-[0.98]">
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
            {product.staffFavorite && (
              <div className="absolute top-3 left-3">
                <Badge variant="default">Staff Pick</Badge>
              </div>
            )}
          </div>

          <CardContent className="p-3 space-y-2 sm:p-5 sm:space-y-3">
            <p className="text-xs font-medium text-muted-foreground">
              {product.brand}
            </p>

            <h3 className="font-semibold text-base leading-tight line-clamp-2">
              {product.name}
            </h3>

            <p className="text-xl font-bold text-foreground tabular-nums">
              {formatPrice(product.price)}
            </p>

            <ul role="list" className="flex flex-wrap gap-1.5 pt-1 list-none" aria-label="Product attributes">
              {product.levelOfProtection && (
                <li><Badge
                  size="sm"
                  className={`${cardBadge} whitespace-nowrap`}
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
                  <span className="sm:hidden" aria-hidden="true">
                    {protectionShortLabels[product.levelOfProtection] ?? product.levelOfProtection}
                  </span>
                  <span className="hidden sm:inline" aria-hidden="true">
                    {product.levelOfProtection}
                  </span>
                  <span className="sr-only">{product.levelOfProtection}</span>
                </Badge></li>
              )}
              {product.season.map((s, i) => {
                const { emoji, name } = splitSeason(s)
                const more = product.season.length - 1
                return (
                  <li key={s} className={i > 0 ? "hidden sm:block" : undefined}>
                    <Badge size="sm" variant="outline" className={`${cardBadge} whitespace-nowrap`}>
                      <span className="hidden sm:inline">{s}</span>
                      {/* Below sm: the first season as its emoji plus "+N" for the rest,
                          so the attribute row stays on one line */}
                      {i === 0 && (
                        <span className="sm:hidden">
                          <span aria-hidden="true">
                            {emoji || name}
                            {more > 0 && ` +${more}`}
                          </span>
                          <span className="sr-only">{product.season.map((x) => splitSeason(x).name).join(", ")}</span>
                        </span>
                      )}
                    </Badge>
                  </li>
                )
              })}
              {product.gender && (
                <li className="hidden sm:block"><Badge size="sm" variant="outline" className={cardBadge}>
                  {product.gender}
                </Badge></li>
              )}
            </ul>

          </CardContent>
        </Card>
      </Link>
    </article>
  )
})
