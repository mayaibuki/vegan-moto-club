import { getProducts, getEvents } from "@/lib/notion"
import { ProductCard } from "@/components/ProductCard"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Logo } from "@/components/Logo"
import Link from "next/link"
import { formatDate } from "@/lib/utils"

export default async function Home() {
  const products = await getProducts()
  const events = await getEvents()

  const staffPicks = products.filter((p) => p.staffFavorite).slice(0, 6)
  const upcomingEvents = events.slice(0, 5)

  return (
    <div className="space-y-12">
      {/* Hero Section */}
      <section className="py-12 md:py-20 text-center space-y-6 bg-gradient-to-br from-secondary/10 via-accent/5 to-background rounded-lg p-8 md:p-12">
        <div className="flex justify-center mb-6">
          <Logo size="lg" />
        </div>
        <div>
          <h1 className="text-4xl md:text-5xl font-heading font-bold mb-2">
            Vegan Moto Club
          </h1>
          <p className="text-lg text-muted-foreground font-semibold">
            100% Cruelty-Free Motorcycle Gear Database
          </p>
        </div>
        <p className="text-lg text-foreground max-w-2xl mx-auto leading-relaxed">
          Discover ethical and cruelty-free motorcycle gear. We curate the best vegan alternatives for every riding style, protection level, and budget.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Button size="lg" asChild>
            <Link href="/products">Browse Products</Link>
          </Button>
          <Button size="lg" variant="outline" asChild>
            <Link href="/about">Learn More</Link>
          </Button>
        </div>
      </section>

      {/* Featured Products Section */}
      <section>
        <div className="flex items-center justify-between mb-8">
          <div>
            <h2 className="text-3xl font-bold">Staff Picks</h2>
            <p className="text-muted-foreground">Our favorite vegan motorcycle gear</p>
          </div>
          <Button variant="outline" asChild>
            <Link href="/products">View All →</Link>
          </Button>
        </div>

        {staffPicks.length === 0 ? (
          <Card>
            <CardContent className="py-8">
              <p className="text-center text-muted-foreground">
                No staff picks available yet. Check back soon!
              </p>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {staffPicks.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        )}
      </section>

      {/* Upcoming Events Section */}
      {upcomingEvents.length > 0 && (
        <section>
          <div className="flex items-center justify-between mb-8">
            <div>
              <h2 className="text-3xl font-bold">Upcoming Events</h2>
              <p className="text-muted-foreground">Join the community</p>
            </div>
            <Button variant="outline" asChild>
              <Link href="/events">View All →</Link>
            </Button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {upcomingEvents.map((event) => (
              <Card key={event.id}>
                <CardHeader>
                  <CardTitle>{event.name}</CardTitle>
                  <CardDescription>
                    {formatDate(event.startDate)}
                    {event.endDate && event.endDate !== event.startDate
                      ? ` - ${formatDate(event.endDate)}`
                      : ""}
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div>
                    <p className="text-sm font-medium">📍 Location</p>
                    <p className="text-sm text-muted-foreground">{event.location}</p>
                  </div>
                  {event.description && (
                    <div>
                      <p className="text-sm font-medium">Description</p>
                      <p className="text-sm text-muted-foreground line-clamp-2">
                        {event.description}
                      </p>
                    </div>
                  )}
                  <div className="flex items-center justify-between pt-2">
                    <Badge variant="outline">{event.price}</Badge>
                    {event.url && (
                      <Button size="sm" asChild>
                        <a href={event.url} target="_blank" rel="noopener noreferrer">
                          Learn More
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
      <section className="bg-muted rounded-lg p-8 md:p-12">
        <h2 className="text-3xl font-bold mb-4">Suggest a Product</h2>
        <p className="text-muted-foreground mb-6">
          Know a great vegan motorcycle gear brand? Tell us about it!
        </p>
        <iframe
          src="https://veganmotoclub.notion.site/ebd//19c439de397b80e99216c28ebd83a771"
          width="100%"
          height="600"
          frameBorder="0"
          allowFullScreen
        />
      </section>
    </div>
  )
}
