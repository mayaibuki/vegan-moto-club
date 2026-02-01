import { getBlogPost, getBlogPosts } from "@/lib/notion"
import { notFound } from "next/navigation"
import Image from "next/image"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { formatDate } from "@/lib/utils"

export async function generateStaticParams() {
  const posts = await getBlogPosts()
  return posts.map((post) => ({
    id: post.id,
  }))
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

  return (
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
            className="object-cover"
            priority
            onError={(e) => {
              e.currentTarget.style.display = "none"
            }}
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
  )
}
