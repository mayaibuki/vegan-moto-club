import Link from "next/link"
import { Logo } from "./Logo"

export function Footer() {
  return (
    <footer className="border-t border-border bg-secondary/10 mt-12">
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
          <div>
            <div className="mb-4">
              <Logo size="sm" />
            </div>
            <h3 className="font-heading font-bold mb-4">Vegan Moto Club</h3>
            <p className="text-sm text-muted-foreground">
              A database of cruelty-free motorcycle gear for compassionate riders.
            </p>
          </div>

          <div>
            <h3 className="font-heading font-bold mb-4">Navigation</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <Link href="/products" className="hover:text-primary">
                  Products
                </Link>
              </li>
              <li>
                <Link href="/events" className="hover:text-primary">
                  Events
                </Link>
              </li>
              <li>
                <Link href="/blog" className="hover:text-primary">
                  Blog
                </Link>
              </li>
              <li>
                <Link href="/about" className="hover:text-primary">
                  About
                </Link>
              </li>
            </ul>
          </div>

          <div>
            <h3 className="font-heading font-bold mb-4">Connect</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <a
                  href="https://discord.com"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-primary"
                >
                  Discord
                </a>
              </li>
              <li>
                <a
                  href="https://instagram.com"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-primary"
                >
                  Instagram
                </a>
              </li>
            </ul>
          </div>
        </div>

        <div className="border-t border-border pt-8 text-center text-sm text-muted-foreground">
          <p>&copy; 2025 Vegan Moto Club. All rights reserved.</p>
        </div>
      </div>
    </footer>
  )
}
