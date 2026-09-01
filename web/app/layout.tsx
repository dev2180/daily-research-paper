import type { Metadata } from "next";
import { Archivo } from "next/font/google";
import "./globals.css";

const archivo = Archivo({
  subsets: ["latin"],
  axes: ["wdth"],
  display: "swap",
  variable: "--font-archivo",
});

export const metadata: Metadata = {
  title: "Daily Research Paper",
  description:
    "A ranked board of the AI/ML research worth your attention — papers, code gaps, and community signal, rebuilt every morning.",
  openGraph: {
    title: "Daily Research Paper",
    description: "A ranked board of the AI/ML research worth your attention.",
    type: "website",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={archivo.variable}>
      <body className="min-h-screen antialiased">{children}</body>
    </html>
  );
}
