#!/bin/sh
# One-time: copies the secrets the Cloudflare deploy needs, without printing them.
#   GitHub Actions  <- NOTION_* from .env.local, plus CLOUDFLARE_API_TOKEN (you paste it)
#   Pages Functions <- NOTION_* from .env.local, NOTION_WEBHOOK_SECRET and GH_DISPATCH_TOKEN from Vercel
# Needs: gh (signed in), wrangler (signed in), vercel (signed in, project linked).
# Usage: sh scripts/cloudflare-secrets.sh
set -e
cd "$(dirname "$0")/.."
PROJECT=${CF_PAGES_PROJECT:-vegan-moto-club}
val() { sed -n "s/^$1=//p" "$2" | head -1 | sed 's/^"//; s/"$//'; }

for k in NOTION_API_KEY NOTION_PRODUCTS_DB_ID NOTION_EVENTS_DB_ID NOTION_BLOG_DB_ID; do
  v=$(val "$k" .env.local)
  [ -n "$v" ] || { echo "Missing $k in .env.local"; exit 1; }
  printf %s "$v" | gh secret set "$k" >/dev/null
  printf %s "$v" | npx wrangler pages secret put "$k" --project-name "$PROJECT" >/dev/null 2>&1
  echo "set $k (GitHub + Cloudflare)"
done

tmp=$(mktemp)
vercel env pull --yes --environment=production "$tmp" >/dev/null 2>&1 || true
for k in NOTION_WEBHOOK_SECRET GH_DISPATCH_TOKEN; do
  v=$(val "$k" "$tmp")
  if [ -n "$v" ]; then
    printf %s "$v" | npx wrangler pages secret put "$k" --project-name "$PROJECT" >/dev/null 2>&1
    echo "set $k (Cloudflare)"
  else
    echo "SKIPPED $k: Vercel would not export it (sensitive). Add it by hand in Cloudflare."
  fi
done
rm -f "$tmp"

echo
echo "Paste the Cloudflare API token, then press Enter:"
gh secret set CLOUDFLARE_API_TOKEN
echo "Done."
