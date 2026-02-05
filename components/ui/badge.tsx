import * as React from "react"
import { cn } from "@/lib/utils"

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "secondary" | "outline" | "accent"
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
        variant === "outline" && "border border-input text-foreground",
        variant === "accent" &&
          "border border-transparent bg-accent/20 text-accent-foreground hover:bg-accent/30",
        className
      )}
      {...props}
    />
  )
}

export { Badge }
