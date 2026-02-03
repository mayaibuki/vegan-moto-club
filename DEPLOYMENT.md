# Deployment Guide - Vegan Moto Club

This guide walks you through deploying your website to Vercel and connecting your custom domain.

## Prerequisites

✅ Project files ready (you have them!)
✅ Notion API credentials configured
✅ GitHub account (recommended)
✅ Vercel account (free)

---

## Step 1: Prepare Your Local Project

### 1.1 Test Locally

Before deploying, test your site locally:

```bash
cd /Users/mayaibuki/Documents/Claude/vegan-moto-club
npm install
npm run dev
```

Visit `http://localhost:3000` and verify everything works.

### 1.2 Verify Environment Variables

Make sure `.env.local` contains:
```
NEXT_PUBLIC_NOTION_API_KEY=YOUR_NOTION_API_KEY
NOTION_PRODUCTS_DB_ID=YOUR_PRODUCTS_DATABASE_ID
NOTION_EVENTS_DB_ID=YOUR_EVENTS_DATABASE_ID
NOTION_BLOG_DB_ID=YOUR_BLOG_DATABASE_ID
```

---

## Step 2: Push to GitHub

### 2.1 Create a GitHub Repository

1. Go to [github.com](https://github.com) and sign in
2. Click **+** → **New repository**
3. Name it: `vegan-moto-club`
4. Set to **Public** (Vercel needs this)
5. Click **Create repository**

### 2.2 Push Your Code

```bash
cd /Users/mayaibuki/Documents/Claude/vegan-moto-club

# Initialize git
git init
git add .
git commit -m "Initial commit: Vegan Moto Club website"

# Add remote and push
git remote add origin https://github.com/YOUR_USERNAME/vegan-moto-club.git
git branch -M main
git push -u origin main
```

**Important**: Replace `YOUR_USERNAME` with your actual GitHub username.

---

## Step 3: Deploy to Vercel

### Option A: Using Vercel Dashboard (Easiest)

1. **Go to [vercel.com](https://vercel.com)**
2. Sign up or log in (can use GitHub login)
3. Click **Add New Project**
4. **Import your GitHub repository**
   - Connect your GitHub account if needed
   - Select `vegan-moto-club` repo
   - Click **Import**
5. **Configure Project**
   - Framework: Next.js (should auto-detect)
   - Root Directory: ./
   - Build Command: `npm run build` (default)
6. **Add Environment Variables**
   - Click **Environment Variables**
   - Add these variables:
     ```
     NEXT_PUBLIC_NOTION_API_KEY = YOUR_NOTION_API_KEY
     NOTION_PRODUCTS_DB_ID = YOUR_PRODUCTS_DATABASE_ID
     NOTION_EVENTS_DB_ID = YOUR_EVENTS_DATABASE_ID
     NOTION_BLOG_DB_ID = YOUR_BLOG_DATABASE_ID
     ```
7. **Deploy**
   - Click **Deploy**
   - Wait 2-5 minutes for build to complete
   - Your site will be live at: `https://vegan-moto-club.vercel.app`

### Option B: Using Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy from your project directory
cd /Users/mayaibuki/Documents/Claude/vegan-moto-club
vercel

# You'll be prompted to:
# - Login to Vercel
# - Confirm project details
# - Add environment variables
# - Deploy!
```

---

## Step 4: Connect Your Custom Domain

### 4.1 In Vercel Dashboard

1. Go to your project on **vercel.com**
2. Click **Settings** → **Domains**
3. Click **Add Domain**
4. Enter: `veganmotoclub.com`
5. Click **Add**
6. Vercel will show you two options:

#### Option A: Use Vercel Nameservers (Recommended)

1. Copy Vercel's nameservers shown in the dashboard
2. Go to your domain registrar (GoDaddy, Namecheap, etc.)
3. Update your domain's DNS nameservers to:
   ```
   ns1.vercel-dns.com
   ns2.vercel-dns.com
   ```
4. Wait 5-48 hours for propagation
5. Vercel will auto-verify once DNS propagates

#### Option B: Add DNS Records Manually

If your registrar doesn't allow nameserver changes:

1. Get your domain registrar's DNS panel
2. Add the CNAME records Vercel provides
3. Wait for verification

### 4.2 Verify Setup

Once DNS propagates:
- Visit `https://veganmotoclub.com`
- Should show your site!
- HTTPS certificate auto-generates

---

## Step 5: Automatic Deployments

Once connected to GitHub, Vercel automatically deploys when you push code:

```bash
# Make changes locally
git add .
git commit -m "Update product colors"
git push origin main

# Vercel automatically builds & deploys!
# Check progress at vercel.com
```

---

## Post-Deployment Checklist

- [ ] Site loads at `veganmotoclub.com`
- [ ] All products display from Notion
- [ ] Filters work correctly
- [ ] Dark mode toggle works
- [ ] Mobile responsive (test on phone)
- [ ] Images load correctly
- [ ] Links work (Products, Events, Blog, About)
- [ ] Form embed works
- [ ] HTTPS shows (lock icon in browser)

---

## Updating Your Website

### Update Content (No Code Changes)

1. Edit in Notion (prices, products, events, blog)
2. Wait 5-10 seconds
3. Refresh website
4. Changes appear automatically!

### Update Code

1. Make changes locally
2. Test with `npm run dev`
3. Push to GitHub:
   ```bash
   git add .
   git commit -m "Your change description"
   git push origin main
   ```
4. Vercel auto-deploys (watch at vercel.com)

### Update Logo

1. Replace `/public/images/logo.svg` with your logo
2. Commit and push
3. Vercel deploys automatically

### Update Colors/Fonts

1. Edit `app/globals.css` CSS variables
2. Or edit `tailwind.config.ts`
3. Commit and push
4. Vercel deploys automatically

---

## Troubleshooting

### Site shows "Not Found"
- Wait for DNS to propagate (up to 48 hours)
- Check nameservers in domain registrar match Vercel

### Products don't load
- Check Notion API key is in Vercel environment variables
- Verify database IDs are correct
- Check Notion integration has database access

### Build fails
- Check for error messages in Vercel dashboard logs
- Ensure all environment variables are set
- Try `npm run build` locally to debug

### Site is slow
- Check Notion API isn't rate-limited
- Optimize images in Notion
- Check browser Network tab for slow requests

---

## Need Help?

### Resources
- Vercel Docs: https://vercel.com/docs
- Next.js Docs: https://nextjs.org/docs
- Notion API: https://developers.notion.com

### Common Issues
- **Can't push to GitHub?** - Check you're using correct GitHub username and have git installed
- **Vercel build fails?** - Check Environment Variables are exactly right (copy/paste, no typos)
- **Domain not working?** - DNS can take up to 48 hours; be patient!

---

## Summary

**You now have:**
- ✅ A modern, fully-functional website
- ✅ Deployed to Vercel (free, fast, secure)
- ✅ Connected to your custom domain
- ✅ Auto-updating from your Notion database
- ✅ Professional branding with custom fonts & colors
- ✅ Mobile-responsive design
- ✅ Dark mode support

**To update your site:**
1. **Content**: Edit in Notion, changes appear automatically
2. **Code**: Push to GitHub, Vercel auto-deploys
3. **Design**: Edit CSS in code, push to GitHub

**Your site is now live and ready to showcase vegan motorcycle gear to the world!** 🏍️💚
