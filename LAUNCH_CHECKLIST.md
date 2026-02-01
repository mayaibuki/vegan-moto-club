# Launch Checklist - Vegan Moto Club

Use this checklist to ensure everything is ready before going live!

## Pre-Launch Checklist

### ✅ Local Testing
- [ ] Run `npm install` successfully
- [ ] Run `npm run dev` and site loads at http://localhost:3000
- [ ] Homepage displays with logo and hero section
- [ ] Products page loads and shows all products
- [ ] Product filters work (Brand, Category, Gender, Riding Style)
- [ ] Product search works
- [ ] Dark mode toggle works
- [ ] All navigation links work
- [ ] Events page displays events
- [ ] Blog page displays blog posts
- [ ] About page loads
- [ ] Mobile view is responsive (test on small screen)
- [ ] Product detail pages load correctly
- [ ] All images load without errors
- [ ] Forms and embedded content work

### ✅ Notion Setup
- [ ] Notion API integration created
- [ ] Products database connected
- [ ] Events database connected
- [ ] Blog database connected
- [ ] At least 1 product added to Notion
- [ ] At least 1 event added to Notion
- [ ] At least 1 blog post added to Notion

### ✅ Environment Variables
- [ ] `.env.local` file exists
- [ ] `NEXT_PUBLIC_NOTION_API_KEY` is correct
- [ ] `NOTION_PRODUCTS_DB_ID` is correct
- [ ] `NOTION_EVENTS_DB_ID` is correct
- [ ] `NOTION_BLOG_DB_ID` is correct
- [ ] No typos in any values

### ✅ GitHub Setup (if using GitHub)
- [ ] GitHub account created
- [ ] Repository created (`vegan-moto-club`)
- [ ] Repository is set to Public
- [ ] Local repo initialized with `git init`
- [ ] All files added with `git add .`
- [ ] Initial commit created
- [ ] Remote added: `git remote add origin https://...`
- [ ] Code pushed to GitHub with `git push -u origin main`

### ✅ Vercel Setup
- [ ] Vercel account created (free tier)
- [ ] Project imported from GitHub OR ready to deploy
- [ ] Environment variables added to Vercel dashboard:
  - [ ] `NEXT_PUBLIC_NOTION_API_KEY`
  - [ ] `NOTION_PRODUCTS_DB_ID`
  - [ ] `NOTION_EVENTS_DB_ID`
  - [ ] `NOTION_BLOG_DB_ID`
- [ ] Deployment completed successfully
- [ ] Site accessible at vercel domain (vegan-moto-club.vercel.app)

### ✅ Domain Configuration
- [ ] Domain registered at registrar (GoDaddy, Namecheap, etc.)
- [ ] Domain nameservers updated to Vercel (or DNS records added)
- [ ] Vercel domain settings configured for `veganmotoclub.com`
- [ ] DNS propagation checked (can take up to 48 hours)
- [ ] HTTPS certificate issued automatically by Vercel
- [ ] Site accessible at `veganmotoclub.com` (once DNS propagates)

### ✅ Content Verification
- [ ] Logo updated (replace `/public/images/logo.svg` with your actual logo)
- [ ] Product information complete in Notion
- [ ] Event information complete in Notion
- [ ] Blog posts formatted correctly in Notion
- [ ] All product images display correctly
- [ ] Price formatting is correct
- [ ] All links point to correct URLs

### ✅ Performance & Security
- [ ] Build completes without errors: `npm run build`
- [ ] No console errors or warnings
- [ ] All sensitive data in `.env.local` (not in code)
- [ ] `.gitignore` prevents `.env.local` from being committed
- [ ] HTTPS enabled on live domain
- [ ] No broken images or 404 errors
- [ ] Page loads quickly (under 3 seconds)

### ✅ Feature Testing
- [ ] Search functionality works on products page
- [ ] Filters apply correctly
- [ ] Product detail pages show all specs
- [ ] Staff favorite badge shows for marked products
- [ ] Season icons display correctly (☀️ 🌦 ❄️)
- [ ] Product suggestion form embeds correctly
- [ ] Dark mode colors look correct
- [ ] Light mode colors look correct

### ✅ Mobile Testing
- [ ] Layout responsive on iPhone (375px)
- [ ] Layout responsive on tablet (768px)
- [ ] Layout responsive on desktop (1920px)
- [ ] Touch-friendly buttons and links
- [ ] Hamburger menu works if needed
- [ ] All text readable on mobile
- [ ] Images load properly on mobile

### ✅ Accessibility
- [ ] All images have alt text
- [ ] Color contrast is sufficient
- [ ] Links are clearly distinguishable
- [ ] Form labels are clear
- [ ] Focus states visible for keyboard navigation

---

## Launch Day Checklist

### Before Going Live
- [ ] Final review of homepage
- [ ] Final review of products
- [ ] Final review of events
- [ ] Final review of blog
- [ ] Final review of about page
- [ ] Test on real iPhone/Android devices
- [ ] Test on slow internet connection (throttle in dev tools)

### Announcement
- [ ] Update Discord/Slack with new site link
- [ ] Post on Instagram about new website
- [ ] Update email signature with site link
- [ ] Share on social media
- [ ] Add to your bio/about sections

### Monitoring
- [ ] Check Vercel dashboard for any errors
- [ ] Monitor site traffic and errors
- [ ] Respond to user feedback
- [ ] Fix any reported issues quickly

---

## Post-Launch

### Week 1
- [ ] Monitor for bugs and issues
- [ ] Gather user feedback
- [ ] Test all filtering combinations
- [ ] Verify Notion updates sync correctly
- [ ] Check analytics if you add tracking

### Ongoing
- [ ] Update products in Notion regularly
- [ ] Add new events as they're planned
- [ ] Write new blog posts
- [ ] Monitor site performance
- [ ] Keep dependencies updated

---

## Quick Troubleshooting During Launch

### If site doesn't load:
1. Check Vercel deployment status
2. Verify environment variables are set
3. Check DNS propagation (may take 48 hours)
4. Try accessing `.vercel.app` subdomain instead

### If Notion data doesn't show:
1. Verify API key is correct
2. Verify database IDs are correct
3. Check Notion integration has database access
4. Restart dev server / redeploy

### If styles look wrong:
1. Hard refresh browser (Ctrl+Shift+R or Cmd+Shift+R)
2. Clear browser cache
3. Check CSS variables in `app/globals.css`
4. Check tailwind build completed successfully

### If dark mode doesn't work:
1. Check browser localStorage is enabled
2. Check theme toggle button was clicked
3. Verify CSS variables for `.dark` class exist

---

## Support Resources

If you get stuck:
1. **Quick help**: See `QUICKSTART.md`
2. **Detailed steps**: See `DEPLOYMENT.md`
3. **Full docs**: See `README.md`
4. **What was built**: See `PROJECT_SUMMARY.md`
5. **Troubleshooting**: See `DEPLOYMENT.md` → Troubleshooting

---

## Key Commands You Might Need

```bash
# Development
npm run dev              # Start dev server
npm run build            # Build for production
npm start                # Start production server

# Git
git add .                # Stage all changes
git commit -m "message"  # Commit changes
git push origin main     # Push to GitHub

# Vercel
vercel                   # Deploy with CLI
vercel --prod           # Deploy to production
```

---

## Final Checklist Before Clicking "Go Live"

- [ ] Have I tested everything locally?
- [ ] Have I pushed code to GitHub?
- [ ] Have I deployed to Vercel?
- [ ] Have I configured the domain?
- [ ] Have I waited for DNS to propagate?
- [ ] Can I access the site at veganmotoclub.com?
- [ ] Do products load from Notion?
- [ ] Does dark mode work?
- [ ] Is the logo displaying?
- [ ] Are colors correct?
- [ ] Are fonts loading?
- [ ] Does it look good on mobile?
- [ ] Is everything I want on the homepage visible?

---

## You're Ready to Launch! 🚀

Once you've checked all the boxes above, your website is ready for the world to see.

**Go live and share your vegan motorcycle gear database with the community!** 🏍️💚

---

**Questions during launch?** Refer to the guides or check the code comments.

Good luck! 🎉
