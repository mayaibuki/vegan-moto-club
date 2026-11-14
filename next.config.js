// Old URLs of products removed from the catalog (see scripts/build-removed-products.mjs).
const removedProducts = require('./lib/removed-products.json')

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async redirects() {
    const removed = Object.entries(removedProducts).map(([slug, destination]) => ({
      source: `/products/${slug}`,
      destination,
      permanent: true,
    }))
    // "Street wear" was retired on 2026-11-14. Most of its products are now Jackets.
    return [
      {
        source: '/vegan-motorcycle-street-wear',
        destination: '/vegan-motorcycle-jackets',
        permanent: true,
      },
      {
        source: '/products',
        has: [{ type: 'query', key: 'category', value: 'Street wear' }],
        destination: '/products?category=Jackets',
        permanent: true,
      },
      ...removed,
    ]
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
