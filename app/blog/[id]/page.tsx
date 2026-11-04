import type { Metadata } from "next"
import { JsonLd } from "@/components/JsonLd"
import { getBlogPost, getPosts } from "@/lib/notion"
import { notFound } from "next/navigation"
import Image from "next/image"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { formatDate, notionImageUrl, truncateAtWord } from "@/lib/utils"
import { SITE_URL, SITE_OG_IMAGE } from "@/lib/constants"
import { Breadcrumbs } from "@/components/Breadcrumbs"
import { breadcrumbJsonLd } from "@/lib/seo"

export async function generateStaticParams() {
  const posts = await getPosts()
  return posts.map((post) => ({
    id: post.id,
  }))
}

export const revalidate = 3600

export async function generateMetadata({
  params,
}: {
  params: { id: string }
}): Promise<Metadata> {
  const post = await getBlogPost(params.id)

  if (!post || post.type !== "Post") {
    return {
      title: "Post Not Found",
    }
  }

  const description = post.content
    ? truncateAtWord(post.content)
    : `Read ${post.title} on Vegan Moto Club.`

  return {
    title: post.title,
    description,
    openGraph: {
      title: `${post.title} | Vegan Moto Club`,
      description,
      url: `/blog/${post.id}`,
      type: "article",
      publishedTime: post.publishDate,
      images: post.featuredImage ? [{ url: post.featuredImage }] : [SITE_OG_IMAGE],
    },
    twitter: {
      card: "summary_large_image",
      title: post.title,
      description,
      images: post.featuredImage ? [post.featuredImage] : [SITE_OG_IMAGE.url],
    },
    alternates: {
      canonical: `/blog/${post.id}`,
    },
  }
}

export default async function BlogPostPage({
  params,
}: {
  params: { id: string }
}) {
  const post = await getBlogPost(params.id)

  // FAQ rows are rendered inline on their pages, never as standalone posts.
  if (!post || post.type !== "Post") {
    notFound()
  }

  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "BlogPosting",
    headline: post.title,
    description: post.content ? truncateAtWord(post.content) : "",
    image: post.featuredImage || undefined,
    datePublished: post.publishDate,
    author: {
      "@type": "Organization",
      name: "Vegan Moto Club",
    },
    publisher: {
      "@type": "Organization",
      name: "Vegan Moto Club",
      logo: {
        "@type": "ImageObject",
        url: `${SITE_URL}/images/logo.png`,
      },
    },
    mainEntityOfPage: {
      "@type": "WebPage",
      "@id": `${SITE_URL}/blog/${post.id}`,
    },
  }

  return (
    <>
      <JsonLd data={jsonLd} />
      <JsonLd data={breadcrumbJsonLd([{ name: "Home", path: "/" }, { name: "Guides and FAQ", path: "/blog" }, { name: post.title, path: `/blog/${post.id}` }])} />
      <article className="max-w-3xl space-y-8">
      <Breadcrumbs items={[{ label: "Home", href: "/" }, { label: "Guides and FAQ", href: "/blog" }, { label: post.title }]} />

      {/* Header */}
      <header className="space-y-4">
        <h1 className="h-page">{post.title}</h1>
        <p className="text-muted-foreground">
          Published on {formatDate(post.publishDate)}
        </p>
      </header>

      {/* Featured Image */}
      {post.featuredImage && (
        <div className="relative w-full h-96 bg-muted rounded-lg overflow-hidden">
          <Image
            src={notionImageUrl(post.featuredImage, 1200)}
            alt={post.title}
            fill
            sizes="(max-width: 768px) 100vw, 768px"
            className="object-cover"
            priority
            unoptimized={post.featuredImage.startsWith("/api/notion-image")}
          />
        </div>
      )}

      {/* Content */}
      <div className="prose dark:prose-invert max-w-none">
        <div className="text-base text-muted-foreground whitespace-pre-wrap leading-relaxed">
          {post.content}
        </div>
      </div>

      <div className="border-t border-border pt-8">
        <Button variant="outline" asChild>
          <Link href="/blog">All guides and questions</Link>
        </Button>
      </div>
      </article>
    </>
  )
}
