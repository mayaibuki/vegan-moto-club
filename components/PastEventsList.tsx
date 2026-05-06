"use client"

import { useState } from "react"
import { ChevronLeft, ChevronRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import { EventCard } from "@/components/EventCard"
import type { Event } from "@/lib/notion"

const PAGE_SIZE = 12

export function PastEventsList({ events }: { events: Event[] }) {
  const [currentPage, setCurrentPage] = useState(1)

  const totalPages = Math.max(1, Math.ceil(events.length / PAGE_SIZE))
  const startIndex = (currentPage - 1) * PAGE_SIZE
  const paginated = events.slice(startIndex, startIndex + PAGE_SIZE)

  return (
    <>
      <div className="flex items-center justify-between">
        <h2 id="past-heading" className="text-2xl font-semibold text-muted-foreground">Past Events</h2>
        <p className="text-sm text-muted-foreground" aria-live="polite" aria-atomic="true">
          Showing{" "}
          <span className="font-semibold text-foreground">
            {events.length > 0 ? startIndex + 1 : 0}–{Math.min(startIndex + PAGE_SIZE, events.length)}
          </span>{" "}
          of {events.length} events
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {paginated.map((event) => (
          <EventCard key={event.id} event={event} muted />
        ))}
      </div>

      {totalPages > 1 && (
        <nav
          aria-label="Past events pagination"
          className="flex items-center justify-end gap-2 pt-6 border-t border-border"
        >
          <span className="sr-only">Page {currentPage} of {totalPages}</span>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setCurrentPage((p) => p - 1)}
            disabled={currentPage === 1}
            className="gap-1"
            aria-label="Go to previous page"
          >
            <ChevronLeft className="h-4 w-4" aria-hidden="true" />
            Previous
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setCurrentPage((p) => p + 1)}
            disabled={currentPage >= totalPages}
            className="gap-1"
            aria-label="Go to next page"
          >
            Next
            <ChevronRight className="h-4 w-4" aria-hidden="true" />
          </Button>
        </nav>
      )}
    </>
  )
}
