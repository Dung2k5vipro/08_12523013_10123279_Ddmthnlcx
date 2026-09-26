import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Dự đoán mức tiêu hao nhiên liệu xe',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="vi">
      <body>{children}</body>
    </html>
  );
}