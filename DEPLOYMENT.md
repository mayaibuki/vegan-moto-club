# Deployment — Vegan Moto Club

## Live Site

**URL:** https://veganmotoclub.com
**Hosting:** Vercel (Hobby plan)
**Deploy model:** Auto-deploy on push to `main` via GitHub integration

## Environment Variables

Set these in Vercel Dashboard → Settings → Environment Variables:

| Variable | Description |
|----------|-------------|
| `NOTION_API_KEY` | Notion integration token |
| `NOTION_PRODUCTS_DB_ID` | Products database ID |
| `NOTION_EVENTS_DB_ID` | Events database ID |
| `NOTION_BLOG_DB_ID` | Blog database ID |
| `NEXT_PUBLIC_SITE_URL` | `https://veganmotoclub.com` |

## How Deploys Work

1. Push code to `main` branch on GitHub
2. Vercel automatically detects the push and starts a build
3. Build runs `npm run build` (Next.js production build)
4. On success, the new version goes live at veganmotoclub.com
5. Preview deployments are created automatically for PRs

## Adding a Preview Domain

1. Go to Vercel Dashboard → your project → Settings → Domains
2. Click "Add Domain"
3. Enter the domain and follow DNS setup instructions
4. HTTPS certificate auto-generates

## Re-running a Deployment

- **From dashboard:** Vercel Dashboard → Deployments → click the three dots on any deployment → Redeploy
- **From CLI:** `vercel --prod` (requires Vercel CLI installed globally)

## Logs & Monitoring

- **Build logs:** Vercel Dashboard → Deployments → click any deployment
- **Runtime logs:** Vercel Dashboard → your project → Logs tab
- **Analytics:** Vercel Dashboard → Analytics (Vercel Analytics installed)
- **Performance:** Vercel Dashboard → Speed Insights (Speed Insights installed)
