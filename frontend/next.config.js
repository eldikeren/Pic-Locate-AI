/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*',
      },
      {
        source: '/v4/:path*',
        destination: 'http://localhost:8000/v4/:path*',
      },
      {
        source: '/indexing/:path*',
        destination: 'http://localhost:8000/indexing/:path*',
      },
      {
        source: '/stats/:path*',
        destination: 'http://localhost:8000/stats/:path*',
      },
      {
        source: '/health',
        destination: 'http://localhost:8000/health',
      },
      {
        source: '/docs',
        destination: 'http://localhost:8000/docs',
      }
    ]
  },
  env: {
    API_BASE: process.env.API_BASE || 'http://localhost:8000',
  }
}

module.exports = nextConfig