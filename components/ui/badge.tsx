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
        "inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
        variant === "default" &&
          "border border-transparent bg-primary text-primary-foreground hover:bg-primary/80",
        variant === "secondary" &&
          "border border-transparent bg-secondary text-secondary-foreground hover:bg-secondary/80",
        variant === "outline" && "border border-border text-foreground",
        variant === "accent" &&
          "border border-transparent bg-primary/15 text-primary-text",
        variant === "destructive" &&
          "border border-transparent bg-destructive text-destructive-foreground hover:bg-destructive/80",
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
