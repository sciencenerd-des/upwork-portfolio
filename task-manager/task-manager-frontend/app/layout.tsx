import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { AuthKitProvider } from "@/providers/AuthKitProvider";
import { ConvexProvider } from "@/providers/ConvexProvider";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "TaskFlow - Project & Task Management",
  description:
    "A modern task management application with Kanban boards and project organization",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <AuthKitProvider>
          <ConvexProvider>{children}</ConvexProvider>
        </AuthKitProvider>
      </body>
    </html>
  );
}
