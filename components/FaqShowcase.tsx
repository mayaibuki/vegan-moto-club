"use client"

import { useEffect, useId, useRef, useState, type AnimationEvent } from "react"
import Image from "next/image"
import { ChevronDown } from "lucide-react"
import type { FaqItem } from "@/lib/notion"
import { JsonLd } from "@/components/JsonLd"
import { faqPageJsonLd } from "@/lib/seo"
import { cn, notionImageUrl } from "@/lib/utils"

/** Shown for rows that have no Featured image in Notion yet. */
const FALLBACK_IMAGE = "/images/hero.jpg"

/** React 18 only renders `inert` as a string attribute ("" turns it on), while
 *  @types/react 18.3 types it as boolean, so the cast lives here once. */
const INERT = { inert: "" } as unknown as { inert?: boolean }

interface FaqShowcaseProps {
  items: FaqItem[]
  title?: string
  /** Emit FAQPage JSON-LD for these items (one block per page). */
  withSchema?: boolean
  id?: string
}

function useMediaQuery(query: string): boolean {
  const [matches, setMatches] = useState(false)
  useEffect(() => {
    const mql = window.matchMedia(query)
    const update = () => setMatches(mql.matches)
    update()
    mql.addEventListener("change", update)
    return () => mql.removeEventListener("change", update)
  }, [query])
  return matches
}

function imageProps(item: FaqItem, width: 600 | 1200) {
  const src = item.image || FALLBACK_IMAGE
  return { src: notionImageUrl(src, width), unoptimized: src.startsWith("/api/notion-image") }
}

/**
 * Progressive-disclosure FAQ for the home page: one question open at a time.
 * From lg up, a photo column sits beside the list and crossfades to the open
 * question's image, and the list auto-advances every --duration-dwell while it
 * is on screen. The progress fill's CSS animation is the timer (animationend
 * opens the next item), so pausing is just animation-play-state. Below lg each
 * open panel shows its own image and nothing advances on its own.
 *
 * Every answer stays in the server HTML (collapsed panels are inert, not
 * removed), and the JSON-LD is built from the same items.
 */
export function FaqShowcase({ items, title = "Common Questions", withSchema = true, id = "faq" }: FaqShowcaseProps) {
  const [active, setActive] = useState(0)
  const [takenOver, setTakenOver] = useState(false)
  const [hovered, setHovered] = useState(false)
  const [focused, setFocused] = useState(false)
  const [inView, setInView] = useState(false)
  const sectionRef = useRef<HTMLElement>(null)
  const uid = useId()

  const isLarge = useMediaQuery("(min-width: 1024px)")
  const reducedMotion = useMediaQuery("(prefers-reduced-motion: reduce)")
  // Reduced motion must switch autoplay off entirely: globals.css shortens every
  // animation to 0.01ms there, which would make the items cycle instantly.
  const autoplay = isLarge && !reducedMotion && !takenOver && items.length > 1
  const running = autoplay && inView && !hovered && !focused

  useEffect(() => {
    const node = sectionRef.current
    if (!node) return
    const observer = new IntersectionObserver(([entry]) => setInView(entry.isIntersecting), { threshold: 0.3 })
    observer.observe(node)
    return () => observer.disconnect()
  }, [])

  if (items.length === 0) return null

  const headingId = `${id}-heading`

  function choose(index: number) {
    setActive(index)
    setTakenOver(true)
  }

  function handleProgressEnd(event: AnimationEvent<HTMLDivElement>) {
    if (event.target !== event.currentTarget) return
    setActive((current) => (current + 1) % items.length)
  }

  return (
    <section
      ref={sectionRef}
      aria-labelledby={headingId}
      className="space-y-8"
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      onFocus={() => setFocused(true)}
      onBlur={(event) => {
        if (!event.currentTarget.contains(event.relatedTarget as Node | null)) setFocused(false)
      }}
    >
      {withSchema && <JsonLd data={faqPageJsonLd(items)} />}
      <h2 id={headingId} className="h-section">
        {title}
      </h2>

      <div className="grid gap-8 lg:grid-cols-2 lg:items-start lg:gap-16">
        {/* Photo column (lg+): every image stacked, the open question's one visible */}
        <div className="hidden lg:sticky lg:top-24 lg:block">
          <div className="relative aspect-square overflow-hidden rounded-2xl bg-muted">
            {items.map((item, index) => (
              <Image
                key={item.question}
                {...imageProps(item, 1200)}
                alt=""
                fill
                sizes="(min-width: 1024px) 50vw, 100vw"
                className={cn(
                  "object-cover transition-opacity duration-300",
                  index === active ? "opacity-100" : "opacity-0"
                )}
              />
            ))}
          </div>
        </div>

        {/* Question list */}
        <div className="border-b border-border">
          {items.map((item, index) => {
            const open = index === active
            const buttonId = `${uid}-q${index}`
            const panelId = `${uid}-a${index}`
            return (
              <div key={item.question}>
                {/* Top border doubles as the auto-advance progress track */}
                <div className="relative h-px overflow-hidden bg-border" aria-hidden="true">
                  {open && autoplay && (
                    <div
                      key={`progress-${active}`}
                      className="absolute inset-0 origin-left bg-primary-text animate-progress"
                      style={{ animationPlayState: running ? "running" : "paused" }}
                      onAnimationEnd={handleProgressEnd}
                    />
                  )}
                </div>

                <h3>
                  <button
                    type="button"
                    id={buttonId}
                    aria-expanded={open}
                    aria-controls={panelId}
                    onClick={() => choose(index)}
                    className="focus-ring group flex min-h-11 w-full items-center justify-between gap-4 py-5 text-left"
                  >
                    <span className="text-lg font-semibold text-balance md:text-xl">{item.question}</span>
                    <span
                      className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full border border-border bg-card text-foreground transition-colors duration-150 group-hover:bg-accent group-hover:text-accent-foreground"
                      aria-hidden="true"
                    >
                      <ChevronDown className={cn("h-4 w-4 transition-transform duration-300", open && "rotate-180")} />
                    </span>
                  </button>
                </h3>

                <div
                  id={panelId}
                  role="region"
                  aria-labelledby={buttonId}
                  className={cn(
                    "grid transition-[grid-template-rows] duration-300",
                    open ? "grid-rows-open" : "grid-rows-closed"
                  )}
                  {...(open ? {} : INERT)}
                >
                  <div className="min-h-0 overflow-hidden">
                    <div className="space-y-4 pb-6">
                      <p className="max-w-prose text-base leading-relaxed text-muted-foreground text-pretty">{item.answer}</p>
                      <div className="relative aspect-4/3 overflow-hidden rounded-xl bg-muted sm:aspect-video lg:hidden">
                        <Image
                          {...imageProps(item, 1200)}
                          alt=""
                          fill
                          sizes="100vw"
                          className="object-cover"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </section>
  )
}
