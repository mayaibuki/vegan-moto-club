import { getBlogPosts } from "@/lib/notion"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import Link from "next/link"
import Image from "next/image"
import { formatDate } from "@/lib/utils"

export default async function BlogPage() {
  const posts = await getBlogPosts()

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-4xl font-heading font-bold mb-2">Blog</h1>
        <p className="text-muted-foreground">
          Articles, reviews, and stories from the vegan moto community
        </p>
      </div>

      {posts.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <p className="text-muted-foreground">
              No blog posts yet. Check back soon!
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-6">
          {posts.map((post) => (
            <Link key={post.id} href={`/blog/${post.id}`}>
              <Card className="overflow-hidden hover:shadow-lg transition-shadow cursor-pointer h-full">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-0">
                  {post.featuredImage && (
                    <div className="relative h-48 md:h-auto bg-muted md:col-span-1">
                      <Image
                        src={post.featuredImage}
                        alt={post.title}
                        fill
                        className="object-cover"
                      />
                    </div>
                  )}

                  <div className={`flex flex-col justify-between ${post.featuredImage ? 'md:col-span-2' : 'col-span-1'}`}>
                    <CardHeader>
                      <CardTitle className="text-xl line-clamp-2">{post.title}</CardTitle>
                      <CardDescription>
                        {formatDate(post.publishDate)}
                      </CardDescription>
                    </CardHeader>

                    <CardContent>
                      <p className="text-muted-foreground line-clamp-2">
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
  )
}
