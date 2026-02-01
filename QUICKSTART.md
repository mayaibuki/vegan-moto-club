# Quick Start Guide - Vegan Moto Club

Get your website live in 5 minutes! 🚀

## What You Have

✅ Complete website code
✅ Connected to your Notion databases
✅ Professional branding (fonts, colors, logo)
✅ Mobile responsive design
✅ Dark mode support

## Your 3 Deployment Options

### Option 1: Vercel + GitHub (Recommended - 5 min)

**Best for**: Easy updates, automatic deployments

```bash
# 1. Create GitHub repo at github.com/new
# 2. Push code
cd /Users/mayaibuki/Documents/Claude/vegan-moto-club
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/vegan-moto-club
git push -u origin main

# 3. Deploy at vercel.com
# - Click "Add New Project"
# - Import your GitHub repo
# - Add environment variables (see below)
# - Click Deploy!

# 4. Connect domain at vercel.com/domains
# - Add veganmotoclub.com
# - Update DNS nameservers
# - Done!
```

**Environment Variables to add in Vercel:**
```
NEXT_PUBLIC_NOTION_API_KEY=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
NOTION_PRODUCTS_DB_ID=e6d109a83834445b8ca042e430c511f8
NOTION_EVENTS_DB_ID=veganmotoclub/Events-3f9543148b934f689907fdcdecf90a44
NOTION_BLOG_DB_ID=veganmotoclub/22d439de397b80039676fd22f633a2cf
```

---

### Option 2: Vercel CLI (10 min)

**Best for**: Quick deploy without GitHub

```bash
# 1. Install Vercel
npm i -g vercel

# 2. Deploy
cd /Users/mayaibuki/Documents/Claude/vegan-moto-club
vercel

# 3. Follow prompts to add environment variables
# 4. Done! Site deployed
```

---

### Option 3: Netlify (10 min)

**Best for**: Alternative to Vercel

```bash
# 1. Go to netlify.com and sign up
# 2. Click "Add new site" → "Deploy manually"
# 3. Drag & drop your folder
# 4. Or connect GitHub for auto-deployment
# 5. Add environment variables in Netlify dashboard
# 6. Connect domain
```

---

## After Deployment

### To Update Your Site:

**Content Updates** (Products, Events, Blog):
1. Edit in Notion
2. Refresh website (changes appear in 5-10 seconds)

**Code Updates** (Design, Layout, Features):
1. Edit code locally
2. Test with `npm run dev`
3. Push to GitHub: `git add . && git commit -m "changes" && git push`
4. Vercel auto-deploys automatically

**Logo Update**:
1. Replace `/public/images/logo.svg` with your actual logo
2. `git add . && git commit -m "Update logo" && git push`
3. Done!

---

## Before You Deploy

### ✅ Quick Checklist

- [ ] Test locally: `npm install && npm run dev`
- [ ] Check that products load from Notion
- [ ] Verify filters work
- [ ] Test dark mode toggle
- [ ] Check mobile view (responsive)
- [ ] All links work (Products, Events, Blog, About)

### ✅ Have Ready

- [ ] GitHub account (for Option 1 & 2)
- [ ] Vercel account (free, takes 1 min)
- [ ] Your domain registrar login (GoDaddy, Namecheap, etc.)
- [ ] Notion API credentials (already configured!)

---

## Stuck? Use These Guides

- **Full deployment guide**: `DEPLOYMENT.md`
- **Full README**: `README.md`
- **Troubleshooting**: See DEPLOYMENT.md → Troubleshooting section

---

## Next Steps

1. **Test Locally** (2 min)
   ```bash
   cd /Users/mayaibuki/Documents/Claude/vegan-moto-club
   npm install
   npm run dev
   # Visit http://localhost:3000
   ```

2. **Deploy** (5 min with Option 1 or 2)

3. **Connect Domain** (5 min)
   - Or use Vercel's free subdomain: `vegan-moto-club.vercel.app`

4. **Celebrate** 🎉
   - Your website is LIVE!
   - Share with your community!

---

## Support

If something doesn't work:

1. **Build fails?** → Check environment variables in Vercel
2. **Products don't load?** → Verify Notion API key is correct
3. **Domain not working?** → Wait 24-48 hours for DNS propagation
4. **Styles look wrong?** → Hard refresh browser (Ctrl+Shift+R)

See `DEPLOYMENT.md` for detailed troubleshooting.

---

**You're all set! Your website is production-ready.** 🏍️✨

Questions? Check the guides above or the README.md file.
