"use client";

import { AuthKitProvider as WorkOSAuthKitProvider } from "@workos-inc/authkit-nextjs/components";
import { ReactNode } from "react";

export function AuthKitProvider({ children }: { children: ReactNode }) {
  return <WorkOSAuthKitProvider>{children}</WorkOSAuthKitProvider>;
}
