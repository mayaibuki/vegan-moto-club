import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cn } from "@/lib/utils"

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  asChild?: boolean
  variant?: "default" | "destructive" | "outline" | "secondary" | "ghost" | "link"
  size?: "default" | "sm" | "lg" | "icon"
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "default", size = "default", asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button"
    return (
      <Comp
        className={cn(
          "inline-flex items-center justify-center whitespace-nowrap rounded-xl text-sm font-medium ring-offset-background transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
          variant === "default" && "bg-primary text-primary-foreground shadow-sm hover:bg-primary/90 hover:shadow-md",
          variant === "destructive" &&
            "bg-destructive text-destructive-foreground shadow-sm hover:bg-destructive/90",
          variant === "outline" &&
            "border-2 border-input bg-background hover:bg-accent hover:text-accent-foreground hover:border-accent",
          variant === "secondary" &&
            "bg-secondary text-secondary-foreground shadow-sm hover:bg-secondary/80",
          variant === "ghost" && "hover:bg-accent/50 hover:text-accent-foreground",
          variant === "link" && "text-primary underline-offset-4 hover:underline",
          size === "default" && "h-11 px-5 py-2.5",
          size === "sm" && "h-10 rounded-lg px-4",
          size === "lg" && "h-12 rounded-xl px-8 text-base",
          size === "icon" && "h-11 w-11",
          className
        )}
        ref={ref}
        {...props}
      />
    )
  }
)
Button.displayName = "Button"

export { Button }
