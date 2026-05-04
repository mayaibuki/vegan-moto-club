"use client"

import { useState } from "react"
import Image from "next/image"
import { notionImageUrl } from "@/lib/utils"

interface ProductCardImageProps {
  src: string
  alt: string
}

export function ProductCardImage({ src, alt }: ProductCardImageProps) {
  const [errored, setErrored] = useState(false)

  if (errored) {
    return (
      <div
        className="absolute inset-0 flex items-center justify-center text-muted-foreground"
        aria-hidden="true"
      >
        No Image
      </div>
    )
  }

  const isProxy = src.startsWith("/api/notion-image")
  const resolved = isProxy ? notionImageUrl(src, 600) : src

  return (
    <Image
      src={resolved}
      alt={alt}
      fill
      sizes="(max-width: 768px) 100vw, (max-width: 1280px) 50vw, 33vw"
      className="object-contain p-4 transition-transform duration-300 group-hover:scale-105 ring-1 ring-border/10"
      onError={() => setErrored(true)}
      unoptimized={isProxy}
    />
  )
}
