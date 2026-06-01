"use client"

import Link from "next/link"
import { Tag, X } from "lucide-react"
import { useEffect, useState, useCallback } from "react"
import { Button } from "./ui/button"

const STORAGE_KEY = "promo-bellissimoto-dismissed"

export function PromoBanner() {
  const [mounted, setMounted] = useState(false)
  const [dismissed, setDismissed] = useState(false)

  useEffect(() => {
    setMounted(true)
    setDismissed(localStorage.getItem(STORAGE_KEY) === "true")
  }, [])

  const handleDismiss = useCallback(() => {
    setDismissed(true)
    localStorage.setItem(STORAGE_KEY, "true")
  }, [])

  if (!mounted || dismissed) return null

  return (
    <div
      role="region"
      aria-label="Promotion"
      className="relative rounded-lg border border-border border-l-4 border-l-primary bg-card text-card-foreground p-4 sm:p-5 pr-14 sm:pr-16 shadow-sm"
    >
      <div className="flex flex-col sm:flex-row sm:items-center gap-3 sm:gap-4">
        <Tag className="h-5 w-5 text-primary flex-shrink-0 hidden sm:block" aria-hidden="true" />
        <p className="text-sm sm:text-base text-foreground">
          Members get 15% off Virus Power via Bellissimoto.com. Promo Code: VEGANMC
        </p>
        <Button asChild variant="outline" size="xs" className="flex-shrink-0 sm:ml-auto">
          <Link href="/products?brand=Virus+Power">View Virus Power Suits</Link>
        </Button>
      </div>
      <Button
        variant="ghost"
        size="icon"
        onClick={handleDismiss}
        aria-label="Dismiss promotion"
        className="absolute top-1/2 right-2 -translate-y-1/2 rounded-full"
      >
        <X className="h-5 w-5" aria-hidden="true" />
      </Button>
    </div>
  )
}
