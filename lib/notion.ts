import { Client } from "@notionhq/client";
import { unstable_cache } from "next/cache";

const notion = new Client({
  auth: process.env.NOTION_API_KEY,
});

// Revalidation time in seconds (1 hour for production, shorter for development)
const REVALIDATE_TIME = process.env.NODE_ENV === "production" ? 3600 : 60;

export interface Product {
  id: string;
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
}

export interface BlogPost {
  id: string;
  title: string;
  content: string;
  publishDate: string;
  featuredImage: string;
}

// Notion API response types
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
  last_edited_time: string
  properties: NotionPageProperties
}

// Helper function to extract text from rich text blocks
function extractText(richText: NotionRichText[]): string {
  return richText.map((block) => block.plain_text).join("");
}

// Helper function to get image URL from files
function getImageUrl(file: NotionFile): string | null {
  if (!file) return null;
  if (file.type === "external") {
    return file.external?.url ?? null;
  } else if (file.type === "file") {
    return file.file?.url ?? null;
  }
  return null;
}

// Internal function to fetch products from Notion
async function fetchProductsFromNotion(): Promise<Product[]> {
  try {
    const allResults: NotionPage[] = [];
    let hasMore = true;
    let startCursor: string | undefined = undefined;

    // Paginate through all results (Notion API returns max 100 per request)
    while (hasMore) {
      const response = await notion.databases.query({
        database_id: process.env.NOTION_PRODUCTS_DB_ID!,
        filter: {
          property: "Name of product",
          title: {
            is_not_empty: true,
          },
        },
        sorts: [
          {
            timestamp: "last_edited_time",
            direction: "descending" as const,
          },
        ],
        start_cursor: startCursor,
        page_size: 100,
      });

      allResults.push(...(response.results as NotionPage[]));
      hasMore = response.has_more;
      startCursor = response.next_cursor ?? undefined;
    }

    return allResults.map((page: NotionPage) => {
      const properties = page.properties;

      return {
        id: page.id,
        lastEditedTime: page.last_edited_time,
        name: properties["Name of product"]?.title?.[0]?.plain_text || "",
        brand: properties.Brand?.select?.name || "",
        category: (properties.Category?.multi_select || []).map((s: NotionSelectOption) => s.name).join(", ") || "",
        levelOfProtection: properties["Level of Protection"]?.select?.name || "",
        gender: (properties.Gender?.multi_select || []).map((s: NotionSelectOption) => s.name).join(", ") || "",
        price: properties.Price?.number || 0,
        description: extractText(properties.Description?.rich_text || []),
        url: properties.URL?.url || "",
        photos: (properties.Photos?.files || [])
          .map((file: NotionFile) => getImageUrl(file))
          .filter(Boolean) as string[],
        ridingStyle: (properties["Riding style"]?.multi_select || []).map(
          (s: NotionSelectOption) => s.name
        ),
        season: (properties.Season?.multi_select || []).map((s: NotionSelectOption) => s.name),
        waterproofLevel: properties["Level of Waterproof"]?.select?.name || "",
        materials: (properties.Materials?.multi_select || []).map(
          (m: NotionSelectOption) => m.name
        ),
        veganVerified: properties["Vegan Verified"]?.select?.name || "",
        staffFavorite: properties["Staff favorite"]?.checkbox || false,
      };
    });
  } catch (error) {
    console.error("[Notion] Failed to fetch products:", error);
    return [];
  }
}

// Cached version of getProducts with revalidation
export const getProducts = unstable_cache(
  fetchProductsFromNotion,
  ["products"],
  { revalidate: REVALIDATE_TIME, tags: ["products"] }
);

// Internal function to fetch single product from Notion
async function fetchProductFromNotion(id: string): Promise<Product | null> {
  try {
    const page = await notion.pages.retrieve({ page_id: id });
    const properties = (page as NotionPage).properties;

    return {
      id: page.id,
      lastEditedTime: (page as NotionPage).last_edited_time,
      name: properties["Name of product"]?.title?.[0]?.plain_text || "",
      brand: properties.Brand?.select?.name || "",
      category: (properties.Category?.multi_select || []).map((s: NotionSelectOption) => s.name).join(", ") || "",
      levelOfProtection: properties["Level of Protection"]?.select?.name || "",
      gender: (properties.Gender?.multi_select || []).map((s: NotionSelectOption) => s.name).join(", ") || "",
      price: properties.Price?.number || 0,
      description: extractText(properties.Description?.rich_text || []),
      url: properties.URL?.url || "",
      photos: (properties.Photos?.files || [])
        .map((file: NotionFile) => getImageUrl(file))
        .filter(Boolean) as string[],
      ridingStyle: (properties["Riding style"]?.multi_select || []).map(
        (s: NotionSelectOption) => s.name
      ),
      season: (properties.Season?.multi_select || []).map((s: NotionSelectOption) => s.name),
      waterproofLevel: properties["Level of Waterproof"]?.select?.name || "",
      materials: (properties.Materials?.multi_select || []).map(
        (m: NotionSelectOption) => m.name
      ),
      veganVerified: properties["Vegan Verified"]?.select?.name || "",
      staffFavorite: properties["Staff favorite"]?.checkbox || false,
    };
  } catch (error) {
    console.error("[Notion] Failed to fetch product:", error);
    return null;
  }
}

// Get a single product by ID with caching
export async function getProduct(id: string): Promise<Product | null> {
  const getCachedProduct = unstable_cache(
    () => fetchProductFromNotion(id),
    [`product-${id}`],
    { revalidate: REVALIDATE_TIME, tags: ["products", `product-${id}`] }
  );
  return getCachedProduct();
}

// Internal function to fetch events from Notion
async function fetchEventsFromNotion(): Promise<Event[]> {
  try {
    const allResults: NotionPage[] = [];
    let hasMore = true;
    let startCursor: string | undefined = undefined;

    // Paginate through all results (Notion API returns max 100 per request)
    while (hasMore) {
      const response = await notion.databases.query({
        database_id: process.env.NOTION_EVENTS_DB_ID!,
        filter: {
          property: "Name of event",
          title: {
            is_not_empty: true,
          },
        },
        sorts: [
          {
            property: "Date",
            direction: "ascending",
          },
        ],
        start_cursor: startCursor,
        page_size: 100,
      });

      allResults.push(...(response.results as NotionPage[]));
      hasMore = response.has_more;
      startCursor = response.next_cursor ?? undefined;
    }

    return allResults.map((page: NotionPage) => {
      const properties = page.properties;
      const dateRange = properties.Date?.date;

      return {
        id: page.id,
        name: properties["Name of event"]?.title?.[0]?.plain_text || "",
        startDate: dateRange?.start || "",
        endDate: dateRange?.end || dateRange?.start || "",
        description: extractText(properties.Description?.rich_text || []),
        location: extractText(properties.Location?.rich_text || []),
        url: extractText(properties.URL?.rich_text || []),
        price: extractText(properties.Price?.rich_text || []) || "Free",
      };
    });
  } catch (error) {
    console.error("[Notion] Failed to fetch events:", error);
    return [];
  }
}

// Cached version of getEvents with revalidation
export const getEvents = unstable_cache(
  fetchEventsFromNotion,
  ["events"],
  { revalidate: REVALIDATE_TIME, tags: ["events"] }
);

// Internal function to fetch blog posts from Notion
async function fetchBlogPostsFromNotion(): Promise<BlogPost[]> {
  try {
    const allResults: NotionPage[] = [];
    let hasMore = true;
    let startCursor: string | undefined = undefined;

    while (hasMore) {
      const response = await notion.databases.query({
        database_id: process.env.NOTION_BLOG_DB_ID!,
        filter: {
          property: "Name",
          title: {
            is_not_empty: true,
          },
        },
        sorts: [
          {
            property: "Date",
            direction: "descending",
          },
        ],
        start_cursor: startCursor,
        page_size: 100,
      });

      allResults.push(...(response.results as NotionPage[]));
      hasMore = response.has_more;
      startCursor = response.next_cursor ?? undefined;
    }

    return allResults.map((page: NotionPage) => {
      const properties = page.properties;

      return {
        id: page.id,
        title: properties.Name?.title?.[0]?.plain_text || "",
        content: extractText(properties.Description?.rich_text || []),
        publishDate: properties.Date?.date?.start || "",
        featuredImage: getImageUrl(
          properties["Thumbnail Image"]?.files?.[0] as NotionFile
        ) || "",
      };
    });
  } catch (error) {
    console.error("[Notion] Failed to fetch blog posts:", error);
    return [];
  }
}

// Cached version of getBlogPosts with revalidation
export const getBlogPosts = unstable_cache(
  fetchBlogPostsFromNotion,
  ["blog-posts"],
  { revalidate: REVALIDATE_TIME, tags: ["blog"] }
);

// Internal function to fetch single blog post from Notion
async function fetchBlogPostFromNotion(id: string): Promise<BlogPost | null> {
  try {
    const page = await notion.pages.retrieve({ page_id: id });
    const properties = (page as NotionPage).properties;

    return {
      id: page.id,
      title: properties.Name?.title?.[0]?.plain_text || "",
      content: extractText(properties.Description?.rich_text || []),
      publishDate: properties.Date?.date?.start || "",
      featuredImage: getImageUrl(
        properties["Thumbnail Image"]?.files?.[0] as NotionFile
      ) || "",
    };
  } catch (error) {
    console.error("[Notion] Failed to fetch blog post:", error);
    return null;
  }
}

// Get a single blog post by ID with caching
export async function getBlogPost(id: string): Promise<BlogPost | null> {
  const getCachedBlogPost = unstable_cache(
    () => fetchBlogPostFromNotion(id),
    [`blog-post-${id}`],
    { revalidate: REVALIDATE_TIME, tags: ["blog", `blog-post-${id}`] }
  );
  return getCachedBlogPost();
}
