import type { Metadata } from "next";
import { Inter, Outfit } from "next/font/google";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

const outfit = Outfit({
  variable: "--font-outfit",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "India Democracy Simulator — Experience Lok Sabha Elections",
  description:
    "An AI-powered civic education game where you experience the Indian General Elections from the inside. 543 seats, real 2024 data, and your decisions shape the outcome.",
  keywords: ["India", "democracy", "simulator", "elections", "Lok Sabha", "civics"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${inter.variable} ${outfit.variable} h-full antialiased dark`}
    >
      <body className="min-h-full flex flex-col bg-[#0a0a12] text-white font-[family-name:var(--font-inter)]">
        {children}
      </body>
    </html>
  );
}
