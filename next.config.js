// Old URLs of products removed from the catalog (see scripts/build-removed-products.mjs).
const removedProducts = require('./lib/removed-products.json')

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async redirects() {
    return Object.entries(removedProducts).map(([slug, destination]) => ({
      source: `/products/${slug}`,
      destination,
      permanent: true,
    }))
  },
  experimental: {
    serverComponentsExternalPackages: ['sharp'],
  },
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**',
      },
    ],
    formats: ['image/webp'],
    minimumCacheTTL: 2678400,
    deviceSizes: [640, 1200],
    imageSizes: [96, 256],
  },
}

module.exports = nextConfig
