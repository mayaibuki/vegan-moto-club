"use client"

import dynamic from "next/dynamic"

// Only load agentation in development to avoid bundling in production
const Agentation = dynamic(
  () => import("agentation").then((mod) => mod.Agentation),
  { ssr: false }
)

export function AgentationWrapper() {
  if (process.env.NODE_ENV !== "development") {
    return null
  }

  return <Agentation />
}
