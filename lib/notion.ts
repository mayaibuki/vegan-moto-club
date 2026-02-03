import { Client } from "@notionhq/client";

const notion = new Client({
  auth: process.env.NEXT_PUBLIC_NOTION_API_KEY,
});

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

// Helper function to extract text from rich text blocks
function extractText(richText: any[]): string {
  return richText.map((block) => block.plain_text).join("");
}

// Helper function to get image URL from files
function getImageUrl(file: any): string | null {
  if (!file) return null;
  if (file.type === "external") {
    return file.external.url;
  } else if (file.type === "file") {
    return file.file.url;
  }
  return null;
}

// Fetch all products
export async function getProducts(): Promise<Product[]> {
  try {
    const response = await notion.databases.query({
      database_id: process.env.NOTION_PRODUCTS_DB_ID!,
      filter: {
        property: "Name of product",
        title: {
          is_not_empty: true,
        },
      },
    });

    return response.results.map((page: any) => {
      const properties = page.properties;

      return {
        id: page.id,
        name: properties["Name of product"]?.title?.[0]?.plain_text || "",
        brand: extractText(properties.Brand?.rich_text || []),
        category: properties.Category?.select?.name || "",
        levelOfProtection: properties["Level of Protection"]?.select?.name || "",
        gender: properties.Gender?.select?.name || "",
        price: properties.Price?.number || 0,
        description: extractText(properties.Description?.rich_text || []),
        url: extractText(properties.URL?.rich_text || []),
        photos: (properties.Photos?.files || [])
          .map((file: any) => getImageUrl(file))
          .filter(Boolean) as string[],
        ridingStyle: (properties["Riding style"]?.multi_select || []).map(
          (s: any) => s.name
        ),
        season: (properties.Season?.multi_select || []).map((s: any) => s.name),
        waterproofLevel: properties["Level of Waterproof"]?.select?.name || "",
        materials: (properties.Materials?.multi_select || []).map(
          (m: any) => m.name
        ),
        veganVerified: properties["Vegan Verified"]?.select?.name || "",
        staffFavorite: properties["Staff favorite"]?.checkbox || false,
      };
    });
  } catch (error) {
    console.error("Error fetching products:", error);
    return [];
  }
}

// Get a single product by ID
export async function getProduct(id: string): Promise<Product | null> {
  try {
    const page = await notion.pages.retrieve({ page_id: id });
    const properties = (page as any).properties;

    return {
      id: page.id,
      name: properties["Name of product"]?.title?.[0]?.plain_text || "",
      brand: extractText(properties.Brand?.rich_text || []),
      category: properties.Category?.select?.name || "",
      levelOfProtection: properties["Level of Protection"]?.select?.name || "",
      gender: properties.Gender?.select?.name || "",
      price: properties.Price?.number || 0,
      description: extractText(properties.Description?.rich_text || []),
      url: extractText(properties.URL?.rich_text || []),
      photos: (properties.Photos?.files || [])
        .map((file: any) => getImageUrl(file))
        .filter(Boolean) as string[],
      ridingStyle: (properties["Riding style"]?.multi_select || []).map(
        (s: any) => s.name
      ),
      season: (properties.Season?.multi_select || []).map((s: any) => s.name),
      waterproofLevel: properties["Level of Waterproof"]?.select?.name || "",
      materials: (properties.Materials?.multi_select || []).map(
        (m: any) => m.name
      ),
      veganVerified: properties["Vegan Verified"]?.select?.name || "",
      staffFavorite: properties["Staff favorite"]?.checkbox || false,
    };
  } catch (error) {
    console.error("Error fetching product:", error);
    return null;
  }
}

// Fetch all events
export async function getEvents(): Promise<Event[]> {
  try {
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
    });

    return response.results.map((page: any) => {
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
    console.error("Error fetching events:", error);
    return [];
  }
}

// Fetch all blog posts
export async function getBlogPosts(): Promise<BlogPost[]> {
  try {
    const response = await notion.databases.query({
      database_id: process.env.NOTION_BLOG_DB_ID!,
      filter: {
        property: "Name",
        title: {
          is_not_empty: true,
        },
      },
    });

    return response.results.map((page: any) => {
      const properties = page.properties;

      return {
        id: page.id,
        title: properties.Name?.title?.[0]?.plain_text || "",
        content: extractText(properties.Description?.rich_text || []),
        publishDate: "",
        featuredImage: getImageUrl(
          properties["Thumbnail Image"]?.files?.[0]
        ) || "",
      };
    });
  } catch (error) {
    console.error("Error fetching blog posts:", error);
    return [];
  }
}

// Get a single blog post by ID
export async function getBlogPost(id: string): Promise<BlogPost | null> {
  try {
    const page = await notion.pages.retrieve({ page_id: id });
    const properties = (page as any).properties;

    return {
      id: page.id,
      title: properties.Name?.title?.[0]?.plain_text || "",
      content: extractText(properties.Description?.rich_text || []),
      publishDate: "",
      featuredImage: getImageUrl(
        properties["Thumbnail Image"]?.files?.[0]
      ) || "",
    };
  } catch (error) {
    console.error("Error fetching blog post:", error);
    return null;
  }
}
