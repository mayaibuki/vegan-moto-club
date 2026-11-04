import type { Metadata } from "next"
import Link from "next/link"
import Image from "next/image"
import { getBlogPosts } from "@/lib/notion"
import type { FaqItem } from "@/lib/notion"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { FaqSection } from "@/components/FaqSection"
import { JsonLd } from "@/components/JsonLd"
import { faqPageJsonLd } from "@/lib/seo"
import { formatDate, notionImageUrl } from "@/lib/utils"
import { SITE_URL, SITE_OG_IMAGE, CATEGORY_PAGES } from "@/lib/constants"

const DESCRIPTION =
  "Answers to the questions riders ask about vegan motorcycle gear: materials, CE ratings, how we verify products, and what to check before buying."

export const metadata: Metadata = {
  title: "Guides and FAQ",
  description: DESCRIPTION,
  openGraph: {
    title: "Guides and FAQ | Vegan Moto Club",
    description: DESCRIPTION,
    url: "/blog",
    images: [SITE_OG_IMAGE],
  },
  alternates: {
    canonical: "/blog",
  },
}

export const revalidate = 3600

// Section order on the page. Gear categories follow CATEGORY_PAGES.
const FAQ_GROUPS: { category: string; title: string; href?: string }[] = [
  { category: "General", title: "Vegan motorcycle gear" },
  { category: "Verification", title: "How we verify", href: "/verification" },
  ...CATEGORY_PAGES.map((page) => ({ category: page.category, title: page.title, href: `/${page.slug}` })),
]

export default async function BlogPage() {
  const rows = await getBlogPosts()
  const posts = rows.filter((row) => row.type === "Post")
  const faqs = rows
    .filter((row) => row.type === "FAQ" && row.content !== "")
    .sort((a, b) => a.publishDate.localeCompare(b.publishDate))
  const groups = FAQ_GROUPS.map((group) => ({
    ...group,
    items: faqs
      .filter((row) => row.category === group.category)
      .map<FaqItem>((row) => ({ question: row.title, answer: row.content })),
  })).filter((group) => group.items.length > 0)
  const allFaqItems = groups.flatMap((group) => group.items)

  const postListJsonLd = {
    "@context": "https://schema.org",
    "@type": "ItemList",
    itemListElement: posts.map((post, index) => ({
      "@type": "ListItem",
      position: index + 1,
      url: `${SITE_URL}/blog/${post.id}`,
      name: post.title,
    })),
  }

  return (
    <>
      {allFaqItems.length > 0 && <JsonLd data={faqPageJsonLd(allFaqItems)} />}
      {posts.length > 0 && <JsonLd data={postListJsonLd} />}
      <div className="space-y-12">
        <div className="space-y-4 max-w-3xl">
          <h1 className="h-page">Guides and FAQ</h1>
          <p className="lead">{DESCRIPTION}</p>
        </div>

        {groups.length === 0 && posts.length === 0 && (
          <p className="text-muted-foreground py-8">Nothing here yet. Check back soon.</p>
        )}

        {groups.map((group) => (
          <div key={group.category} className="space-y-4">
            <FaqSection
              id={`faq-${group.category.toLowerCase().replace(/\s+/g, "-")}`}
              items={group.items}
              title={group.title}
              withSchema={false}
            />
            {group.href && (
              <p className="text-sm">
                <Link href={group.href} className="inline-flex min-h-11 items-center hover:underline underline-offset-4 decoration-primary decoration-2 focus-ring">
                  {group.category === "Verification" ? "Read how verification works" : `Browse ${group.title.toLowerCase()}`}
                </Link>
              </p>
            )}
          </div>
        ))}

        {posts.length > 0 && (
          <section aria-labelledby="posts-heading" className="space-y-6">
            <h2 id="posts-heading" className="h-section">Articles</h2>
            <div className="grid gap-6">
              {posts.map((post) => (
                <Link key={post.id} href={`/blog/${post.id}`} aria-label={`Read: ${post.title}`} className="focus-ring rounded-lg">
                  <Card className="overflow-hidden hover:shadow-lg transition-shadow h-full group">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-0">
                      {post.featuredImage && (
                        <div className="relative h-48 md:h-auto bg-muted md:col-span-1 overflow-hidden">
                          <Image
                            src={notionImageUrl(post.featuredImage, 600)}
                            alt={post.title}
                            fill
                            sizes="(max-width: 768px) 100vw, 33vw"
                            className="object-cover transition-transform duration-300 group-hover:scale-105"
                            loading="lazy"
                            unoptimized={post.featuredImage.startsWith("/api/notion-image")}
                          />
                        </div>
                      )}
                      <div className={`flex flex-col justify-between ${post.featuredImage ? "md:col-span-2" : "col-span-1"}`}>
                        <CardHeader className="pb-3">
                          <CardDescription className="text-sm">{formatDate(post.publishDate)}</CardDescription>
                          <CardTitle className="text-xl line-clamp-2 group-hover:text-primary transition-colors text-balance">
                            {post.title}
                          </CardTitle>
                        </CardHeader>
                        <CardContent>
                          <p className="text-muted-foreground line-clamp-3">{post.content}</p>
                        </CardContent>
                      </div>
                    </div>
                  </Card>
                </Link>
              ))}
            </div>
          </section>
        )}
      </div>
    </>
  )
}
