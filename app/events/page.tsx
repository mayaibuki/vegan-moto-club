import { getEvents } from "@/lib/notion"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { formatDate } from "@/lib/utils"

export default async function EventsPage() {
  const events = await getEvents()

  return (
    <div className="space-y-10">
      <div className="space-y-2">
        <h1 className="text-3xl md:text-4xl font-bold">Events</h1>
        <p className="text-lg text-muted-foreground">
          Join our community at upcoming events and meetups
        </p>
      </div>

      {events.length === 0 ? (
        <Card>
          <CardContent className="py-16 text-center">
            <p className="text-lg text-muted-foreground">
              No upcoming events at the moment. Check back soon!
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-6">
          {events.map((event) => (
            <Card key={event.id} className="overflow-hidden">
              <CardHeader className="pb-4">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 space-y-1">
                    <CardTitle className="text-xl md:text-2xl">{event.name}</CardTitle>
                    <CardDescription className="text-base">
                      📅 {formatDate(event.startDate)}
                      {event.endDate && event.endDate !== event.startDate
                        ? ` - ${formatDate(event.endDate)}`
                        : ""}
                    </CardDescription>
                  </div>
                  <Badge variant="secondary" className="whitespace-nowrap shrink-0">
                    {event.price}
                  </Badge>
                </div>
              </CardHeader>

              <CardContent className="space-y-4">
                <div>
                  <p className="text-sm font-medium mb-1">📍 Location</p>
                  <p className="text-muted-foreground">{event.location}</p>
                </div>

                {event.description && (
                  <div>
                    <p className="text-sm font-medium mb-1">Description</p>
                    <p className="text-muted-foreground">{event.description}</p>
                  </div>
                )}

                {event.url && (
                  <div className="pt-2">
                    <Button asChild>
                      <a href={event.url} target="_blank" rel="noopener noreferrer">
                        Learn More & Register
                      </a>
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
