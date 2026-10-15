import * as React from "react"
import { cn } from "@/lib/utils"

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "secondary" | "outline" | "accent" | "destructive" | "positive" | "negative"
}

function Badge({ className, variant = "default", ...props }: BadgeProps) {
  return (
    <div
      className={cn(
        "inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold transition-colors",
        variant === "default" &&
          "border border-transparent bg-primary text-primary-foreground",
        variant === "secondary" &&
          "border border-transparent bg-secondary text-secondary-foreground",
        variant === "outline" && "border border-border text-foreground",
        variant === "accent" &&
          "border border-transparent bg-primary/15 text-primary-text",
        variant === "destructive" &&
          "border border-transparent bg-destructive text-destructive-foreground",
        variant === "positive" &&
          "border border-primary/30 bg-primary/15 text-primary-text",
        variant === "negative" &&
          "border border-destructive/30 bg-destructive/10 text-destructive-text",
        className
      )}
      {...props}
    />
  )
}

export { Badge }
