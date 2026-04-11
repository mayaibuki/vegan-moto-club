/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**',
      },
    ],
    formats: ['image/webp'],
    minimumCacheTTL: 2678400,
    deviceSizes: [640, 1080, 1920],
    imageSizes: [16, 32, 48, 64, 96, 256],
  },
}

module.exports = nextConfig
