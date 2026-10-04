import type { Metadata } from "next";
import "./globals.css";
import { Sidebar } from "@/components/Sidebar";

export const metadata: Metadata = {
  title: "Crab News — News Analytics & Trend Intelligence",
  description: "News crawling, Indonesian text processing, keyword analysis, and trend dashboard.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="id" className="dark">
      <body className="bg-slate-950 text-slate-100 flex min-h-screen antialiased selection:bg-rose-500 selection:text-white">
        <Sidebar />
        <main className="flex-1 flex flex-col min-w-0 overflow-y-auto bg-slate-950">
          {children}
        </main>
      </body>
    </html>
  );
}
