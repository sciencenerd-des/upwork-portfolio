import { getAuthContext } from "@/convex/auth";
import { AuthState, UserProfile } from "@/types";

export async function getAuthState(): Promise<AuthState> {
  return getAuthContext();
}

export async function getCurrentUser(): Promise<UserProfile> {
  const authState = await getAuthState();
  return authState.user;
}
