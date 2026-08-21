import { Client } from "@notionhq/client";
import { unstable_cache } from "next/cache";
import { generateSlug } from "./utils";

export const notion = new Client({
  auth: process.env.NOTION_API_KEY,
  // Fail fast instead of the 60s default — a healthy query answers in
  // seconds, and slow requests burn billed CPU time. Retries handle the rest.
  timeoutMs: 15_000,
});

const REVALIDATE_TIME = process.env.NODE_ENV === "production" ? 3600 : 60;

// ─── Exported types ──────────────────────────────────────────────

export interface Product {
  id: string;
  slug: string;
  createdTime: string;
  name: string;
  brand: string;
  category: string;
  levelOfProtection: string;
  gender: string;
  price: number;
  description: string;
  url: string;
  photos: string[];
  ridingStyle: string[];
  season: string[];
  waterproofLevel: string;
  materials: string[];
  veganVerified: string;
  staffFavorite: boolean;
  lastEditedTime: string;
}

export interface Event {
  id: string;
  name: string;
  startDate: string;
  endDate: string;
  description: string;
  location: string;
  url: string;
  price: string;
  poster: string;
}

export interface BlogPost {
  id: string;
  title: string;
  content: string;
  publishDate: string;
  featuredImage: string;
}

// ─── Notion API response types ───────────────────────────────────

interface NotionRichText {
  plain_text: string
}

interface NotionSelectOption {
  name: string
}

interface NotionFile {
  type: "external" | "file"
  external?: { url: string }
  file?: { url: string }
}

interface NotionPageProperties {
  [key: string]: {
    title?: NotionRichText[]
    rich_text?: NotionRichText[]
    select?: { name: string }
    multi_select?: NotionSelectOption[]
    number?: number
    url?: string
    checkbox?: boolean
    date?: { start: string; end?: string }
    files?: NotionFile[]
  }
}

interface NotionPage {
  id: string
  created_time: string
  last_edited_time: string
  properties: NotionPageProperties
}

// ─── Internal helpers ────────────────────────────────────────────

function extractText(richText: NotionRichText[]): string {
  return richText.map((block) => block.plain_text).join("");
}

/**
 * Resolve a Notion file to a stable URL. External files use their URL directly;
 * Notion-hosted files go through the /api/notion-image proxy so Vercel's image
 * optimizer cache key doesn't rotate with Notion's signed URLs.
 */
function resolveFileUrl(
  pageId: string,
  file: NotionFile | undefined,
  prop: string,
  idx: number
): string {
  if (!file) return "";
  if (file.type === "file") {
    return `/api/notion-image?pageId=${pageId}&prop=${encodeURIComponent(prop)}&idx=${idx}`;
  }
  return file.external?.url ?? "";
}

/** Retry transient Notion failures (timeouts, 429s, 5xx) with a short backoff. */
async function withRetry<T>(fn: () => Promise<T>, attempts = 3): Promise<T> {
  let lastError: unknown;
  for (let attempt = 0; attempt < attempts; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;
      if (attempt < attempts - 1) {
        await new Promise((resolve) => setTimeout(resolve, 1000 * (attempt + 1)));
      }
    }
  }
  throw lastError;
}

/**
 * Generic Notion database pagination — returns every page in the database.
 * Deliberately unfiltered and unsorted: property filters/sorts make Notion's
 * query slower and couple us to property names, and the large products DB was
 * timing out on them. Callers filter and sort in JS instead.
 */
async function paginateDatabase(databaseId: string): Promise<NotionPage[]> {
  const allResults: NotionPage[] = [];
  let hasMore = true;
  let startCursor: string | undefined = undefined;

  while (hasMore) {
    const response = await withRetry(() =>
      notion.databases.query({
        database_id: databaseId,
        start_cursor: startCursor,
        page_size: 50,
      })
    );

    allResults.push(...(response.results as NotionPage[]));
    hasMore = response.has_more;
    startCursor = response.next_cursor ?? undefined;
  }

  return allResults;
}

// ─── Mapping helpers (single source of truth per model) ──────────

function mapNotionPageToProduct(page: NotionPage): Product {
  const properties = page.properties;
  const name = properties["Name of product"]?.title?.[0]?.plain_text || "";

  return {
    id: page.id,
    slug: generateSlug(name),
    createdTime: page.created_time,
    lastEditedTime: page.last_edited_time,
    name,
    brand: properties.Brand?.select?.name || "",
    category: (properties.Category?.multi_select || []).map((s: NotionSelectOption) => s.name).join(", ") || "",
    levelOfProtection: properties["Level of Protection"]?.select?.name || "",
    gender: (properties.Gender?.multi_select || []).map((s: NotionSelectOption) => s.name).join(", ") || "",
    price: properties.Price?.number || 0,
    description: extractText(properties.Description?.rich_text || []),
    url: properties.URL?.url || "",
    photos: (properties.Photos?.files || [])
      .map((file: NotionFile, idx: number) => resolveFileUrl(page.id, file, "Photos", idx))
      .filter(Boolean),
    ridingStyle: (properties["Riding style"]?.multi_select || []).map((s: NotionSelectOption) => s.name),
    season: (properties.Season?.multi_select || []).map((s: NotionSelectOption) => s.name),
    waterproofLevel: properties["Level of Waterproof"]?.select?.name || "",
    materials: (properties.Materials?.multi_select || []).map((m: NotionSelectOption) => m.name),
    veganVerified: properties["Vegan Verified"]?.select?.name || "",
    staffFavorite: properties["Staff favorite"]?.checkbox || false,
  };
}

function mapNotionPageToBlogPost(page: NotionPage): BlogPost {
  const properties = page.properties;

  return {
    id: page.id,
    title: properties.Name?.title?.[0]?.plain_text || "",
    content: extractText(properties.Description?.rich_text || []),
    publishDate: properties.Date?.date?.start || "",
    featuredImage: resolveFileUrl(page.id, properties["Thumbnail Image"]?.files?.[0] as NotionFile | undefined, "Thumbnail Image", 0),
  };
}

// ─── Products ────────────────────────────────────────────────────

// Fetchers deliberately do NOT catch errors: a throw inside unstable_cache
// leaves the last good value in place, whereas returning [] would cache an
// empty catalog for the full revalidate window. The exported wrappers catch
// per-request so pages degrade gracefully without poisoning the cache.

async function fetchProductsFromNotion(): Promise<Product[]> {
  const pages = await paginateDatabase(process.env.NOTION_PRODUCTS_DB_ID!);
  return pages
    .map(mapNotionPageToProduct)
    // Rows created by the suggestion form live in the same database until
    // they're reviewed — keep them out of the public catalog and sitemap.
    .filter((product) => product.name !== "" && !product.name.startsWith("User Suggestion -"))
    .sort((a, b) => b.lastEditedTime.localeCompare(a.lastEditedTime));
}

const getProductsCached = unstable_cache(
  fetchProductsFromNotion,
  ["products"],
  { revalidate: REVALIDATE_TIME, tags: ["products"] }
);

export async function getProducts(): Promise<Product[]> {
  try {
    return await getProductsCached();
  } catch (error) {
    console.error("[Notion] Failed to fetch products:", error);
    return [];
  }
}

async function fetchProductFromNotion(id: string): Promise<Product | null> {
  const page = await withRetry(() => notion.pages.retrieve({ page_id: id }));
  return mapNotionPageToProduct(page as NotionPage);
}

const getProductCached = unstable_cache(
  fetchProductFromNotion,
  ["product"],
  { revalidate: REVALIDATE_TIME, tags: ["products"] }
);

export async function getProduct(id: string): Promise<Product | null> {
  try {
    return await getProductCached(id);
  } catch (error) {
    console.error("[Notion] Failed to fetch product:", error);
    return null;
  }
}

export async function getProductBySlug(slug: string): Promise<Product | null> {
  const products = await getProducts();
  return products.find((p) => p.slug === slug) || null;
}

// ─── Events ──────────────────────────────────────────────────────

async function fetchEventsFromNotion(): Promise<Event[]> {
  const pages = await paginateDatabase(process.env.NOTION_EVENTS_DB_ID!);

  return pages
    .map((page: NotionPage) => {
      const properties = page.properties;
      const dateRange = properties.Date?.date;
      const priceNumber = properties.Price?.number;

      return {
        id: page.id,
        name: properties["Name of event"]?.title?.[0]?.plain_text || "",
        startDate: dateRange?.start || "",
        endDate: dateRange?.end || dateRange?.start || "",
        description: extractText(properties.Description?.rich_text || []),
        location: extractText(properties.Location?.rich_text || []),
        url: properties.URL?.url || "",
        price: priceNumber ? `$${priceNumber.toFixed(2)}` : "Free",
        poster: resolveFileUrl(page.id, properties["Event poster"]?.files?.[0] as NotionFile | undefined, "Event poster", 0),
      };
    })
    .filter((event) => event.name !== "")
    .sort((a, b) => a.startDate.localeCompare(b.startDate));
}

const getEventsCached = unstable_cache(
  fetchEventsFromNotion,
  ["events"],
  { revalidate: REVALIDATE_TIME, tags: ["events"] }
);

export async function getEvents(): Promise<Event[]> {
  try {
    return await getEventsCached();
  } catch (error) {
    console.error("[Notion] Failed to fetch events:", error);
    return [];
  }
}

// ─── Blog ────────────────────────────────────────────────────────

async function fetchBlogPostsFromNotion(): Promise<BlogPost[]> {
  const pages = await paginateDatabase(process.env.NOTION_BLOG_DB_ID!);
  return pages
    .map(mapNotionPageToBlogPost)
    .filter((post) => post.title !== "")
    .sort((a, b) => b.publishDate.localeCompare(a.publishDate));
}

const getBlogPostsCached = unstable_cache(
  fetchBlogPostsFromNotion,
  ["blog-posts"],
  { revalidate: REVALIDATE_TIME, tags: ["blog"] }
);

export async function getBlogPosts(): Promise<BlogPost[]> {
  try {
    return await getBlogPostsCached();
  } catch (error) {
    console.error("[Notion] Failed to fetch blog posts:", error);
    return [];
  }
}

async function fetchBlogPostFromNotion(id: string): Promise<BlogPost | null> {
  const page = await withRetry(() => notion.pages.retrieve({ page_id: id }));
  return mapNotionPageToBlogPost(page as NotionPage);
}

const getBlogPostCached = unstable_cache(
  fetchBlogPostFromNotion,
  ["blog-post"],
  { revalidate: REVALIDATE_TIME, tags: ["blog"] }
);

export async function getBlogPost(id: string): Promise<BlogPost | null> {
  try {
    return await getBlogPostCached(id);
  } catch (error) {
    console.error("[Notion] Failed to fetch blog post:", error);
    return null;
  }
}
