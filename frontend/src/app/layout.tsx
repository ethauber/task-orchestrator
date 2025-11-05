import type { Metadata } from "next";
import Link from "next/link";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Task Orchestrator",
  description: "LLM-powered task orchestration",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body style={{ fontFamily: 'system-ui, sans-serif' }}>
        <header style={{ padding: 12, borderBottom: '1px solid #333' }}>
          <nav style={{ display: 'flex', gap: 16 }}>
            <Link href='/'>Home</Link>
            <Link href='/health'>Health</Link>
            <Link href='/breakdown'>Breakdown</Link>
          </nav>
        </header>
        <main style={{ padding: 24 }}>{children}</main>
      </body>
    </html>
  );
}
