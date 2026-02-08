import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "TaskPilot",
  description: "AI-powered task automation across your apps",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
