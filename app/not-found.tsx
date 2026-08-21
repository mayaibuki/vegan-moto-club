import Link from "next/link"
import { Button } from "@/components/ui/button"
import { CATEGORY_PAGES } from "@/lib/constants"

export default function NotFound() {
  return (
    <div className="py-24 text-center space-y-8">
      <div className="space-y-3">
        <p className="text-sm font-semibold uppercase tracking-wide text-primary">404</p>
        <h1 className="text-3xl md:text-4xl font-bold">This page took a wrong turn</h1>
        <p className="text-lg text-muted-foreground max-w-xl mx-auto">
          The page you&apos;re looking for doesn&apos;t exist or may have moved.
          The gear is still here, though.
        </p>
      </div>

      <div className="flex flex-col sm:flex-row gap-4 justify-center">
        <Button size="lg" asChild>
          <Link href="/products">Browse All Gear</Link>
        </Button>
        <Button size="lg" variant="outline" asChild>
          <Link href="/">Back to Home</Link>
        </Button>
      </div>

      <nav aria-label="Popular categories" className="pt-4">
        <p className="text-sm text-muted-foreground mb-3">Or jump straight to a category:</p>
        <ul className="flex flex-wrap justify-center gap-3">
          {CATEGORY_PAGES.map((page) => (
            <li key={page.slug}>
              <Link
                href={`/${page.slug}`}
                className="inline-block rounded-full border border-border px-4 py-1.5 text-sm hover:bg-muted"
              >
                {page.category}
              </Link>
            </li>
          ))}
        </ul>
      </nav>
    </div>
  )
}
