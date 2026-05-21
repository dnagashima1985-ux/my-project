import type { MetadataRoute } from 'next';

export default function robots(): MetadataRoute.Robots {
  const base = process.env.NEXT_PUBLIC_APP_URL ?? 'https://scoutiq.app';
  return {
    rules: [
      { userAgent: '*', allow: '/', disallow: ['/api/', '/dashboard', '/longlist', '/players', '/reports', '/shortlist', '/settings', '/market-intelligence'] },
    ],
    sitemap: `${base}/sitemap.xml`,
  };
}
