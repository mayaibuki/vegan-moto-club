import type { MetadataRoute } from "next"
import { getProducts, getBlogPosts } from "@/lib/notion"
import { SITE_URL, CATEGORY_PAGES } from "@/lib/constants"
const STATIC_LAST_MODIFIED = new Date("2026-02-07")

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  // Static pages
  const staticPages: MetadataRoute.Sitemap = [
    {
      url: SITE_URL,
      lastModified: STATIC_LAST_MODIFIED,
      changeFrequency: "daily",
      priority: 1,
    },
    {
      url: `${SITE_URL}/products`,
      lastModified: STATIC_LAST_MODIFIED,
      changeFrequency: "daily",
      priority: 0.9,
    },
    {
      url: `${SITE_URL}/events`,
      lastModified: STATIC_LAST_MODIFIED,
      changeFrequency: "weekly",
      priority: 0.8,
    },
    {
      url: `${SITE_URL}/blog`,
      lastModified: STATIC_LAST_MODIFIED,
      changeFrequency: "weekly",
      priority: 0.8,
    },
    {
      url: `${SITE_URL}/about`,
      lastModified: STATIC_LAST_MODIFIED,
      changeFrequency: "monthly",
      priority: 0.7,
    },
    {
      url: `${SITE_URL}/verification`,
      lastModified: STATIC_LAST_MODIFIED,
      changeFrequency: "monthly",
      priority: 0.6,
    },
  ]

  // Static category landing pages (real server-rendered pages, not
  // query-param views of /products)
  const categoryPages: MetadataRoute.Sitemap = CATEGORY_PAGES.map((page) => ({
    url: `${SITE_URL}/${page.slug}`,
    lastModified: STATIC_LAST_MODIFIED,
    changeFrequency: "weekly" as const,
    priority: 0.7,
  }))

  // Dynamic product pages — real lastModified so crawlers can prioritize
  // actual changes instead of seeing every URL "modified" on every build
  const products = await getProducts()
  const productPages: MetadataRoute.Sitemap = products.map((product) => ({
    url: `${SITE_URL}/products/${product.slug}`,
    lastModified: product.lastEditedTime ? new Date(product.lastEditedTime) : new Date(),
    changeFrequency: "weekly" as const,
    priority: 0.6,
  }))

  // Dynamic blog pages
  const blogPosts = await getBlogPosts()
  const blogPages: MetadataRoute.Sitemap = blogPosts.map((post) => ({
    url: `${SITE_URL}/blog/${post.id}`,
    lastModified: post.publishDate ? new Date(post.publishDate) : new Date(),
    changeFrequency: "monthly" as const,
    priority: 0.6,
  }))

  return [...staticPages, ...categoryPages, ...productPages, ...blogPages]
}
