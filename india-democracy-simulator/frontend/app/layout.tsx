import type { Metadata } from "next";
import { Inter, Outfit, Space_Grotesk } from "next/font/google";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

const outfit = Outfit({
  variable: "--font-outfit",
  subsets: ["latin"],
});

const spaceGrotesk = Space_Grotesk({
  variable: "--font-space",
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
      className={`${inter.variable} ${outfit.variable} ${spaceGrotesk.variable} h-full antialiased dark`}
    >
      <body className="min-h-full flex flex-col bg-[#06080F] text-white font-[family-name:var(--font-inter)]">
        {/* Animated mesh gradient background */}
        <div className="mesh-bg" />
        {/* Page content */}
        <div className="relative z-10 flex-1 flex flex-col">
          {children}
        </div>
      </body>
    </html>
  );
}
