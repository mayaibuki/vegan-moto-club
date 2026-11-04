import type { Metadata } from "next"
import Link from "next/link"
import { notFound } from "next/navigation"
import { GUIDES, getGuide } from "@/lib/guides"
import { CATEGORY_PAGES, SITE_URL, SITE_OG_IMAGE, absoluteUrl } from "@/lib/constants"
import { Breadcrumbs } from "@/components/Breadcrumbs"
import { FaqSection } from "@/components/FaqSection"
import { JsonLd } from "@/components/JsonLd"
import { breadcrumbJsonLd } from "@/lib/seo"

export const dynamicParams = false

export function generateStaticParams() {
  return GUIDES.map((guide) => ({ slug: guide.slug }))
}

export function generateMetadata({ params }: { params: { slug: string } }): Metadata {
  const guide = getGuide(params.slug)
  if (!guide) return {}
  return {
    title: guide.title,
    description: guide.description,
    openGraph: {
      title: `${guide.title} | Vegan Moto Club`,
      description: guide.description,
      url: `/guides/${guide.slug}`,
      type: "article",
      publishedTime: guide.datePublished,
      modifiedTime: guide.dateModified,
      images: [SITE_OG_IMAGE],
    },
    alternates: {
      canonical: `/guides/${guide.slug}`,
    },
  }
}

export default function GuidePage({ params }: { params: { slug: string } }) {
  const guide = getGuide(params.slug)
  if (!guide) notFound()

  const related = CATEGORY_PAGES.filter((page) => guide.relatedCategories.includes(page.slug))

  const articleJsonLd = {
    "@context": "https://schema.org",
    "@type": "Article",
    headline: guide.title,
    description: guide.description,
    datePublished: guide.datePublished,
    dateModified: guide.dateModified,
    image: absoluteUrl(SITE_OG_IMAGE.url),
    author: { "@type": "Organization", name: "Vegan Moto Club", url: SITE_URL },
    publisher: {
      "@type": "Organization",
      name: "Vegan Moto Club",
      logo: { "@type": "ImageObject", url: absoluteUrl("/images/logo.png") },
    },
    mainEntityOfPage: { "@type": "WebPage", "@id": `${SITE_URL}/guides/${guide.slug}` },
  }

  return (
    <>
      <JsonLd data={articleJsonLd} />
      <JsonLd
        data={breadcrumbJsonLd([
          { name: "Home", path: "/" },
          { name: "Guides", path: "/guides" },
          { name: guide.title, path: `/guides/${guide.slug}` },
        ])}
      />
      <article className="max-w-3xl space-y-10">
        <Breadcrumbs items={[{ label: "Home", href: "/" }, { label: "Guides", href: "/guides" }, { label: guide.title }]} />

        <header className="space-y-4">
          <h1 className="h-page">{guide.title}</h1>
          <p className="lead">{guide.description}</p>
          <p className="text-sm text-muted-foreground">
            Updated <time dateTime={guide.dateModified}>{formatGuideDate(guide.dateModified)}</time>
          </p>
        </header>

        {guide.sections.map((section) => (
          <section key={section.heading} className="space-y-4">
            <h2 className="h-section">{section.heading}</h2>
            {section.paragraphs.map((paragraph) => (
              <p key={paragraph.slice(0, 40)} className="text-base text-muted-foreground leading-relaxed max-w-prose text-pretty">
                {paragraph}
              </p>
            ))}
          </section>
        ))}

        {related.length > 0 && (
          <nav aria-label="Related gear" className="space-y-4">
            <h2 className="h-section">Related gear</h2>
            <ul className="flex flex-wrap gap-2">
              {related.map((page) => (
                <li key={page.slug}>
                  <Link
                    href={`/${page.slug}`}
                    className="inline-flex h-11 items-center rounded-full border border-border bg-card px-4 text-sm transition-colors duration-150 hover:bg-muted focus-ring"
                  >
                    {page.title}
                  </Link>
                </li>
              ))}
            </ul>
          </nav>
        )}

        <FaqSection items={guide.faq} title="Common questions" />

        {guide.sources.length > 0 && (
          <section aria-labelledby="sources-heading" className="space-y-3">
            <h2 id="sources-heading" className="text-lg font-semibold">Sources</h2>
            <ul className="text-sm text-muted-foreground space-y-1">
              {guide.sources.map((source) => (
                <li key={source.url + source.label}>
                  <a href={source.url} target="_blank" rel="noopener noreferrer" className="hover:underline underline-offset-4 decoration-primary decoration-2 focus-ring">
                    {source.label}
                    <span className="sr-only"> (opens in new tab)</span>
                  </a>
                </li>
              ))}
            </ul>
          </section>
        )}
      </article>
    </>
  )
}

function formatGuideDate(iso: string): string {
  const [year, month, day] = iso.split("-").map(Number)
  return new Date(Date.UTC(year, month - 1, day)).toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
    timeZone: "UTC",
  })
}
