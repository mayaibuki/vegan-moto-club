/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    // Allow all HTTPS image hosts since product images in Notion
    // come from various external sources (retailer CDNs, brand sites, etc.)
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**',
      },
    ],
    // Optimize image formats
    formats: ['image/avif', 'image/webp'],
  },
}

module.exports = nextConfig
