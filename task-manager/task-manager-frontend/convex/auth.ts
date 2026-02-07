import { DEMO_MODE, WORKOS_PLACEHOLDER_CONFIG } from "@/lib/config";
import { demoUser } from "@/lib/demo-data";
import { AuthState } from "@/types";

export async function getAuthContext(): Promise<AuthState> {
  return {
    mode: DEMO_MODE ? "demo" : "workos",
    isAuthenticated: true,
    workosClientId: WORKOS_PLACEHOLDER_CONFIG.clientId,
    user: demoUser
  };
}
