import { NextRequest, NextResponse } from "next/server";
import crypto from "crypto";

export const runtime = "nodejs";

const NOTION_WEBHOOK_SECRET = process.env.NOTION_WEBHOOK_SECRET;
const GH_TOKEN = process.env.GH_DISPATCH_TOKEN;
const GH_OWNER = process.env.GH_OWNER || "mayaibuki";
const GH_REPO  = process.env.GH_REPO  || "vegan-moto-club";
const GH_WORKFLOW = process.env.GH_WORKFLOW || "product-audit.yml";

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

async function dispatchWorkflow(pageId: string) {
  if (!GH_TOKEN) throw new Error("GH_DISPATCH_TOKEN not configured");
  const url = `https://api.github.com/repos/${GH_OWNER}/${GH_REPO}/actions/workflows/${GH_WORKFLOW}/dispatches`;
  const res = await fetch(url, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${GH_TOKEN}`,
      Accept: "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28",
    },
    body: JSON.stringify({ ref: "main", inputs: { page_id: pageId } }),
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`GitHub dispatch failed: ${res.status} ${body}`);
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

  let payload: { type?: string; entity?: { id?: string }; data?: { id?: string } };
  try {
    payload = JSON.parse(rawBody);
  } catch {
    return NextResponse.json({ error: "invalid json" }, { status: 400 });
  }

  // Only act on page-created / page-content-updated events.
  const eventType = payload.type || "";
  if (!/page\.(created|content_updated)/.test(eventType)) {
    return NextResponse.json({ ok: true, skipped: eventType });
  }

  const pageId = payload.entity?.id || payload.data?.id;
  if (!pageId) {
    return NextResponse.json({ error: "no page id in payload" }, { status: 400 });
  }

  // Always acknowledge with 200 once the event is verified. Notion pauses the
  // subscription after sustained non-2xx responses, and a failed GitHub
  // dispatch is our problem, not a delivery problem. The weekly cron in
  // product-audit.yml picks up anything missed here.
  try {
    await dispatchWorkflow(pageId);
  } catch (e) {
    console.error("dispatchWorkflow failed", e);
    return NextResponse.json({ ok: true, dispatched: false, error: String(e) });
  }
  return NextResponse.json({ ok: true, dispatched: pageId });
}
