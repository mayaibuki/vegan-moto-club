"use client"

import { useEffect } from "react"
import { Button } from "@/components/ui/button"

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    console.error(error)
  }, [error])

  return (
    <div className="py-24 text-center space-y-6">
      <div className="space-y-3">
        <h1 className="text-3xl font-bold">Something went wrong</h1>
        <p className="text-lg text-muted-foreground max-w-xl mx-auto">
          An unexpected error occurred while loading this page. It&apos;s usually
          temporary.
        </p>
      </div>
      <Button size="lg" onClick={reset}>
        Try Again
      </Button>
    </div>
  )
}
