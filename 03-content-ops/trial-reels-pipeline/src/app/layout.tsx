import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Trial Reels Pipeline",
  description: "Hook & example pipeline for trial reels",
  robots: { index: false, follow: false },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
