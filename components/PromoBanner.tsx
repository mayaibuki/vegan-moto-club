"use client"

import Link from "next/link"
import { Tag, X } from "lucide-react"
import { useEffect, useState, useCallback, useRef } from "react"
import { Button } from "./ui/button"

const STORAGE_KEY = "promo-bellissimoto-dismissed"
const WRAPPER_ID = "promo-banner"

// Runs while the HTML is parsed, before first paint, so visitors who already
// dismissed the banner never see it. It sets the hidden attribute as well as
// display:none (the grid utility would override [hidden]) so parent space-y-*
// utilities skip the wrapper and the gap does not jump when React later
// unmounts it. The banner itself is server-rendered, so first-time visitors
// get it in the initial layout (no shift after hydration).
const PRE_PAINT_SCRIPT = `try{if(localStorage.getItem("${STORAGE_KEY}")==="true"){var e=document.getElementById("${WRAPPER_ID}");e.hidden=true;e.style.display="none"}}catch(e){}`

export function PromoBanner() {
  const [dismissed, setDismissed] = useState(false)
  const [closing, setClosing] = useState(false)
  const wrapperRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    try {
      if (localStorage.getItem(STORAGE_KEY) === "true") setDismissed(true)
    } catch {}
  }, [])

  const handleDismiss = useCallback(() => {
    try {
      localStorage.setItem(STORAGE_KEY, "true")
    } catch {}
    const el = wrapperRef.current
    // Collapse first, unmount on transitionend. With no transition (reduced
    // motion sets the duration to ~0, or the element is not rendered) remove at once.
    const duration = el ? parseFloat(getComputedStyle(el).transitionDuration) : 0
    if (!el || !(duration > 0.001)) {
      setDismissed(true)
      return
    }
    setClosing(true)
  }, [])

  const handleTransitionEnd = useCallback((e: React.TransitionEvent<HTMLDivElement>) => {
    if (e.target === e.currentTarget && e.propertyName === "grid-template-rows") setDismissed(true)
  }, [])

  if (dismissed) return null

  return (
    // Collapse wrapper: a one-row grid whose row animates from 1fr to 0fr (300ms),
    // then the banner unmounts on transitionend.
    <div
      ref={wrapperRef}
      id={WRAPPER_ID}
      data-state={closing ? "closed" : "open"}
      suppressHydrationWarning
      onTransitionEnd={handleTransitionEnd}
      className={`grid transition-[grid-template-rows] duration-300 ${closing ? "grid-rows-closed" : "grid-rows-open"}`}
    >
      <div className={`min-h-0 overflow-hidden transition-opacity duration-300 ${closing ? "opacity-0" : "opacity-100"}`}>
        <div
          role="region"
          aria-label="Promotion"
          className="relative rounded-2xl border border-border border-l-4 border-l-primary bg-card text-card-foreground px-4 py-3 pr-12 sm:p-5 sm:pr-16 shadow-sm"
        >
          <div className="flex flex-col sm:flex-row sm:items-center gap-1 sm:gap-4">
            <Tag className="h-5 w-5 text-primary-text flex-shrink-0 hidden sm:block" aria-hidden="true" />
            <p className="text-sm sm:text-base text-foreground">
              Members get 15% off Virus Power via Bellissimoto.com. Promo Code: VEGANMC
            </p>
            {/* Mobile: compact text link. -my-2 keeps its 44px tap area without adding height. */}
            <Button asChild variant="link" size="xs" className="-my-2 self-start px-0 text-sm sm:hidden">
              <Link href="/products?brand=Virus+Power">View Virus Power Suits</Link>
            </Button>
            <Button asChild variant="outline" size="xs" className="hidden flex-shrink-0 sm:ml-auto sm:inline-flex">
              <Link href="/products?brand=Virus+Power">View Virus Power Suits</Link>
            </Button>
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={handleDismiss}
            disabled={closing}
            aria-label="Dismiss promotion"
            className="absolute top-0 right-0 sm:top-1/2 sm:right-2 sm:-translate-y-1/2"
          >
            <X className="h-5 w-5" aria-hidden="true" />
          </Button>
        </div>
      </div>
      <script dangerouslySetInnerHTML={{ __html: PRE_PAINT_SCRIPT }} />
    </div>
  )
}
