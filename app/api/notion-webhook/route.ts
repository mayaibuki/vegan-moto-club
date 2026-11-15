// Notion webhook: refreshes the site's cached Notion data (products, events, blog)
// when a page changes. Verifies Notion's signature, then revalidates cache tags.
import { NextRequest, NextResponse } from "next/server";
import { revalidateTag } from "next/cache";
import crypto from "crypto";

export const runtime = "nodejs";

const NOTION_WEBHOOK_SECRET = process.env.NOTION_WEBHOOK_SECRET;

// Cache tags used by the fetchers in lib/notion.ts, keyed by the database they read.
const DB_TAGS: Array<[string | undefined, string]> = [
  [process.env.NOTION_PRODUCTS_DB_ID, "products"],
  [process.env.NOTION_EVENTS_DB_ID, "events"],
  [process.env.NOTION_BLOG_DB_ID, "blog"],
];

type NotionParent = { id?: string; type?: string; database_id?: string; data_source_id?: string };
type NotionEvent = {
  type?: string;
  entity?: { id?: string; type?: string };
  authors?: Array<{ id?: string; type?: string }>;
  data?: { id?: string; parent?: NotionParent };
};

// Edits made by integrations (the daily enrichment task)
// arrive in bursts of dozens of events. Each one used to clear the products cache,
// so the next visitors all triggered a full Notion re-fetch at once and hit 429s.
// Those edits can wait for the hourly refresh; human edits and structural events
// (created, deleted, restored, moved) still refresh immediately.
function isBotEdit(event: NotionEvent): boolean {
  const isEdit = /^page\.(properties_updated|content_updated)$/.test(event.type || "");
  const authors = event.authors ?? [];
  return isEdit && authors.length > 0 && authors.every((a) => a.type === "bot" || a.type === "agent");
}

const bareId = (id?: string) => (id || "").replace(/-/g, "").toLowerCase();

// Which cached data a changed page belongs to. Newer Notion API versions report the
// parent as a data source, whose id differs from the database ids in our env vars;
// when nothing matches, refreshing all three tags is cheap and never wrong.
function tagsFor(parent?: NotionParent): string[] {
  const ids = [parent?.id, parent?.database_id, parent?.data_source_id].map(bareId).filter(Boolean);
  const hits = DB_TAGS.filter(([dbId]) => dbId && ids.includes(bareId(dbId))).map(([, tag]) => tag);
  return hits.length ? hits : DB_TAGS.map(([, tag]) => tag);
}

function verifySignature(rawBody: string, signature: string | null): boolean {
  if (!NOTION_WEBHOOK_SECRET || !signature) return false;
  const expected = crypto
    .createHmac("sha256", NOTION_WEBHOOK_SECRET)
    .update(rawBody)
    .digest("hex");
  const sig = signature.startsWith("sha256=") ? signature.slice(7) : signature;
  try {
    return crypto.timingSafeEqual(Buffer.from(expected), Buffer.from(sig));
  } catch {
    return false;
  }
}

export async function POST(req: NextRequest) {
  const rawBody = await req.text();

  // Notion's verification handshake: log the token loud and clear so it can be
  // retrieved from Vercel runtime logs and pasted into the Notion UI.
  try {
    const parsed = JSON.parse(rawBody);
    if (parsed?.verification_token) {
      console.log("=== NOTION VERIFICATION TOKEN ===");
      console.log(parsed.verification_token);
      console.log("=================================");
      return NextResponse.json({ ok: true });
    }
  } catch { /* not JSON, fall through */ }

  const signature = req.headers.get("x-notion-signature");
  if (!verifySignature(rawBody, signature)) {
    return NextResponse.json({ error: "invalid signature" }, { status: 401 });
  }

  let payload: NotionEvent;
  try {
    payload = JSON.parse(rawBody);
  } catch {
    return NextResponse.json({ error: "invalid json" }, { status: 400 });
  }

  const eventType = payload.type || "";

  // Refresh the site's cached Notion data on any page change (created, edited,
  // properties updated, moved, deleted, restored). Without this, an edit waits for
  // both the hourly data cache and the hourly page cache to expire, up to ~2 hours.
  // Locking or unlocking a page changes nothing the site shows.
  const changesContent = eventType.startsWith("page.") && !/^page\.(un)?locked$/.test(eventType);
  const skippedBotEdit = changesContent && isBotEdit(payload);
  const revalidated = changesContent && !skippedBotEdit ? tagsFor(payload.data?.parent) : [];
  for (const tag of revalidated) revalidateTag(tag);
  if (skippedBotEdit) {
    console.log("[notion-webhook] skipped cache refresh for bot edit", eventType, payload.entity?.id || payload.data?.id);
  }

  return NextResponse.json({ ok: true, event: eventType, revalidated });
}
