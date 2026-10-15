"use client"

import { useEffect } from "react"
import { usePathname } from "next/navigation"

const SELECTOR = ".h-hero, .h-page, .h-section"

// Distance (px) from cursor to heading box. Inside the box -> 70. Upper bound of
// each outer band, from level 50 down to level 10; beyond the last bound: clean.
const LEVELS = [50, 35, 20, 10]
const DIST_BOUNDS = [40, 120, 240, 400]
const HYSTERESIS = 12

function levelForDistance(d: number): number {
  for (let i = 0; i < DIST_BOUNDS.length; i++) if (d <= DIST_BOUNDS[i]) return LEVELS[i]
  return 0
}

// Hysteresis applies to the outer bands only; the inside-the-box test is exact.
function levelWithHysteresis(d: number, inside: boolean, current: number): number {
  if (inside) return 70
  if (current === 70) return levelForDistance(d)
  const raw = levelForDistance(d)
  if (raw === current) return current
  if (raw < current) {
    // moving away: must pass the current band's outer bound by HYSTERESIS
    return d > DIST_BOUNDS[LEVELS.indexOf(current)] + HYSTERESIS ? levelForDistance(d - HYSTERESIS) : current
  }
  // moving closer: must pass the boundary into the new band by HYSTERESIS
  const inner = current === 0 ? DIST_BOUNDS[3] : DIST_BOUNDS[LEVELS.indexOf(current) - 1]
  return d < inner - HYSTERESIS ? levelForDistance(d + HYSTERESIS) : current
}

function current(el: HTMLElement): number {
  return Number(el.dataset.degrade ?? 0)
}

function apply(el: HTMLElement, level: number) {
  if (level === 0) {
    if (el.hasAttribute("data-degrade")) el.removeAttribute("data-degrade")
  } else if (el.dataset.degrade !== String(level)) {
    el.dataset.degrade = String(level)
  }
}

/**
 * Swaps Redaction heading cuts (clean, _10, _20, _35, _50, _70) by cursor
 * proximity. Pointer devices only: touch devices and prefers-reduced-motion
 * keep the clean cut (no listeners, no observers).
 * Mounted once in the root layout.
 */
export function DegradeOnScroll() {
  const pathname = usePathname()

  useEffect(() => {
    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)")
    const fine = window.matchMedia("(hover: hover) and (pointer: fine)")
    if (reduced.matches || !fine.matches) return

    let headings: HTMLElement[] = []
    const visible = new Set<HTMLElement>()
    let frame = 0
    let pointer: { x: number; y: number } | null = null

    const io = new IntersectionObserver((entries) => {
      for (const e of entries) {
        const el = e.target as HTMLElement
        if (e.isIntersecting) visible.add(el)
        else {
          visible.delete(el)
          apply(el, 0)
        }
      }
      schedule()
    })

    const scan = () => {
      const next = Array.from(document.querySelectorAll<HTMLElement>(SELECTOR))
      for (const el of headings) if (!next.includes(el)) { io.unobserve(el); visible.delete(el) }
      for (const el of next) if (!headings.includes(el)) io.observe(el)
      headings = next
    }

    const resetAll = () => {
      for (const el of headings) apply(el, 0)
    }

    const update = () => {
      frame = 0
      if (!pointer) return resetAll()
      const { x, y } = pointer
      for (const el of visible) {
        const r = el.getBoundingClientRect()
        const dx = Math.max(r.left - x, 0, x - r.right)
        const dy = Math.max(r.top - y, 0, y - r.bottom)
        apply(el, levelWithHysteresis(Math.hypot(dx, dy), dx === 0 && dy === 0, current(el)))
      }
    }

    function schedule() {
      if (!frame) frame = requestAnimationFrame(update)
    }

    const onPointerMove = (e: PointerEvent) => {
      if (e.pointerType !== "mouse" && e.pointerType !== "pen") return
      pointer = { x: e.clientX, y: e.clientY }
      schedule()
    }
    const onPointerLeave = () => {
      pointer = null
      schedule()
    }

    scan()
    schedule()

    // Client-rendered headings (filters, suggestion forms) appear after mount.
    const mo = new MutationObserver(() => {
      scan()
      schedule()
    })
    mo.observe(document.body, { childList: true, subtree: true })

    window.addEventListener("pointermove", onPointerMove, { passive: true })
    document.documentElement.addEventListener("pointerleave", onPointerLeave)
    window.addEventListener("scroll", schedule, { passive: true })
    window.addEventListener("resize", schedule, { passive: true })

    return () => {
      if (frame) cancelAnimationFrame(frame)
      io.disconnect()
      mo.disconnect()
      resetAll()
      window.removeEventListener("pointermove", onPointerMove)
      document.documentElement.removeEventListener("pointerleave", onPointerLeave)
      window.removeEventListener("scroll", schedule)
      window.removeEventListener("resize", schedule)
    }
  }, [pathname])

  return null
}
