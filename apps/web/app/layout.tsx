import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Daily Job Hub",
  description: "AI-powered internship and new grad platform",
  metadataBase: new URL("https://dailyjobhub.example.com")
};

export default function RootLayout({
  children
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-slate-950 text-slate-100 antialiased">
        <main>{children}</main>
      </body>
    </html>
  );
}
