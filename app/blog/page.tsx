import type { Metadata } from "next"
import { getBlogPosts } from "@/lib/notion"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import Link from "next/link"
import Image from "next/image"
import { formatDate } from "@/lib/utils"

export const metadata: Metadata = {
  title: "Blog",
  description:
    "Articles, reviews, and stories from the vegan moto community. Read about cruelty-free gear, ethical riding, and compassionate motorcycling.",
  openGraph: {
    title: "Blog | Vegan Moto Club",
    description:
      "Articles, reviews, and stories from the vegan moto community. Read about cruelty-free gear, ethical riding, and compassionate motorcycling.",
    url: "/blog",
  },
  alternates: {
    canonical: "/blog",
  },
}

export default async function BlogPage() {
  const posts = await getBlogPosts()

  const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || "https://veganmotoclub.com"

  const blogListJsonLd = {
    "@context": "https://schema.org",
    "@type": "ItemList",
    itemListElement: posts.map((post, index) => ({
      "@type": "ListItem",
      position: index + 1,
      url: `${siteUrl}/blog/${post.id}`,
      name: post.title,
    })),
  }

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(blogListJsonLd) }}
      />
      <div className="space-y-10">
      <div className="space-y-2">
        <h1 className="text-3xl md:text-4xl font-bold">Blog</h1>
        <p className="text-lg text-muted-foreground">
          Articles, reviews, and stories from the vegan moto community
        </p>
      </div>

      {posts.length === 0 ? (
        <Card>
          <CardContent className="py-16 text-center">
            <p className="text-lg text-muted-foreground">
              No blog posts yet. Check back soon!
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-6">
          {posts.map((post) => (
            <Link key={post.id} href={`/blog/${post.id}`} aria-label={`Read: ${post.title}`}>
              <Card className="overflow-hidden hover:shadow-lg transition-all cursor-pointer h-full group">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-0">
                  {post.featuredImage && (
                    <div className="relative h-48 md:h-auto bg-muted md:col-span-1 overflow-hidden">
                      <Image
                        src={post.featuredImage}
                        alt={post.title}
                        fill
                        sizes="(max-width: 768px) 100vw, 33vw"
                        className="object-cover transition-transform duration-300 group-hover:scale-105"
                        loading="lazy"
                      />
                    </div>
                  )}

                  <div className={`flex flex-col justify-between ${post.featuredImage ? 'md:col-span-2' : 'col-span-1'}`}>
                    <CardHeader className="pb-3">
                      <CardDescription className="text-sm">
                        {formatDate(post.publishDate)}
                      </CardDescription>
                      <CardTitle className="text-xl line-clamp-2 group-hover:text-primary transition-colors">
                        {post.title}
                      </CardTitle>
                    </CardHeader>

                    <CardContent>
                      <p className="text-muted-foreground line-clamp-3">
                        {post.content}
                      </p>
                    </CardContent>
                  </div>
                </div>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
    </>
  )
}
