import type { Metadata } from "next"
import Link from "next/link"
import { GUIDES } from "@/lib/guides"
import { SITE_URL, SITE_OG_IMAGE } from "@/lib/constants"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { JsonLd } from "@/components/JsonLd"

const DESCRIPTION =
  "Short guides on the questions riders ask about vegan motorcycle gear: which fabrics are animal-free, how boots are rated, and how textile compares with leather under EN 17092."

export const metadata: Metadata = {
  title: "Guides",
  description: DESCRIPTION,
  openGraph: {
    title: "Guides | Vegan Moto Club",
    description: DESCRIPTION,
    url: "/guides",
    images: [SITE_OG_IMAGE],
  },
  alternates: {
    canonical: "/guides",
  },
}

export default function GuidesIndexPage() {
  const listJsonLd = {
    "@context": "https://schema.org",
    "@type": "ItemList",
    itemListElement: GUIDES.map((guide, index) => ({
      "@type": "ListItem",
      position: index + 1,
      url: `${SITE_URL}/guides/${guide.slug}`,
      name: guide.title,
    })),
  }

  return (
    <>
      <JsonLd data={listJsonLd} />
      <div className="space-y-10">
        <div className="space-y-4 max-w-3xl">
          <h1 className="h-page">Guides</h1>
          <p className="lead">{DESCRIPTION}</p>
        </div>
        <ul className="grid gap-6 md:grid-cols-2 list-none">
          {GUIDES.map((guide) => (
            <li key={guide.slug}>
              <Link href={`/guides/${guide.slug}`} className="block h-full focus-ring rounded-lg">
                <Card className="h-full hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <CardTitle className="text-xl text-balance">{guide.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-muted-foreground text-pretty">{guide.description}</p>
                  </CardContent>
                </Card>
              </Link>
            </li>
          ))}
        </ul>
        <p className="text-sm">
          <Link href="/blog" className="inline-flex min-h-11 items-center hover:underline underline-offset-4 decoration-primary decoration-2 focus-ring">
            Looking for quick answers? See the FAQ
          </Link>
        </p>
      </div>
    </>
  )
}
