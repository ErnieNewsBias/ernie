import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'standalone',
  images: {
    domains: ['cdn.discordapp.com']
  }
};

export default nextConfig;
