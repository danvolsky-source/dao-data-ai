import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'DAO Data AI - Governance Analytics Platform',
  description: 'AI-powered governance analytics platform for DAOs. Predicts proposal outcomes using on-chain and off-chain data.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
