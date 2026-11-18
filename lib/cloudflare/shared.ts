// Helpers for the Cloudflare Pages Functions in functions/api/. They run on
// Cloudflare's Workers runtime, not Node: use fetch and Web Crypto only, and no
// imports from the Next.js app (the Notion SDK and next/server are not available).

export interface Env {
  NOTION_API_KEY: string
  NOTION_PRODUCTS_DB_ID: string
  NOTION_EVENTS_DB_ID: string
  NOTION_BLOG_DB_ID: string
  NOTION_WEBHOOK_SECRET?: string
  /** GitHub token allowed to run workflows (fine-grained: Actions read/write on this repo). */
  GH_DISPATCH_TOKEN?: string
  GH_OWNER?: string
  GH_REPO?: string
  /** Workflow that rebuilds and redeploys the site. */
  GH_DEPLOY_WORKFLOW?: string
  /** Optional workflow to run for new or edited pages (the old product audit). Unset = skip. */
  GH_AUDIT_WORKFLOW?: string
}

export interface PagesContext {
  request: Request
  env: Env
}

export function json(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  })
}

// Best-effort limit of 5 submissions per IP per hour. Workers keep this map per
// isolate, so it is a speed bump, not a guarantee; the honeypot field does most of the work.
const rateLimit = new Map<string, { count: number; resetTime: number }>()
const RATE_LIMIT_MAX = 5
const RATE_LIMIT_WINDOW = 60 * 60 * 1000

export function isRateLimited(request: Request): boolean {
  const ip = request.headers.get("CF-Connecting-IP") || "unknown"
  const now = Date.now()
  const entry = rateLimit.get(ip)
  if (!entry || now > entry.resetTime) {
    rateLimit.set(ip, { count: 1, resetTime: now + RATE_LIMIT_WINDOW })
    return false
  }
  if (entry.count >= RATE_LIMIT_MAX) return true
  entry.count++
  return false
}

export const rateLimitResponse = () => json({ error: "Too many submissions. Please try again later." }, 429)

export function isValidUrl(str: string): boolean {
  try {
    const url = new URL(str)
    return url.protocol === "http:" || url.protocol === "https:"
  } catch {
    return false
  }
}

/** Create a row in a Notion database through the REST API. */
export async function createNotionPage(env: Env, databaseId: string, properties: Record<string, unknown>) {
  const res = await fetch("https://api.notion.com/v1/pages", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${env.NOTION_API_KEY}`,
      "Notion-Version": "2022-06-28",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ parent: { database_id: databaseId }, properties }),
  })
  if (!res.ok) throw new Error(`Notion ${res.status}: ${await res.text()}`)
}

/** Start a GitHub Actions workflow on main. */
export async function dispatchWorkflow(env: Env, workflow: string, inputs?: Record<string, string>) {
  if (!env.GH_DISPATCH_TOKEN) throw new Error("GH_DISPATCH_TOKEN not configured")
  const owner = env.GH_OWNER || "mayaibuki"
  const repo = env.GH_REPO || "vegan-moto-club"
  const res = await fetch(`https://api.github.com/repos/${owner}/${repo}/actions/workflows/${workflow}/dispatches`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${env.GH_DISPATCH_TOKEN}`,
      Accept: "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28",
      "User-Agent": "vegan-moto-club-webhook",
    },
    body: JSON.stringify({ ref: "main", ...(inputs ? { inputs } : {}) }),
  })
  if (!res.ok) throw new Error(`GitHub dispatch ${workflow} failed: ${res.status} ${await res.text()}`)
}

/** Hex HMAC-SHA256 of body, compared in constant time with Notion's signature header. */
export async function verifyNotionSignature(secret: string | undefined, body: string, signature: string | null) {
  if (!secret || !signature) return false
  const key = await crypto.subtle.importKey("raw", new TextEncoder().encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["sign"])
  const mac = new Uint8Array(await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(body)))
  const expected = Array.from(mac, (b) => b.toString(16).padStart(2, "0")).join("")
  const given = signature.startsWith("sha256=") ? signature.slice(7) : signature
  if (given.length !== expected.length) return false
  let diff = 0
  for (let i = 0; i < expected.length; i++) diff |= expected.charCodeAt(i) ^ given.charCodeAt(i)
  return diff === 0
}
