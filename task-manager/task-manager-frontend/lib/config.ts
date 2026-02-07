export const DEMO_MODE = process.env.NEXT_PUBLIC_DEMO_MODE !== "false";

export const WORKOS_PLACEHOLDER_CONFIG = {
  clientId:
    process.env.NEXT_PUBLIC_WORKOS_CLIENT_ID ?? process.env.WORKOS_CLIENT_ID ?? "demo_workos_client_id",
  organizationId: process.env.NEXT_PUBLIC_WORKOS_ORGANIZATION_ID ?? "demo_org_001",
  apiKey: process.env.WORKOS_API_KEY ?? "demo_workos_api_key",
  redirectUri: process.env.WORKOS_REDIRECT_URI ?? "http://localhost:3000/auth/callback"
};
