import type { MetadataRoute } from "next"
import { getProducts, getPosts, type Product } from "@/lib/notion"
import { SITE_URL, CATEGORY_PAGES } from "@/lib/constants"
import { GUIDES } from "@/lib/guides"
import { splitCategories } from "@/lib/utils"

// Date of the last copy change to the hand-written pages (/about, /verification, /events).
// Bump it when their content ships. Data-driven pages use the newest product edit instead.
const STATIC_LAST_MODIFIED = new Date("2026-11-03")

// Refresh hourly like the pages it lists; revalidateTag("products") refreshes sooner.
export const revalidate = 3600

/** Newest lastEditedTime in a list, or undefined when the list is empty. */
function latestEdit(products: Product[]): Date | undefined {
  let latest = ""
  for (const p of products) if (p.lastEditedTime > latest) latest = p.lastEditedTime
  return latest ? new Date(latest) : undefined
}

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  // getProducts() returns [] when Notion is unavailable; every lastmod then
  // falls back to STATIC_LAST_MODIFIED and product entries are simply absent.
  const [products, posts] = await Promise.all([getProducts(), getPosts()])
  const catalogModified = latestEdit(products) ?? STATIC_LAST_MODIFIED

  const staticPages: MetadataRoute.Sitemap = [
    {
      url: SITE_URL,
      lastModified: catalogModified,
      changeFrequency: "daily",
      priority: 1,
    },
    {
      url: `${SITE_URL}/products`,
      lastModified: catalogModified,
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
    {
      url: `${SITE_URL}/blog`,
      lastModified: STATIC_LAST_MODIFIED,
      changeFrequency: "weekly",
      priority: 0.6,
    },
  ]

  const guidePages: MetadataRoute.Sitemap = [
    {
      url: `${SITE_URL}/guides`,
      lastModified: GUIDES.reduce((latest, g) => (g.dateModified > latest ? g.dateModified : latest), "") ? new Date(GUIDES.reduce((latest, g) => (g.dateModified > latest ? g.dateModified : latest), "")) : STATIC_LAST_MODIFIED,
      changeFrequency: "monthly",
      priority: 0.6,
    },
    ...GUIDES.map((guide) => ({
      url: `${SITE_URL}/guides/${guide.slug}`,
      lastModified: new Date(guide.dateModified),
      changeFrequency: "monthly" as const,
      priority: 0.6,
    })),
  ]

  const postPages: MetadataRoute.Sitemap = posts.map((post) => ({
    url: `${SITE_URL}/blog/${post.id}`,
    lastModified: post.publishDate ? new Date(post.publishDate) : STATIC_LAST_MODIFIED,
    changeFrequency: "monthly" as const,
    priority: 0.5,
  }))

  // Static category landing pages: lastmod is the newest edit among the
  // products that page lists (same filter as app/[category]/page.tsx).
  const categoryPages: MetadataRoute.Sitemap = CATEGORY_PAGES.map((page) => ({
    url: `${SITE_URL}/${page.slug}`,
    lastModified:
      latestEdit(products.filter((p) => splitCategories(p.category).includes(page.category))) ??
      STATIC_LAST_MODIFIED,
    changeFrequency: "weekly" as const,
    priority: 0.7,
  }))

  // Product pages carry their own Notion edit time so crawlers can prioritize
  // real changes instead of seeing every URL "modified" on every build.
  const productPages: MetadataRoute.Sitemap = products.map((product) => ({
    url: `${SITE_URL}/products/${product.slug}`,
    lastModified: product.lastEditedTime ? new Date(product.lastEditedTime) : catalogModified,
    changeFrequency: "weekly" as const,
    priority: 0.6,
  }))

  return [...staticPages, ...categoryPages, ...guidePages, ...postPages, ...productPages]
}
