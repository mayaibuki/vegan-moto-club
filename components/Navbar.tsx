"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { Moon, Sun, Menu, X } from "lucide-react"
import { useEffect, useState, useCallback, useRef } from "react"
import { Button } from "./ui/button"
import { Logo } from "./Logo"
import { cn } from "@/lib/utils"

export function Navbar() {
  const pathname = usePathname()
  const [isDark, setIsDark] = useState(false)
  const [mounted, setMounted] = useState(false)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const mobileMenuRef = useRef<HTMLDivElement>(null)
  const menuButtonRef = useRef<HTMLButtonElement>(null)

  useEffect(() => {
    setMounted(true)
    const isDarkMode = document.documentElement.classList.contains("dark")
    setIsDark(isDarkMode)
  }, [])

  useEffect(() => {
    if (mobileMenuOpen && mobileMenuRef.current) {
      const firstLink = mobileMenuRef.current.querySelector('a')
      firstLink?.focus()
    }
  }, [mobileMenuOpen])

  useEffect(() => {
    if (!mobileMenuOpen) return
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setMobileMenuOpen(false)
        menuButtonRef.current?.focus()
      }
    }
    document.addEventListener("keydown", onKeyDown)
    return () => document.removeEventListener("keydown", onKeyDown)
  }, [mobileMenuOpen])

  const toggleTheme = useCallback(() => {
    if (!mounted) return
    const html = document.documentElement
    html.classList.toggle("dark")
    const newIsDark = html.classList.contains("dark")
    setIsDark(newIsDark)
    localStorage.setItem("theme", newIsDark ? "dark" : "light")
  }, [mounted])

  const navLinks = [
    { href: "/products", label: "Products" },
    { href: "/events", label: "Events" },
    { href: "/about", label: "About" },
  ]

  return (
    <header className="border-b border-border/50 bg-card/80 backdrop-blur-sm sticky top-0 z-50">
      <nav aria-label="Main navigation" className="page-container py-4 flex items-center justify-between">
        <Logo size="md" href="/" />

        {/* Desktop Navigation */}
        <div className="hidden md:flex items-center gap-8">
          {navLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              aria-current={pathname === link.href ? "page" : undefined}
              className="text-lg font-medium hover:underline aria-[current=page]:underline decoration-primary decoration-2 underline-offset-8 transition-colors focus-ring"
            >
              {link.label}
            </Link>
          ))}

          {mounted && (
            <Button
              variant="ghost"
              size="icon"
              onClick={toggleTheme}
              aria-label={isDark ? "Switch to light mode" : "Switch to dark mode"}
              className="rounded-full"
            >
              {isDark ? <Sun className="h-5 w-5" aria-hidden="true" /> : <Moon className="h-5 w-5" aria-hidden="true" />}
            </Button>
          )}
        </div>

        {/* Mobile Menu Button */}
        <div className="flex md:hidden items-center gap-2">
          {mounted && (
            <Button
              variant="ghost"
              size="icon"
              onClick={toggleTheme}
              aria-label={isDark ? "Switch to light mode" : "Switch to dark mode"}
              className="rounded-full"
            >
              {isDark ? <Sun className="h-5 w-5" aria-hidden="true" /> : <Moon className="h-5 w-5" aria-hidden="true" />}
            </Button>
          )}
          <Button
            ref={menuButtonRef}
            variant="ghost"
            size="icon"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label={mobileMenuOpen ? "Close navigation menu" : "Open navigation menu"}
            aria-expanded={mobileMenuOpen}
            aria-controls="mobile-nav-menu"
            className="rounded-full"
          >
            {mobileMenuOpen ? <X className="h-5 w-5" aria-hidden="true" /> : <Menu className="h-5 w-5" aria-hidden="true" />}
          </Button>
        </div>
      </nav>

      {/* Mobile Navigation Menu */}
      <nav
        id="mobile-nav-menu"
        // React 18 types only allow boolean for inert, but React 18 needs the "" string form to render the attribute
        {...(!mobileMenuOpen ? ({ inert: "" } as object) : {})}
        aria-hidden={!mobileMenuOpen}
        className={`md:hidden grid transition-[grid-template-rows] duration-200 ${mobileMenuOpen ? "grid-rows-[1fr]" : "grid-rows-[0fr]"}`}
        aria-label="Mobile navigation"
      >
        <div ref={mobileMenuRef} className={cn("overflow-hidden min-h-0", !mobileMenuOpen && "invisible transition-[visibility] duration-200")}>
          <div className="border-t border-border/50 bg-card">
            <ul className="page-container py-4 space-y-1 list-none">
              {navLinks.map((link) => (
                <li key={link.href}>
                  <Link
                    href={link.href}
                    onClick={() => { setMobileMenuOpen(false); menuButtonRef.current?.focus() }}
                    aria-current={pathname === link.href ? "page" : undefined}
                    className="block py-3 text-base font-medium hover:underline aria-[current=page]:underline decoration-primary decoration-2 underline-offset-8 transition-colors focus-ring"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </nav>
    </header>
  )
}
