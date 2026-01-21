"use client";

import { ConvexReactClient } from "convex/react";
import { ConvexProviderWithAuth } from "convex/react";
import { ReactNode, useCallback, useMemo } from "react";
import { useAuth } from "@workos-inc/authkit-nextjs/components";

const convex = new ConvexReactClient(
  process.env.NEXT_PUBLIC_CONVEX_URL as string
);

function useAuthFromWorkOS() {
  const { user, loading } = useAuth();

  const fetchAccessToken = useCallback(async () => {
    // WorkOS handles tokens internally, we return a placeholder
    // The actual auth is handled by WorkOS middleware
    if (user) {
      return "authenticated";
    }
    return null;
  }, [user]);

  return useMemo(
    () => ({
      isLoading: loading,
      isAuthenticated: !!user,
      fetchAccessToken,
    }),
    [loading, user, fetchAccessToken]
  );
}

export function ConvexProvider({ children }: { children: ReactNode }) {
  return (
    <ConvexProviderWithAuth client={convex} useAuth={useAuthFromWorkOS}>
      {children}
    </ConvexProviderWithAuth>
  );
}
