import { getEvents } from "@/lib/notion"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { formatDate } from "@/lib/utils"

export default async function EventsPage() {
  const events = await getEvents()

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-4xl font-heading font-bold mb-2">Events</h1>
        <p className="text-muted-foreground">
          Join our community at upcoming events and meetups
        </p>
      </div>

      {events.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <p className="text-muted-foreground">
              No upcoming events at the moment. Check back soon!
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-6">
          {events.map((event) => (
            <Card key={event.id} className="overflow-hidden">
              <CardHeader>
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <CardTitle className="text-2xl">{event.name}</CardTitle>
                    <CardDescription className="text-base mt-1">
                      📅 {formatDate(event.startDate)}
                      {event.endDate && event.endDate !== event.startDate
                        ? ` - ${formatDate(event.endDate)}`
                        : ""}
                    </CardDescription>
                  </div>
                  <Badge variant="secondary" className="whitespace-nowrap">
                    {event.price}
                  </Badge>
                </div>
              </CardHeader>

              <CardContent className="space-y-4">
                <div>
                  <h3 className="font-semibold mb-1">📍 Location</h3>
                  <p className="text-muted-foreground">{event.location}</p>
                </div>

                {event.description && (
                  <div>
                    <h3 className="font-semibold mb-1">Description</h3>
                    <p className="text-muted-foreground">{event.description}</p>
                  </div>
                )}

                {event.url && (
                  <Button asChild>
                    <a href={event.url} target="_blank" rel="noopener noreferrer">
                      Learn More & Register
                    </a>
                  </Button>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
