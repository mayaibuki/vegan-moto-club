import Image from "next/image"
import { ArrowRight } from "lucide-react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import type { Event } from "@/lib/notion"
import { cn, formatDate, formatEventDay, formatEventMonth, isSameEventDay, notionImageUrl } from "@/lib/utils"

interface EventCardProps {
  event: Event
  muted?: boolean
}

function DateBlock({ date }: { date: string }) {
  return (
    <div
      className="flex size-12 flex-col items-center justify-center rounded-md bg-foreground text-background shadow-sm"
      aria-hidden="true"
    >
      <span className="text-sm font-semibold leading-5">{formatEventMonth(date)}</span>
      <span className="text-2xl font-semibold leading-7">{formatEventDay(date)}</span>
    </div>
  )
}

export function EventCard({ event, muted = false }: EventCardProps) {
  const multiDay = !isSameEventDay(event.startDate, event.endDate)

  const dates = (
    <div className="flex items-center gap-2">
      <DateBlock date={event.startDate} />
      {multiDay && (
        <>
          <ArrowRight className="size-6 text-foreground" aria-hidden="true" />
          <DateBlock date={event.endDate} />
        </>
      )}
      {muted && (
        <span className="rounded-full bg-card px-2 py-0.5 text-xs font-semibold text-muted-foreground">
          Past
        </span>
      )}
      <span className="sr-only">
        {multiDay
          ? `From ${formatDate(event.startDate)} to ${formatDate(event.endDate)}`
          : `On ${formatDate(event.startDate)}`}
      </span>
    </div>
  )

  const price = (
    <div className="self-start rounded-full border border-border bg-card px-3.5 py-1 text-xs font-semibold text-foreground shadow-sm">
      {event.price}
    </div>
  )

  return (
    <article className="h-full">
      <Card className="flex h-full flex-col gap-4 p-4 transition-[transform,box-shadow] duration-200 hover:-translate-y-0.5 hover:shadow-md">
        {event.poster ? (
          /* Poster with overlays: 4:3 on phones, square from sm up */
          <div className="relative aspect-4/3 w-full overflow-hidden rounded-xl bg-muted sm:aspect-square">
            <div className={cn("absolute inset-0", muted && "opacity-60 grayscale")}>
              <Image
                src={notionImageUrl(event.poster, 600)}
                alt={`${event.name} event poster`}
                fill
                sizes="(max-width: 768px) 100vw, (max-width: 1280px) 50vw, 33vw"
                className="object-cover"
                unoptimized={event.poster.startsWith("/api/notion-image")}
              />
            </div>
            {/* Hairline outline so light posters keep an edge against the card */}
            <div className="pointer-events-none absolute inset-0 rounded-xl ring-1 ring-inset ring-foreground/10" aria-hidden="true" />
            <div className="pointer-events-none absolute inset-0 flex flex-col justify-between p-2">
              {dates}
              {price}
            </div>
          </div>
        ) : (
          /* No poster: a compact row instead of an empty square */
          <div className="flex flex-wrap items-center justify-between gap-3">
            {dates}
            {price}
          </div>
        )}

        {/* Heading */}
        <h3 className="text-xl font-semibold leading-7 text-foreground line-clamp-2 text-balance">
          {event.name}
        </h3>

        {/* Location */}
        {event.location && (
          <p className="text-sm font-medium leading-5 text-muted-foreground line-clamp-2">
            {event.location}
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
          <Button asChild className="w-full">
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
