/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  poweredByHeader: false,
  env: {
    NEXT_PUBLIC_DEMO_MODE: process.env.NEXT_PUBLIC_DEMO_MODE ?? "true",
    NEXT_PUBLIC_WORKOS_CLIENT_ID:
      process.env.NEXT_PUBLIC_WORKOS_CLIENT_ID ?? "demo_workos_client_id",
    NEXT_PUBLIC_WORKOS_ORGANIZATION_ID:
      process.env.NEXT_PUBLIC_WORKOS_ORGANIZATION_ID ?? "demo_org_001"
  }
};

module.exports = nextConfig;
