"use client"

import Link from "next/link"
import { Moon, Sun } from "lucide-react"
import { useEffect, useState } from "react"
import { Button } from "./ui/button"
import { Logo } from "./Logo"

export function Navbar() {
  const [isDark, setIsDark] = useState(false)
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
    const isDarkMode = document.documentElement.classList.contains("dark")
    setIsDark(isDarkMode)
  }, [])

  const toggleTheme = () => {
    if (!mounted) return

    const html = document.documentElement
    html.classList.toggle("dark")
    const newIsDark = html.classList.contains("dark")
    setIsDark(newIsDark)
    localStorage.setItem("theme", newIsDark ? "dark" : "light")
  }

  return (
    <nav className="border-b border-border bg-background sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
        <Logo size="md" href="/" />

        <div className="flex items-center gap-6">
          <Link href="/products" className="hover:text-primary transition-colors">
            Products
          </Link>
          <Link href="/events" className="hover:text-primary transition-colors">
            Events
          </Link>
          <Link href="/blog" className="hover:text-primary transition-colors">
            Blog
          </Link>
          <Link href="/about" className="hover:text-primary transition-colors">
            About
          </Link>

          {mounted && (
            <Button
              variant="ghost"
              size="icon"
              onClick={toggleTheme}
              aria-label="Toggle theme"
            >
              {isDark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </Button>
          )}
        </div>
      </div>
    </nav>
  )
}
