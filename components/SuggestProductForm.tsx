"use client"

import { useState, useRef, FormEvent } from "react"
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { Spinner } from "@/components/Spinner"

type FormStatus = "idle" | "submitting" | "success" | "error"

interface SuggestProductFormProps {
  id?: string
}

export function SuggestProductForm({ id }: SuggestProductFormProps) {
  const [url, setUrl] = useState("")
  const [honeypot, setHoneypot] = useState("")
  const [status, setStatus] = useState<FormStatus>("idle")
  const [errorMessage, setErrorMessage] = useState("")
  const mountTime = useRef(Date.now())

  const headingId = id ? `suggest-product-heading-${id}` : "suggest-product-heading"
  const inputId = id ? `product-url-${id}` : "product-url"

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()

    // Honeypot check — bots fill this hidden field, humans don't
    if (honeypot) {
      // Fake success so bots think it worked
      setStatus("success")
      setUrl("")
      setTimeout(() => setStatus("idle"), 3000)
      return
    }

    // Timing check — reject submissions faster than 2 seconds
    const elapsed = Date.now() - mountTime.current
    if (elapsed < 2000) {
      setStatus("success")
      setUrl("")
      setTimeout(() => setStatus("idle"), 3000)
      return
    }

    const trimmed = url.trim()
    if (!trimmed) {
      setStatus("error")
      setErrorMessage("Please enter a URL.")
      return
    }

    try {
      new URL(trimmed)
    } catch {
      setStatus("error")
      setErrorMessage("Please enter a valid URL (e.g. https://example.com).")
      return
    }

    setStatus("submitting")
    setErrorMessage("")

    try {
      const res = await fetch("/api/suggest", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: trimmed, website: honeypot }),
      })

      const data = await res.json()

      if (!res.ok) {
        setStatus("error")
        setErrorMessage(data.error || "Something went wrong.")
        return
      }

      setStatus("success")
      setUrl("")
      setTimeout(() => setStatus("idle"), 3000)
    } catch {
      setStatus("error")
      setErrorMessage("Network error. Please try again.")
    }
  }

  return (
    <section aria-labelledby={headingId}>
      <Card className="max-w-2xl mx-auto">
        <CardHeader>
          <CardTitle id={headingId}>Suggest a Product</CardTitle>
          <CardDescription className="text-base">
            Know a good vegan motorcycle product? Share the link and we will
            post it here.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Honeypot field — hidden from humans, filled by bots */}
            <div className="absolute opacity-0 h-0 w-0 overflow-hidden" aria-hidden="true">
              <label htmlFor={id ? `website-${id}` : "website"}>Website</label>
              <input
                type="text"
                id={id ? `website-${id}` : "website"}
                name="website"
                tabIndex={-1}
                autoComplete="off"
                value={honeypot}
                onChange={(e) => setHoneypot(e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor={inputId}>Product URL</Label>
              <div className="flex flex-col sm:flex-row gap-3">
                <Input
                  id={inputId}
                  type="url"
                  placeholder="https://example.com/product"
                  value={url}
                  onChange={(e) => {
                    setUrl(e.target.value)
                    if (status === "error") setStatus("idle")
                  }}
                  disabled={status === "submitting"}
                  className="flex-1"
                />
                <Button
                  type="submit"
                  disabled={status === "submitting"}
                  className="sm:w-auto w-full"
                >
                  {status === "submitting" ? (
                    <span className="flex items-center gap-2">
                      <Spinner />
                      Submitting...
                    </span>
                  ) : (
                    "Submit"
                  )}
                </Button>
              </div>
            </div>

            {status === "success" && (
              <p className="text-sm text-success font-medium">
                Thanks! Your suggestion has been submitted.
              </p>
            )}

            {status === "error" && errorMessage && (
              <p className="text-sm text-destructive font-medium">
                {errorMessage}
              </p>
            )}
          </form>
        </CardContent>
      </Card>
    </section>
  )
}
