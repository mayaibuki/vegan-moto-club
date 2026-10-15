"use client"

import { useEffect } from "react"
import { usePathname } from "next/navigation"

const SELECTOR = ".h-hero, .h-page, .h-section"

// Pointer: distance (px) from cursor to heading box. Upper bound of each band,
// from level 50 down to level 10; beyond the last bound the heading is clean.
const DIST_BOUNDS = [40, 120, 240, 400] // -> 50, 35, 20, 10
const HYSTERESIS = 12

function levelForDistance(d: number): number {
  if (d <= DIST_BOUNDS[0]) return 50
  if (d <= DIST_BOUNDS[1]) return 35
  if (d <= DIST_BOUNDS[2]) return 20
  if (d <= DIST_BOUNDS[3]) return 10
  return 0
}

// Distance at which the band for `level` ends on the far (cleaner) side.
function outerBound(level: number): number {
  return DIST_BOUNDS[[50, 35, 20, 10].indexOf(level)]
}

// Only change level once the distance has crossed a boundary by more than HYSTERESIS.
function levelWithHysteresis(d: number, current: number): number {
  const raw = levelForDistance(d)
  if (raw === current) return current
  if (raw < current) {
    // moving away: must pass the current band's outer bound by HYSTERESIS
    return d > outerBound(current) + HYSTERESIS ? levelForDistance(d - HYSTERESIS) : current
  }
  // moving closer: must pass the boundary into the new band by HYSTERESIS
  const inner = current === 0 ? DIST_BOUNDS[3] : DIST_BOUNDS[[50, 35, 20, 10].indexOf(current) - 1]
  return d < inner - HYSTERESIS ? levelForDistance(d + HYSTERESIS) : current
}

// Touch: heading top as a fraction of viewport height. Lower 60% clean; the top
// 40% splits into four equal bands, 10 -> 20 -> 35 -> 50 toward the top edge.
function levelForTop(top: number, vh: number): number {
  const r = top / vh
  if (r >= 0.4) return 0
  if (r >= 0.3) return 10
  if (r >= 0.2) return 20
  if (r >= 0.1) return 35
  return 50
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
 * Swaps Redaction heading cuts (clean, _10, _20, _35, _50).
 * Pointer devices: by cursor proximity. Touch devices: by scroll position.
 * Mounted once in the root layout. Does nothing under prefers-reduced-motion.
 */
export function DegradeOnScroll() {
  const pathname = usePathname()

  useEffect(() => {
    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)")
    const fine = window.matchMedia("(hover: hover) and (pointer: fine)")
    let headings: HTMLElement[] = []
    const visible = new Set<HTMLElement>()
    let frame = 0
    let pointer: { x: number; y: number } | null = null
    let scrolled = window.scrollY > 0

    const io = new IntersectionObserver((entries) => {
      for (const e of entries) {
        const el = e.target as HTMLElement
        if (e.isIntersecting) visible.add(el)
        else {
          visible.delete(el)
          if (fine.matches) apply(el, 0)
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
      if (reduced.matches) return resetAll()
      if (fine.matches) {
        if (!pointer) return resetAll()
        const { x, y } = pointer
        for (const el of visible) {
          const r = el.getBoundingClientRect()
          const dx = Math.max(r.left - x, 0, x - r.right)
          const dy = Math.max(r.top - y, 0, y - r.bottom)
          apply(el, levelWithHysteresis(Math.hypot(dx, dy), current(el)))
        }
      } else {
        const vh = window.innerHeight
        for (const el of headings) {
          apply(el, scrolled ? levelForTop(el.getBoundingClientRect().top, vh) : 0)
        }
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
    const onScroll = () => {
      if (window.scrollY > 0) scrolled = true
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
    window.addEventListener("scroll", onScroll, { passive: true })
    window.addEventListener("resize", schedule, { passive: true })
    reduced.addEventListener("change", schedule)
    fine.addEventListener("change", schedule)

    return () => {
      if (frame) cancelAnimationFrame(frame)
      io.disconnect()
      mo.disconnect()
      window.removeEventListener("pointermove", onPointerMove)
      document.documentElement.removeEventListener("pointerleave", onPointerLeave)
      window.removeEventListener("scroll", onScroll)
      window.removeEventListener("resize", schedule)
      reduced.removeEventListener("change", schedule)
      fine.removeEventListener("change", schedule)
    }
  }, [pathname])

  return null
}

