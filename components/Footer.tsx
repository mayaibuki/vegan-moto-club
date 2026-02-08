import Link from "next/link"
import { Logo } from "./Logo"

export function Footer() {
  return (
    <footer className="border-t border-border bg-secondary/10 mt-12" role="contentinfo">
      <div className="max-w-7xl mx-auto px-6 py-10">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-10 mb-10">
          {/* Brand Section */}
          <div className="text-center md:text-left">
            <div className="mb-4 flex justify-center md:justify-start">
              <Logo size="sm" />
            </div>
            <p className="font-bold mb-3">Vegan Moto Club</p>
            <p className="text-sm text-muted-foreground max-w-xs mx-auto md:mx-0">
              A database of cruelty-free motorcycle gear for compassionate riders.
            </p>
          </div>

          {/* Navigation Section */}
          <nav aria-label="Footer navigation" className="text-center md:text-left">
            <h2 className="font-bold mb-4 text-base">Navigation</h2>
            <ul className="space-y-3 text-sm">
              <li>
                <Link href="/products" className="hover:text-primary transition-colors">
                  Products
                </Link>
              </li>
              <li>
                <Link href="/events" className="hover:text-primary transition-colors">
                  Events
                </Link>
              </li>
              <li>
                <Link href="/blog" className="hover:text-primary transition-colors">
                  Blog
                </Link>
              </li>
              <li>
                <Link href="/about" className="hover:text-primary transition-colors">
                  About
                </Link>
              </li>
            </ul>
          </nav>

          {/* Connect Section */}
          <div className="text-center md:text-left">
            <h2 className="font-bold mb-4 text-base">Connect</h2>
            <ul className="space-y-3 text-sm">
              <li>
                <a
                  href="https://discord.gg/GN4jkBRnut"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-primary transition-colors"
                  aria-label="Join us on Discord (opens in new tab)"
                >
                  Discord<span className="sr-only"> (opens in new tab)</span>
                </a>
              </li>
              <li>
                <a
                  href="https://www.instagram.com/veganmotoclub"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-primary transition-colors"
                  aria-label="Follow us on Instagram (opens in new tab)"
                >
                  Instagram<span className="sr-only"> (opens in new tab)</span>
                </a>
              </li>
            </ul>
          </div>
        </div>

        <div className="border-t border-border pt-8 text-center text-sm text-muted-foreground">
          <p>&copy; 2026 Vegan Moto Club. All rights reserved.</p>
        </div>
      </div>
    </footer>
  )
}
