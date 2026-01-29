import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Backlog UI Pro",
  description: "Project management and issue tracking",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}
