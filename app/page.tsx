import { getProducts, getEvents } from "@/lib/notion"
import { ProductCard } from "@/components/ProductCard"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Logo } from "@/components/Logo"
import Image from "next/image"
import Link from "next/link"
import { formatDate, formatRelativeDate } from "@/lib/utils"
import { Check } from "lucide-react"

const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || "https://veganmotoclub.com"

const jsonLd = {
  "@context": "https://schema.org",
  "@type": "WebSite",
  name: "Vegan Moto Club",
  url: siteUrl,
  description:
    "A curated database of vegan motorcycle gear for compassionate riders. Find ethical alternatives to animal-based protective wear.",
  potentialAction: {
    "@type": "SearchAction",
    target: {
      "@type": "EntryPoint",
      urlTemplate: `${siteUrl}/products?search={search_term_string}`,
    },
    "query-input": "required name=search_term_string",
  },
}

export default async function Home() {
  const products = await getProducts()
  const events = await getEvents()

  const staffPicks = products
    .filter((p) => p.staffFavorite)
    .sort(() => Math.random() - 0.5)
    .slice(0, 8)
  const upcomingEvents = events.slice(0, 5)
  const lastUpdated = products.reduce((latest, p) =>
    p.lastEditedTime > latest ? p.lastEditedTime : latest, products[0]?.lastEditedTime || ""
  )

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <div className="space-y-16">
        {/* Hero Section */}
      <section className="py-16 md:py-24 bg-gradient-to-br from-secondary/20 via-accent/10 to-background rounded-3xl p-10 md:p-16">
        <div className="flex flex-col lg:flex-row lg:items-center lg:gap-12">
          {/* Left Column — Text Content */}
          <div className="flex-1 text-center lg:text-left space-y-8">
            {/* Last Updated Badge */}
            <div className="flex items-center gap-2 justify-center lg:justify-start">
              <span className="inline-flex items-center gap-2 rounded-full border border-border bg-background/80 px-4 py-1.5 text-sm text-muted-foreground">
                <span className="h-2 w-2 rounded-full bg-primary" />
                Last updated: <span className="font-semibold text-foreground">{formatRelativeDate(lastUpdated)}</span>
              </span>
            </div>

            <h1 className="text-4xl md:text-6xl font-bold tracking-tight">
              Ride motorcycles, not animals
            </h1>

            <ul className="space-y-3 text-lg text-muted-foreground mx-auto lg:mx-0 max-w-2xl">
              <li className="flex items-center gap-3 justify-center lg:justify-start">
                <Check className="h-5 w-5 text-primary flex-shrink-0" />
                Find vegan motorcycle gear
              </li>
              <li className="flex items-center gap-3 justify-center lg:justify-start">
                <Check className="h-5 w-5 text-primary flex-shrink-0" />
                Discover bike events
              </li>
              <li className="flex items-center gap-3 justify-center lg:justify-start">
                <Check className="h-5 w-5 text-primary flex-shrink-0" />
                Connect with other riders
              </li>
            </ul>

            <div className="flex flex-col sm:flex-row gap-5 justify-center lg:justify-start pt-4">
              <Button size="lg" asChild>
                <Link href="/products">Browse Products</Link>
              </Button>
              <Button size="lg" variant="outline" asChild>
                <Link href="https://discord.gg/GN4jkBRnut">Join our Discord</Link>
              </Button>
            </div>
          </div>

          {/* Right Column — Hero Image (hidden on mobile, shown on lg+) */}
          <div className="hidden lg:block flex-1 mt-12 lg:mt-0">
            <div className="relative aspect-[4/5] rounded-2xl overflow-hidden">
              <Image
                src="/images/hero.jpg"
                alt="Vegan Moto Club riders on a Ducati motorcycle with a Protect Animals sign at an animal rights rally"
                fill
                className="object-cover"
                priority
                sizes="(min-width: 1024px) 50vw, 100vw"
              />
            </div>
          </div>
        </div>
      </section>

      {/* Featured Products Section */}
      <section aria-labelledby="staff-picks-heading">
        <div className="flex items-center justify-between mb-10">
          <div className="space-y-1">
            <h2 id="staff-picks-heading" className="text-3xl font-bold tracking-tight">Staff Picks</h2>
            <p className="text-muted-foreground text-lg">Our favorite vegan motorcycle gear</p>
          </div>
          <Button variant="outline" asChild>
            <Link href="/products">View All →</Link>
          </Button>
        </div>

        {staffPicks.length === 0 ? (
          <Card>
            <CardContent className="py-12">
              <p className="text-center text-muted-foreground text-lg">
                No staff picks available yet. Check back soon!
              </p>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-8">
            {staffPicks.map((product, index) => (
              <div key={product.id} className={index >= 6 ? "hidden lg:block" : undefined}>
                <ProductCard product={product} />
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Upcoming Events Section */}
      {upcomingEvents.length > 0 && (
        <section aria-labelledby="upcoming-events-heading">
          <div className="flex items-center justify-between mb-10">
            <div className="space-y-1">
              <h2 id="upcoming-events-heading" className="text-3xl font-bold tracking-tight">Upcoming Events</h2>
              <p className="text-muted-foreground text-lg">Join the community</p>
            </div>
            <Button variant="outline" asChild>
              <Link href="/events">View All →</Link>
            </Button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {upcomingEvents.map((event) => (
              <Card key={event.id}>
                <CardHeader>
                  <CardTitle className="text-xl">{event.name}</CardTitle>
                  <CardDescription className="text-base">
                    {formatDate(event.startDate)}
                    {event.endDate && event.endDate !== event.startDate
                      ? ` - ${formatDate(event.endDate)}`
                      : ""}
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <p className="text-sm font-medium"><span aria-hidden="true">📍</span> Location</p>
                    <p className="text-muted-foreground">{event.location}</p>
                  </div>
                  {event.description && (
                    <div>
                      <p className="text-sm font-medium">Description</p>
                      <p className="text-muted-foreground line-clamp-2">
                        {event.description}
                      </p>
                    </div>
                  )}
                  <div className="flex items-center justify-between pt-3">
                    <Badge variant="outline">{event.price}</Badge>
                    {event.url && (
                      <Button size="sm" asChild>
                        <a
                          href={event.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          aria-label={`Learn more about ${event.name} (opens in new tab)`}
                        >
                          Learn More<span className="sr-only"> (opens in new tab)</span>
                        </a>
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </section>
      )}

      {/* Product Suggestion Form Section */}
      <section className="rounded-3xl p-10 md:p-14" aria-labelledby="suggest-product-heading">
        <h2 id="suggest-product-heading" className="text-3xl font-bold tracking-tight mb-3">Suggest a Product</h2>
        <p className="text-muted-foreground text-lg mb-8">
          Know a great vegan motorcycle product? Tell us about it!
        </p>
        <div className="rounded-2xl overflow-hidden border border-border/50">
          <iframe
            src="https://veganmotoclub.notion.site/ebd//19c439de397b80e99216c28ebd83a771"
            width="100%"
            height="600"
            frameBorder="0"
            allowFullScreen
            title="Product suggestion form - Submit vegan motorcycle gear recommendations"
          />
        </div>
      </section>
      </div>
    </>
  )
}
