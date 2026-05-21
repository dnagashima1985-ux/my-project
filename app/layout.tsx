import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

const APP_URL = process.env.NEXT_PUBLIC_APP_URL ?? 'https://scoutiq.app';

export const metadata: Metadata = {
  title: { default: 'ScoutIQ — Professional Football Scouting', template: '%s | ScoutIQ' },
  description: 'The only scouting tool built for professional scouts — not bettors, not clubs. AI-powered longlists, percentiles, EQ analysis, injury intelligence.',
  keywords: ['football scouting', 'soccer scout', 'player analysis', 'longlist', 'transfer intelligence', 'xG', 'scouting software'],
  metadataBase: new URL(APP_URL),
  openGraph: {
    type: 'website',
    siteName: 'ScoutIQ',
    title: 'ScoutIQ — Professional Football Scouting Intelligence',
    description: 'Reduce longlist creation from 8–15 hours to 1–2 hours. AI-powered. 20 play style profiles. League-relative percentiles.',
    url: APP_URL,
  },
  twitter: {
    card: 'summary_large_image',
    title: 'ScoutIQ — Professional Football Scouting Intelligence',
    description: 'Reduce longlist creation from 8–15 hours to 1–2 hours. 7 longlists free — no credit card.',
  },
  alternates: {
    canonical: APP_URL,
    languages: { 'en': APP_URL, 'ja': `${APP_URL}/ja` },
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={inter.className}>
      <body className="min-h-screen bg-gray-950 text-gray-100">{children}</body>
    </html>
  );
}
