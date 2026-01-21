import { redirect } from "next/navigation";
import { getSignUpUrl, withAuth } from "@workos-inc/authkit-nextjs";

export default async function RegisterPage() {
  const { user } = await withAuth();

  if (user) {
    redirect("/dashboard");
  }

  const signUpUrl = await getSignUpUrl();
  redirect(signUpUrl);
}
