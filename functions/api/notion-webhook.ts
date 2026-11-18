// POST /api/notion-webhook: Notion calls this when a page changes.
//
// The site is static, so "refresh" means "rebuild": human edits and structural
// events (created, deleted, restored, moved) start the deploy workflow.
// GitHub's concurrency group in that workflow keeps at most one build running
// and one queued, so a burst of edits becomes one or two builds.
// Edits made by integrations (enrichment task, scripts) arrive in bursts of
// dozens; they wait for the scheduled rebuild instead.
import { dispatchWorkflow, json, verifyNotionSignature, type PagesContext } from "../../lib/cloudflare/shared"

type NotionEvent = {
  type?: string
  verification_token?: string
  entity?: { id?: string; type?: string }
  authors?: Array<{ id?: string; type?: string }>
  data?: { id?: string }
}

function isBotEdit(event: NotionEvent): boolean {
  const isEdit = /^page\.(properties_updated|content_updated)$/.test(event.type || "")
  const authors = event.authors ?? []
  return isEdit && authors.length > 0 && authors.every((a) => a.type === "bot" || a.type === "agent")
}

export async function onRequestPost({ request, env }: PagesContext): Promise<Response> {
  const rawBody = await request.text()

  // Notion's one-time verification handshake: the token shows up in the
  // Pages Functions real-time logs, to paste into the Notion integration UI.
  try {
    const parsed = JSON.parse(rawBody) as NotionEvent
    if (parsed?.verification_token) {
      console.log("=== NOTION VERIFICATION TOKEN ===", parsed.verification_token)
      return json({ ok: true })
    }
  } catch {
    /* not JSON, fall through to the signature check */
  }

  if (!(await verifyNotionSignature(env.NOTION_WEBHOOK_SECRET, rawBody, request.headers.get("x-notion-signature")))) {
    return json({ error: "invalid signature" }, 401)
  }

  let payload: NotionEvent
  try {
    payload = JSON.parse(rawBody)
  } catch {
    return json({ error: "invalid json" }, 400)
  }

  const eventType = payload.type || ""
  // Locking or unlocking a page changes nothing the site shows.
  const changesContent = eventType.startsWith("page.") && !/^page\.(un)?locked$/.test(eventType)
  const rebuild = changesContent && !isBotEdit(payload)
  const pageId = payload.entity?.id || payload.data?.id

  // Always answer 200 once the event is verified: Notion pauses the
  // subscription after repeated errors, and a failed dispatch is our problem.
  const errors: string[] = []
  if (rebuild) {
    try {
      await dispatchWorkflow(env, env.GH_DEPLOY_WORKFLOW || "deploy-cloudflare.yml")
    } catch (e) {
      errors.push(String(e))
    }
  }
  if (env.GH_AUDIT_WORKFLOW && pageId && /page\.(created|content_updated)/.test(eventType)) {
    try {
      await dispatchWorkflow(env, env.GH_AUDIT_WORKFLOW, { page_id: pageId })
    } catch (e) {
      errors.push(String(e))
    }
  }
  if (errors.length) console.error("[notion-webhook]", errors.join(" | "))
  return json({ ok: true, event: eventType, rebuild, errors })
}
