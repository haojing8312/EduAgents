import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "PBL智能助手",
  description: "AI原生多智能体PBL课程设计助手系统",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
