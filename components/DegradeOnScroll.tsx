"use client"

import { useEffect } from "react"
import { usePathname } from "next/navigation"

const SELECTOR = ".h-hero, .h-page, .h-section"

// Heading top position (as a fraction of viewport height) -> pixelation level.
// Lower 60% of the viewport: clean. Top 40%: three equal bands, 10 -> 20 -> 35
// as the heading rises toward the top edge.
function levelFor(top: number, vh: number): string {
  const r = top / vh
  if (r >= 0.4) return "0"
  if (r >= 0.4 * (2 / 3)) return "10"
  if (r >= 0.4 / 3) return "20"
  return "35"
}

/**
 * Swaps Redaction heading cuts (clean, _10, _20, _35) as the visitor scrolls.
 * Mounted once in the root layout. Does nothing under prefers-reduced-motion.
 */
export function DegradeOnScroll() {
  const pathname = usePathname()

  useEffect(() => {
    const media = window.matchMedia("(prefers-reduced-motion: reduce)")
    let headings: HTMLElement[] = []
    let frame = 0
    // Until the visitor scrolls, every heading stays clean (no pixelation flash on load).
    let scrolled = false

    const scan = () => {
      headings = Array.from(document.querySelectorAll<HTMLElement>(SELECTOR))
    }

    const reset = () => {
      for (const el of document.querySelectorAll<HTMLElement>("[data-degrade]")) {
        el.removeAttribute("data-degrade")
      }
    }

    const update = () => {
      frame = 0
      if (media.matches) return
      const vh = window.innerHeight
      for (const el of headings) {
        const level = scrolled ? levelFor(el.getBoundingClientRect().top, vh) : "0"
        if (level === "0") {
          if (el.hasAttribute("data-degrade")) el.removeAttribute("data-degrade")
        } else if (el.dataset.degrade !== level) {
          el.dataset.degrade = level
        }
      }
    }

    const schedule = () => {
      if (!frame) frame = requestAnimationFrame(update)
    }

    const onScroll = () => {
      if (window.scrollY > 0) scrolled = true
      schedule()
    }

    const onMotionChange = () => {
      if (media.matches) reset()
      else schedule()
    }

    scan()
    scrolled = window.scrollY > 0
    schedule()

    // Client-rendered headings (filters, suggestion forms) appear after mount.
    const observer = new MutationObserver(() => {
      scan()
      schedule()
    })
    observer.observe(document.body, { childList: true, subtree: true })

    window.addEventListener("scroll", onScroll, { passive: true })
    window.addEventListener("resize", schedule, { passive: true })
    media.addEventListener("change", onMotionChange)

    return () => {
      if (frame) cancelAnimationFrame(frame)
      observer.disconnect()
      window.removeEventListener("scroll", onScroll)
      window.removeEventListener("resize", schedule)
      media.removeEventListener("change", onMotionChange)
    }
  }, [pathname])

  return null
}
