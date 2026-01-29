import { redirect } from "next/navigation";
import { getSignInUrl, withAuth } from "@workos-inc/authkit-nextjs";

export default async function LoginPage() {
  const { user } = await withAuth();

  if (user) {
    redirect("/dashboard");
  }

  const signInUrl = await getSignInUrl();
  redirect(signInUrl);
}
