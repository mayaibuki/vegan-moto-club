import type { Metadata } from "next"
import { getBlogPost, getBlogPosts } from "@/lib/notion"
import { notFound } from "next/navigation"
import Image from "next/image"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { formatDate } from "@/lib/utils"

const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || "https://veganmotoclub.com"

export async function generateStaticParams() {
  const posts = await getBlogPosts()
  return posts.map((post) => ({
    id: post.id,
  }))
}

export async function generateMetadata({
  params,
}: {
  params: { id: string }
}): Promise<Metadata> {
  const post = await getBlogPost(params.id)

  if (!post) {
    return {
      title: "Post Not Found",
    }
  }

  const description = post.content
    ? post.content.slice(0, 160)
    : `Read ${post.title} on Vegan Moto Club blog.`

  return {
    title: post.title,
    description,
    openGraph: {
      title: `${post.title} | Vegan Moto Club`,
      description,
      url: `/blog/${post.id}`,
      type: "article",
      publishedTime: post.publishDate,
      images: post.featuredImage ? [{ url: post.featuredImage }] : [],
    },
    twitter: {
      card: "summary_large_image",
      title: post.title,
      description,
      images: post.featuredImage ? [post.featuredImage] : [],
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

  if (!post) {
    notFound()
  }

  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "BlogPosting",
    headline: post.title,
    description: post.content ? post.content.slice(0, 160) : "",
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
        url: `${siteUrl}/logo.png`,
      },
    },
    mainEntityOfPage: {
      "@type": "WebPage",
      "@id": `${siteUrl}/blog/${post.id}`,
    },
  }

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <article className="max-w-3xl mx-auto space-y-8">
        {/* Back Button */}
      <Button variant="ghost" asChild className="mb-4">
        <Link href="/blog">← Back to Blog</Link>
      </Button>

      {/* Header */}
      <header className="space-y-4">
        <h1 className="text-4xl font-bold">{post.title}</h1>
        <p className="text-muted-foreground">
          Published on {formatDate(post.publishDate)}
        </p>
      </header>

      {/* Featured Image */}
      {post.featuredImage && (
        <div className="relative w-full h-96 bg-muted rounded-lg overflow-hidden">
          <Image
            src={post.featuredImage}
            alt={post.title}
            fill
            sizes="(max-width: 768px) 100vw, 768px"
            className="object-cover"
            priority
          />
        </div>
      )}

      {/* Content */}
      <div className="prose dark:prose-invert max-w-none">
        <div className="text-base text-muted-foreground whitespace-pre-wrap leading-relaxed">
          {post.content}
        </div>
      </div>

      {/* Back to Blog Link */}
      <div className="border-t border-border pt-8">
        <Button variant="outline" asChild>
          <Link href="/blog">← Back to All Posts</Link>
        </Button>
      </div>
      </article>
    </>
  )
}
