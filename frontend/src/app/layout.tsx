import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "NarrativeAI — AI-Native News Intelligence",
  description:
    "Transform business news from disconnected articles into living intelligence dossiers with Story DNA, Fog of War, and persistent narrative memory.",
  manifest: "/manifest.json",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen antialiased">{children}</body>
    </html>
  );
}
