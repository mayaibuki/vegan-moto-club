# Vegan Moto Club - Website

A modern, fully-functional website for Vegan Moto Club that displays cruelty-free motorcycle gear from a Notion database.

## Features

✅ **Product Showcase**: Display vegan motorcycle gear with advanced filtering
- Filter by: Brand, Category, Gender, Riding Style
- Search by product name
- Product detail pages with full specifications

✅ **Events Management**: Display upcoming events from Notion
- Event dates, location, and registration links
- Automatic sorting by date

✅ **Blog Integration**: Blog posts pulled directly from Notion
- Featured images support
- Responsive design

✅ **Design & Branding**
- Custom typography (Petrona, Zalando Expanded, Havana Script)
- Brand colors: Red primary, warm grey neutrals, lime green accents
- Dark mode support
- Fully responsive (mobile, tablet, desktop)

✅ **Auto-updating**: All content automatically syncs from Notion
- Change a product price in Notion → Website updates in seconds
- No manual code changes needed

## Tech Stack

- **Framework**: Next.js 14 + React 18
- **Styling**: Tailwind CSS + shadcn/ui components
- **Data**: Notion API
- **Deployment**: Vercel
- **Typography**: Petrona (body), Zalando Expanded (headings), Havana Script (display)

## Getting Started

### Prerequisites

- Node.js 18+ and npm/yarn
- Notion workspace with API access

### Setup

1. **Clone the repository**
```bash
cd vegan-moto-club
npm install
```

2. **Configure Notion API**
   - Copy `.env.example` to `.env.local`
   - Add your Notion API credentials:
```bash
NEXT_PUBLIC_NOTION_API_KEY=your_key_here
NOTION_PRODUCTS_DB_ID=your_db_id
NOTION_EVENTS_DB_ID=your_db_id
NOTION_BLOG_DB_ID=your_db_id
```

3. **Run locally**
```bash
npm run dev
```
Visit `http://localhost:3000`

4. **Build for production**
```bash
npm run build
npm start
```

## Deployment to Vercel

### Option 1: Using Vercel CLI (Recommended)

1. **Install Vercel CLI**
```bash
npm i -g vercel
```

2. **Deploy**
```bash
vercel
```

3. **Add Environment Variables**
   - During deployment, Vercel will ask for environment variables
   - Add your Notion API credentials
   - Or add them in Vercel dashboard: Settings → Environment Variables

### Option 2: Using GitHub

1. **Push to GitHub**
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/vegan-moto-club
git push -u origin main
```

2. **Connect to Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Import your GitHub repository
   - Add environment variables
   - Deploy!

### Option 3: Manual Deployment

1. Build your project locally
2. Deploy the `.next` folder to any Node.js hosting (AWS, Netlify, etc.)
3. Set environment variables in your hosting provider's dashboard

## Connecting Your Domain

1. **In Vercel Dashboard**
   - Go to your project settings
   - Click "Domains"
   - Add your domain: `veganmotoclub.com`
   - Follow the DNS setup instructions

2. **Update DNS Records**
   - Point your domain's DNS to Vercel's nameservers
   - Wait for propagation (5-48 hours)

## Customization

### Change Colors
Edit `app/globals.css` CSS variables:
```css
--secondary: 30 8% 65%;       /* Warm grey */
--accent: 81 100% 65%;        /* Lime green */
```

### Change Fonts
Edit `tailwind.config.ts` font families or import different fonts in `app/globals.css`

### Update Logo
Replace `/public/images/logo.svg` with your actual logo

### Add More Pages
Create new routes in `app/` directory following Next.js conventions

## Environment Variables

| Variable | Description |
|----------|-------------|
| `NEXT_PUBLIC_NOTION_API_KEY` | Your Notion API key from integrations |
| `NOTION_PRODUCTS_DB_ID` | Notion Products database ID |
| `NOTION_EVENTS_DB_ID` | Notion Events database ID |
| `NOTION_BLOG_DB_ID` | Notion Blog database ID |

## Project Structure

```
vegan-moto-club/
├── app/                    # Next.js pages & layouts
│   ├── page.tsx           # Home page
│   ├── products/          # Products pages
│   ├── events/            # Events pages
│   ├── blog/              # Blog pages
│   ├── about/             # About page
│   └── layout.tsx         # Root layout
├── components/            # React components
│   ├── ui/               # shadcn/ui components
│   ├── Logo.tsx
│   ├── Navbar.tsx
│   ├── Footer.tsx
│   ├── ProductCard.tsx
│   └── ProductGrid.tsx
├── lib/                   # Utility functions
│   ├── notion.ts         # Notion API integration
│   ├── types.ts          # TypeScript types
│   └── utils.ts          # Helper functions
├── public/               # Static assets
│   ├── images/           # Logo & images
│   └── fonts/            # Custom fonts
└── styles/              # Global styles
```

## Troubleshooting

### Products not loading?
- Check Notion API key in `.env.local`
- Verify database IDs are correct
- Make sure integration has access to databases

### Fonts not loading?
- Check `/public/fonts/` has the font files
- Verify font imports in `app/globals.css`
- Check browser console for 404 errors

### Images not displaying?
- Ensure Notion images are publicly accessible
- Check Next.js Image component optimization settings

## Support

For issues or questions:
1. Check Notion database is properly configured
2. Verify all environment variables are set
3. Run `npm run build` locally to catch build errors
4. Check Vercel deployment logs

## License

All rights reserved - Vegan Moto Club

## Updates

To update your website after making changes:
1. Edit content in Notion
2. Website automatically syncs (refresh browser)
3. For code changes, push to GitHub and Vercel auto-deploys
4. Or run `vercel --prod` to manually deploy
