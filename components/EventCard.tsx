import Image from "next/image"
import { ArrowRight, MapPin } from "lucide-react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import type { Event } from "@/lib/notion"
import { cn, formatEventDay, formatEventMonth, isSameEventDay } from "@/lib/utils"

interface EventCardProps {
  event: Event
  muted?: boolean
}

function DateBlock({ date }: { date: string }) {
  return (
    <div
      className="flex size-12 flex-col items-center justify-center bg-foreground text-background"
      aria-hidden="true"
    >
      <span className="text-sm font-semibold leading-5">{formatEventMonth(date)}</span>
      <span className="text-2xl font-semibold leading-7">{formatEventDay(date)}</span>
    </div>
  )
}

export function EventCard({ event, muted = false }: EventCardProps) {
  const multiDay = !isSameEventDay(event.startDate, event.endDate)

  return (
    <article className={cn("h-full", muted && "opacity-60")}>
      <Card className="flex h-full flex-col gap-4 p-4">
        {/* Poster with overlays */}
        <div className="relative aspect-square w-full overflow-hidden rounded-xl bg-muted">
          {event.poster ? (
            <Image
              src={event.poster}
              alt={`${event.name} event poster`}
              fill
              sizes="(max-width: 768px) 100vw, (max-width: 1280px) 50vw, 33vw"
              className="object-cover"
            />
          ) : (
            <div
              className="absolute inset-0 flex items-center justify-center text-muted-foreground"
              aria-hidden="true"
            >
              No poster
            </div>
          )}

          <div className="pointer-events-none absolute inset-0 flex flex-col justify-between p-2">
            {/* Date overlay */}
            <div className="flex items-center gap-2">
              <DateBlock date={event.startDate} />
              {multiDay && (
                <>
                  <ArrowRight className="size-6 text-foreground" aria-hidden="true" />
                  <DateBlock date={event.endDate} />
                </>
              )}
              <span className="sr-only">
                {multiDay
                  ? `From ${event.startDate} to ${event.endDate}`
                  : `On ${event.startDate}`}
              </span>
            </div>

            {/* Price pill */}
            <div className="self-start rounded-full border border-border bg-card px-3.5 py-1 text-xs font-semibold text-foreground shadow-sm">
              {event.price}
            </div>
          </div>
        </div>

        {/* Heading */}
        <h3 className="text-xl font-semibold leading-7 tracking-tight text-foreground line-clamp-2">
          {event.name}
        </h3>

        {/* Location */}
        {event.location && (
          <p className="flex items-start gap-1.5 text-sm font-medium leading-5 text-muted-foreground">
            <MapPin className="mt-0.5 size-4 shrink-0" aria-hidden="true" />
            <span className="line-clamp-2">{event.location}</span>
          </p>
        )}

        {/* Description */}
        {event.description && (
          <p className="flex-1 text-base leading-6 text-foreground line-clamp-5">
            {event.description}
          </p>
        )}

        {/* CTA */}
        {event.url && (
          <Button asChild className="h-10 w-full rounded-full">
            <a
              href={event.url}
              target="_blank"
              rel="noopener noreferrer"
              aria-label={`Learn more about ${event.name} (opens in new tab)`}
            >
              Learn More
              <span className="sr-only"> (opens in new tab)</span>
            </a>
          </Button>
        )}
      </Card>
    </article>
  )
}
