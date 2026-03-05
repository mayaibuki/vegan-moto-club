import type { Metadata } from "next"
import { getEvents } from "@/lib/notion"
import type { Event } from "@/lib/notion"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { formatDate } from "@/lib/utils"
import { SuggestEventForm } from "@/components/SuggestEventForm"

function EventCard({ event, muted = false }: { event: Event; muted?: boolean }) {
  return (
    <Card className={muted ? "opacity-60" : undefined}>
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
          <p className="text-sm font-medium">Location</p>
          <p className="text-muted-foreground">{event.location}</p>
        </div>
        {event.description && (
          <div>
            <p className="text-sm font-medium">Description</p>
            <p className="text-muted-foreground line-clamp-2">{event.description}</p>
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
  )
}

export const metadata: Metadata = {
  title: "Events",
  description:
    "Join the Vegan Moto Club community at upcoming events, meetups, and rides. Connect with compassionate riders worldwide.",
  openGraph: {
    title: "Events | Vegan Moto Club",
    description:
      "Join the Vegan Moto Club community at upcoming events, meetups, and rides. Connect with compassionate riders worldwide.",
    url: "/events",
  },
  alternates: {
    canonical: "/events",
  },
}

export default async function EventsPage() {
  const rawEvents = await getEvents()

  const oneWeekAgo = new Date()
  oneWeekAgo.setDate(oneWeekAgo.getDate() - 7)

  const upcomingEvents = rawEvents
    .filter((e) => new Date(e.startDate) >= oneWeekAgo)
    .sort((a, b) => new Date(a.startDate).getTime() - new Date(b.startDate).getTime())

  const pastEvents = rawEvents
    .filter((e) => new Date(e.startDate) < oneWeekAgo)
    .sort((a, b) => new Date(b.startDate).getTime() - new Date(a.startDate).getTime())

  const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || "https://veganmotoclub.com"

  const allEvents = [...upcomingEvents, ...pastEvents]

  const eventsJsonLd = {
    "@context": "https://schema.org",
    "@type": "ItemList",
    itemListElement: allEvents.map((event, index) => ({
      "@type": "ListItem",
      position: index + 1,
      item: {
        "@type": "Event",
        name: event.name,
        startDate: event.startDate,
        ...(event.endDate && { endDate: event.endDate }),
        location: {
          "@type": "Place",
          name: event.location,
        },
        description: event.description || undefined,
        url: event.url || undefined,
        organizer: {
          "@type": "Organization",
          name: "Vegan Moto Club",
          url: siteUrl,
        },
      },
    })),
  }

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(eventsJsonLd) }}
      />
      <div className="space-y-10">
          <div className="space-y-2">
            <h1 className="text-3xl md:text-4xl font-bold">Events</h1>
            <p className="text-lg text-muted-foreground">
              Join our community at upcoming events and meetups
            </p>
          </div>

          {/* Upcoming Events */}
          <section aria-labelledby="upcoming-heading" className="space-y-6">
            <h2 id="upcoming-heading" className="text-2xl font-semibold">Upcoming Events</h2>
            {upcomingEvents.length === 0 ? (
              <Card>
                <CardContent className="py-12 text-center">
                  <p className="text-muted-foreground">No upcoming events at the moment. Check back soon!</p>
                </CardContent>
              </Card>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                {upcomingEvents.map((event) => (
                  <EventCard key={event.id} event={event} />
                ))}
              </div>
            )}
          </section>

          <SuggestEventForm />

          {/* Past Events */}
          {pastEvents.length > 0 && (
            <section aria-labelledby="past-heading" className="space-y-6">
              <h2 id="past-heading" className="text-2xl font-semibold text-muted-foreground">Past Events</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                {pastEvents.map((event) => (
                  <EventCard key={event.id} event={event} muted />
                ))}
              </div>
            </section>
          )}
        </div>
    </>
  )
}
