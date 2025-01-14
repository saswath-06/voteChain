/** @type {import('next').NextConfig} */
const nextConfig = {
    reactStrictMode: true,
    images: {
      domains: ['ipfs.io'], // Allow IPFS image loading
    },
    webpack: (config) => {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        net: false,
        tls: false,
        fs: false,
      };
      return config;
    },
  };
  
  module.exports = nextConfig;