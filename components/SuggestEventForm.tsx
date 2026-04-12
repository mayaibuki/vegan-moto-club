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
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { Spinner } from "@/components/Spinner"

type FormStatus = "idle" | "submitting" | "success" | "error"

interface SuggestEventFormProps {
  id?: string
}

export function SuggestEventForm({ id }: SuggestEventFormProps) {
  const [description, setDescription] = useState("")
  const [url, setUrl] = useState("")
  const [honeypot, setHoneypot] = useState("")
  const [status, setStatus] = useState<FormStatus>("idle")
  const [errorMessage, setErrorMessage] = useState("")
  const mountTime = useRef(Date.now())

  const headingId = id ? `suggest-event-heading-${id}` : "suggest-event-heading"
  const descId = id ? `event-description-${id}` : "event-description"
  const urlId = id ? `event-url-${id}` : "event-url"

  function clearErrors() {
    if (status === "error") setStatus("idle")
  }

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()

    // Honeypot check — bots fill this hidden field, humans don't
    if (honeypot) {
      setStatus("success")
      setDescription("")
      setUrl("")
      setTimeout(() => setStatus("idle"), 3000)
      return
    }

    // Timing check — reject submissions faster than 2 seconds
    const elapsed = Date.now() - mountTime.current
    if (elapsed < 2000) {
      setStatus("success")
      setDescription("")
      setUrl("")
      setTimeout(() => setStatus("idle"), 3000)
      return
    }

    const trimmedDesc = description.trim()
    const trimmedUrl = url.trim()

    if (!trimmedDesc) {
      setStatus("error")
      setErrorMessage("Please enter an event description.")
      return
    }

    if (!trimmedUrl) {
      setStatus("error")
      setErrorMessage("Please enter an event URL.")
      return
    }

    try {
      new URL(trimmedUrl)
    } catch {
      setStatus("error")
      setErrorMessage("Please enter a valid URL (e.g. https://example.com).")
      return
    }

    setStatus("submitting")
    setErrorMessage("")

    try {
      const res = await fetch("/api/suggest-event", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ description: trimmedDesc, url: trimmedUrl, website: honeypot }),
      })

      const data = await res.json()

      if (!res.ok) {
        setStatus("error")
        setErrorMessage(data.error || "Something went wrong.")
        return
      }

      setStatus("success")
      setDescription("")
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
          <CardTitle id={headingId}>Suggest an Event</CardTitle>
          <CardDescription className="text-base">
            Know a moto-related event you&apos;d like to share with the community? Let us know.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Honeypot field — hidden from humans, filled by bots */}
            <div className="absolute opacity-0 h-0 w-0 overflow-hidden" aria-hidden="true">
              <label htmlFor={id ? `website-event-${id}` : "website-event"}>Website</label>
              <input
                type="text"
                id={id ? `website-event-${id}` : "website-event"}
                name="website"
                tabIndex={-1}
                autoComplete="off"
                value={honeypot}
                onChange={(e) => setHoneypot(e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor={descId}>Description</Label>
              <Textarea
                id={descId}
                placeholder="Tell us about the event — what, where, when…"
                value={description}
                onChange={(e) => { setDescription(e.target.value); clearErrors() }}
                disabled={status === "submitting"}
                rows={4}
                maxLength={2000}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor={urlId}>Event URL</Label>
              <Input
                id={urlId}
                type="url"
                placeholder="https://example.com/event"
                value={url}
                onChange={(e) => { setUrl(e.target.value); clearErrors() }}
                disabled={status === "submitting"}
              />
            </div>

            <Button
              type="submit"
              disabled={status === "submitting"}
              className="w-full sm:w-auto"
            >
              {status === "submitting" ? (
                <span className="flex items-center gap-2">
                  <Spinner />
                  Submitting...
                </span>
              ) : (
                "Submit Event"
              )}
            </Button>

            {status === "success" && (
              <p className="text-sm text-success font-medium">
                Thanks! Your event suggestion has been submitted.
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
