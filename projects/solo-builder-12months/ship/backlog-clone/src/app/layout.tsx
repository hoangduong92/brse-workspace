import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Backlog Clone",
  description: "A project management tool inspired by Backlog",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
