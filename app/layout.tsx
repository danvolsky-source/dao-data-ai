import type { Metadata } from 'next';
import './globals.css';
import Header from './components/Header';
import Footer from './components/Footer';
import { ThemeProvider } from './components/ThemeProvider';

export const metadata: Metadata = {
  title: 'DAO Data AI - Governance Analytics Platform',
  description: 'AI-powered governance analytics platform for DAOs. Predicts proposal outcomes using on-chain and off-chain data.',
  keywords: ['DAO', 'governance', 'analytics', 'AI', 'blockchain', 'voting', 'proposals'],
  openGraph: {
    title: 'DAO Data AI - Governance Analytics Platform',
    description: 'AI-powered governance analytics platform for DAOs',
    type: 'website',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="flex flex-col min-h-screen">
        <ThemeProvider>
          <Header />
          <main className="flex-grow">
            {children}
          </main>
          <Footer />
        </ThemeProvider>
      </body>
    </html>
  );
}
