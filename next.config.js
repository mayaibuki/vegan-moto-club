// Static export for Cloudflare Pages: `next build` writes plain HTML, CSS, JS and
// images to out/. Nothing runs per visitor, so there is no server CPU to run out
// of. Data comes from the Notion snapshot (scripts/notion-snapshot.mjs) and is
// refreshed by rebuilding (.github/workflows/deploy-cloudflare.yml).
//
// Redirects for removed products are written to out/_redirects by
// scripts/write-cloudflare-files.mjs, since a static export cannot redirect.

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'export',
  images: {
    // Photos are pre-resized at build time; there is no image optimizer on a static host.
    unoptimized: true,
  },
}

module.exports = nextConfig
