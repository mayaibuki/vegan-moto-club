import type { Metadata } from "next"
import { getEvents } from "@/lib/notion"
import { Card, CardContent } from "@/components/ui/card"
import { EventCard } from "@/components/EventCard"
import { SuggestEventForm } from "@/components/SuggestEventForm"

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
