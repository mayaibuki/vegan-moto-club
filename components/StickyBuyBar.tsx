"use client"

import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

interface StickyBuyBarProps {
  /** id of the inline store button; the bar shows once it has scrolled off the top */
  targetId: string
  price: string
  url: string
  productName: string
}

/**
 * Mobile-only (below md) bar with the price and the store button, fixed to the
 * bottom of the viewport once the inline "View on Store" button scrolls away.
 * globals.css pads the body while it is on the page so it never covers the
 * footer's last line.
 */
export function StickyBuyBar({ targetId, price, url, productName }: StickyBuyBarProps) {
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    const target = document.getElementById(targetId)
    if (!target) return
    // The root is stretched far below the viewport, so the button only stops
    // intersecting once it has scrolled off the top. A plain viewport root
    // would also report "not intersecting" while the button is still below
    // the fold, and misses jumps from below the fold to above it.
    const observer = new IntersectionObserver(
      ([entry]) => setVisible(!entry.isIntersecting),
      { rootMargin: "0px 0px 10000% 0px" }
    )
    observer.observe(target)
    return () => observer.disconnect()
  }, [targetId])

  return (
    <div
      data-sticky-buy-bar=""
      aria-hidden={!visible}
      className={cn(
        "fixed inset-x-0 bottom-0 z-sticky border-t border-border bg-card/95 backdrop-blur px-4 pt-3 pb-safe-3 md:hidden",
        "motion-safe:transition-transform motion-safe:duration-200",
        visible ? "translate-y-0" : "translate-y-full"
      )}
    >
      <div className="flex items-center justify-between gap-4">
        <p className="text-xl font-bold tabular-nums">{price}</p>
        <Button size="lg" asChild>
          <a
            href={url}
            target="_blank"
            rel="noopener noreferrer"
            tabIndex={visible ? undefined : -1}
            aria-label={`View ${productName} on store website (opens in new tab)`}
          >
            View on Store
          </a>
        </Button>
      </div>
    </div>
  )
}
