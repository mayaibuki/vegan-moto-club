import Link from "next/link"
import { ChevronRight } from "lucide-react"

interface BreadcrumbItem {
  label: string
  href?: string
}

export function Breadcrumbs({ items }: { items: BreadcrumbItem[] }) {
  return (
    <nav aria-label="Breadcrumb" className="mb-4 sm:mb-6">
      <ol className="flex items-center gap-1.5 text-sm text-muted-foreground flex-nowrap overflow-hidden">
        {items.map((item, i) => (
          <li key={i} className={`flex items-center gap-1.5 ${item.href ? "shrink-0" : "min-w-0"}`}>
            {i > 0 && (
              <ChevronRight className="h-3.5 w-3.5 flex-shrink-0" aria-hidden="true" />
            )}
            {item.href ? (
              <Link
                href={item.href}
                className="inline-flex min-h-11 items-center whitespace-nowrap hover:text-foreground transition-colors focus-ring"
              >
                {item.label}
              </Link>
            ) : (
              <span className="text-foreground font-medium truncate">
                {item.label}
              </span>
            )}
          </li>
        ))}
      </ol>
    </nav>
  )
}
